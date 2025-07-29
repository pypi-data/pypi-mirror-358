#!/usr/bin/python

"""test.thing - A simple modern VM runner.

A simple VM runner script exposing an API useful for use as a pytest fixture.
Can also be used to run a VM and login via the console.

Each VM is allocated an identifier: 'tt.0', 'tt.1', etc.

For each VM, an ephemeral ssh key is created and used to connect to the VM via
vsock with systemd-ssh-proxy, which works even if the guest doesn't have
networking configured.  The ephemeral key means that access is limited to the
current user (since vsock connections are otherwise available to all users on
the host system).  The guest needs to have systemd 256 for this to work.

An ssh control socket is created for sending commands and can also be used
externally, avoiding the need to authenticate.  A suggested ssh config:

```
Host tt.*
        ControlPath ${XDG_RUNTIME_DIR}/test.thing/%h/ssh
```

And then you can say `ssh tt.0` or `scp file tt.0:/tmp`.
"""

import argparse
import asyncio
import contextlib
import ctypes
import json
import os
import shlex
import shutil
import signal
import socket
import sys
import traceback
import weakref
from collections.abc import AsyncGenerator, Callable, Mapping
from pathlib import Path


def _unique_id() -> tuple[int, int]:
    pid = os.getpid()
    pidfd = os.pidfd_open(pid)
    try:
        buf = os.fstat(pidfd)
        return (pid, buf.st_ino)
    finally:
        os.close(pidfd)


# This is basically tempfile.TemporaryDirectory but sequentially-allocated.
# We do that so we can easily interact with the VMs from outside (with ssh).
class _IpcDir:
    finalizer: Callable[[], None] | None = None

    def __enter__(self) -> Path:
        tt_dir = Path(os.environ["XDG_RUNTIME_DIR"]) / "test.thing"
        for n in range(10000):
            tmpdir = tt_dir / f"tt.{n}"

            try:
                tmpdir.mkdir(exist_ok=False, parents=True, mode=0o700)
            except FileExistsError:
                continue

            self.finalizer = weakref.finalize(self, shutil.rmtree, tmpdir)
            (tmpdir / "pid").write_text(f"{_unique_id()}\n")
            return tmpdir

        raise FileExistsError

    def __exit__(self, *args: object) -> None:
        del args
        if self.finalizer:
            self.finalizer()


def _vsock_listen(family: socket.SocketKind) -> tuple[socket.socket, int]:
    """Bind a vsock to a free port number and start listening on it.

    Returns the socket and the chosen port number.
    """
    sock = socket.socket(socket.AF_VSOCK, family)
    sock.bind((-1, -1))
    sock.listen()
    _, port = sock.getsockname()
    return (sock, port)


async def _wait_stdin(msg: str) -> None:
    r"""Wait until stdin sees \n or EOF.

    This prints the given message to stdout without adding an extra newline.

    The input is consumed (and discarded) up to the \n and maybe more...
    """
    done = asyncio.Event()

    def stdin_ready() -> None:
        data = os.read(0, 4096)
        if not data:
            print()
        if not data or b"\n" in data:
            done.set()

    loop = asyncio.get_running_loop()
    loop.add_reader(0, stdin_ready)
    sys.stdout.write(msg)
    sys.stdout.flush()
    try:
        await done.wait()
    finally:
        loop.remove_reader(0)


def _normalize_arg(arg: str | Path | tuple[str | Path, ...]) -> tuple[str, ...]:
    return tuple(map(str, arg)) if isinstance(arg, tuple) else (str(arg),)


def pretty_print_args(*args: str | Path | tuple[str | Path, ...]) -> str:
    """Pretty-print a nested argument list.

    This takes the argument list format used by test.thing and turns it into a
    format that looks like a nicer version of `set -x` from POSIX shell.
    """
    if any(isinstance(arg, tuple) for arg in args):
        # There are tuples: use the fancy format
        return "+ " + " \\\n      ".join(
            shlex.join(_normalize_arg(arg)) for arg in args if arg != ()
        )
    # Simple format
    return "+ " + shlex.join(map(str, args))


def flatten_args(*args: str | Path | tuple[str | Path, ...]) -> tuple[str, ...]:
    """Flatten a nested argument list.

    This takes the argument list format used by test.thing and turns it into a
    argv that you can use with the usual spawn APIs.

    If cmd is None then it's not added to the output.
    """
    return (*(arg for chunk in args for arg in _normalize_arg(chunk)),)


def join_args(*args: str | Path | tuple[str | Path, ...]) -> str:
    """Quote and join a nested argument list.

    This takes the argument list format used by test.thing and turns it into a
    quoted shell command using shlex.join().  This is suitable for use as a
    remote ssh command or with `sh -c`.
    """
    return shlex.join(flatten_args(*args))


async def _run(
    *args: str | Path | tuple[str | Path, ...],
    check: bool = True,
    stdin: int | None = None,
    stdout: int | None = None,
    verbose: bool = True,
) -> int:
    """Run a process, waiting for it to exit.

    This takes the same arguments as _spawn, plus a "check" argument (True by
    default) which works in the usual way.
    """
    process = await _spawn(*args, stdin=stdin, stdout=stdout, verbose=verbose)
    returncode = await process.wait()
    if check and returncode != 0:
        raise SubprocessError(args, returncode=returncode)
    return returncode


async def _spawn(
    *args: str | Path | tuple[str | Path, ...],
    stdin: int | None = None,
    stdout: int | None = None,
    verbose: bool = True,
) -> asyncio.subprocess.Process:
    """Spawn a process.

    This has a couple of extra niceties: the args list is flattened, Path is
    converted to str, the spawned process is logged to stderr for debugging,
    and we call PR_SET_PDEATHSIG with SIGTERM after forking to make sure the
    process exits with us.

    The flattening allows grouping logically-connected arguments together,
    producing nicer verbose output, allowing for adding groups of arguments
    from helper functions or comprehensions, and works nicely with code
    formatters:

    For example:

    private = Path(...)
    options = { ... }

    ssh = await _spawn(
        "ssh",
        ("-i", private),
        *(("-o", f"{k} {v}") for k, v in options.items()),
        ("-l", "root", "x"),
        ...
    )

    The type of the groups is `tuple`.  It could be `Sequence` but this would
    also allow using bare strings, which would be split into their individual
    characters.  Using `tuple` prevents this from happening.
    """
    # This might be complicated: do it before the fork
    prctl = ctypes.CDLL(None, use_errno=True).prctl

    def pr_set_pdeathsig() -> None:
        PR_SET_PDEATHSIG = 1  # noqa: N806
        if prctl(PR_SET_PDEATHSIG, signal.SIGTERM):
            os._exit(1)  # should never happen

    if verbose:
        print(pretty_print_args(*args))

    return await asyncio.subprocess.create_subprocess_exec(
        *flatten_args(*args),
        stdin=stdin,
        stdout=stdout,
        preexec_fn=pr_set_pdeathsig,
    )


async def _ssh_keygen(ipc: Path) -> tuple[Path, str]:
    """Create a ssh key in the given directory.

    Returns the path to the private key and the public key as a string.
    """
    private_key = ipc / "id"

    await _run(
        "ssh-keygen",
        "-q",  # quiet
        ("-t", "ed25519"),
        ("-N", ""),  # no passphrase
        ("-C", ""),  # no comment
        ("-f", f"{private_key}"),
        stdin=asyncio.subprocess.DEVNULL,
    )

    return private_key, (ipc / "id.pub").read_text().strip()


async def _notify_server(
    listener: socket.socket, callback: Callable[[str, str], None]
) -> None:
    """Listen on the socket for incoming sd-notify connections.

    `callback` is called with each notification.

    The socket is consumed and will be closed when the server exits (which
    happens via cancelling its task).
    """
    loop = asyncio.get_running_loop()

    async def handle_connection(conn: socket.socket) -> None:
        try:
            while data := await loop.sock_recv(conn, 65536):
                for line in data.decode().splitlines():
                    k, _, v = line.strip().partition("=")
                    callback(k, v)
        finally:
            conn.close()

    # AbstractEventLoop.sock_accept() expects a non-blocking socket
    listener.setblocking(False)  # noqa: FBT003

    try:
        while True:
            conn, _ = await loop.sock_accept(listener)
            asyncio.create_task(handle_connection(conn))  # noqa: RUF006
    finally:
        # If we have a listener but don't accept the connections then the
        # guest can deadlock.  Make sure we close it when we exit.
        listener.close()


def _find_ovmf() -> tuple[str, Path]:
    candidates = [
        # path for Fedora/RHEL (our tasks container)
        "/usr/share/OVMF/OVMF_CODE.fd",
        # path for Ubuntu (GitHub Actions runners)
        "/usr/share/ovmf/OVMF.fd",
        # path for Arch
        "/usr/share/edk2/x64/OVMF.4m.fd",
    ]

    for path in map(Path, candidates):
        if path.exists():
            return "-bios", path

    raise FileNotFoundError("Unable to find OVMF UEFI BIOS")  # noqa: EM101


async def _run_qemu(
    *,
    attach_console: bool,
    cpus: int,
    image: Path | str,
    ipc: Path,
    memory: int | str,
    port: int,
    public: str,
    snapshot: bool,
) -> asyncio.subprocess.Process:
    # Console setup:
    #
    #  - attach_console = 0 means nothing goes on stdio
    #  - attach_console = 1 means that a getty starts on stdio
    #  - attach_console = 2 means that console= goes also to stdio
    #
    # In the cases that the console isn't directed to stdio (ie: 0, 1) then we
    # write it to a log file instead.  Unfortunately, we also get a getty in
    # our log file: https://github.com/systemd/systemd/issues/37928
    #
    # We also get our screen cleared unnecessarily in '-a' mode:
    # https://github.com/tianocore/edk2/issues/11218
    #
    # We always use hvc0 for the console=.  We use it also for the getty in
    # mode 2.  In mode 1 we create a separate hvc1 and use that.

    creds = {
        "vmm.notify_socket": f"vsock:2:{port}",
        "ssh.ephemeral-authorized_keys-all": public,
    }

    console = [
        ("-device", "virtio-serial"),
        (
            "-smbios",
            "type=11,value=io.systemd.boot.kernel-cmdline-extra=console=hvc0",
        ),
    ]

    if attach_console < 2:
        console.extend(
            [
                ("-chardev", f"file,path={ipc}/console,id=console-log"),
                ("-device", "virtconsole,chardev=console-log"),
            ]
        )

    if attach_console > 0:
        console.extend(
            [
                ("-chardev", "stdio,mux=on,signal=off,id=console-stdio"),
                ("-mon", "chardev=console-stdio,mode=readline"),
            ]
        )

    if attach_console == 1:
        console.extend(
            [
                ("-device", "virtconsole,chardev=console-stdio"),
            ]
        )
        creds["getty.ttys.serial"] = "hvc1\n"

    if attach_console == 2:
        console.extend(
            [
                ("-device", "virtconsole,chardev=console-stdio"),
            ]
        )

    drive = f"file={image},format=qcow2,if=virtio,media=disk"
    if snapshot:
        # TODO: the image can still be written even with snapshot=true, using
        # an explicit commit.  We need to figure out a way to prevent that from
        # happening...
        drive = drive + ",snapshot=on"

    # we don't have a good way to dynamically allocate guest-cid so we
    # assign it to the same numeric value as the port number the kernel
    # gave us when we created our notify-socket listener (which is unique)
    guest_cid = port

    args = [
        "-nodefaults",
        _find_ovmf(),
        ("-smp", f"{cpus}"),
        ("-m", f"{memory}"),
        ("-display", "none"),
        ("-qmp", f"unix:{ipc}/qmp,server,wait=off"),
        # Console stuff...
        *console,
        ("-device", f"vhost-vsock-pci,id=vhost-vsock-pci0,guest-cid={guest_cid}"),
        ("-drive", drive),
        # Credentials
        *(
            ("-smbios", f"type=11,value=io.systemd.credential:{k}={v}")
            for k, v in creds.items()
        ),
    ]

    return await _spawn("qemu-kvm", *args)


async def _wait_qemu(
    qemu: asyncio.subprocess.Process, shutdown_ok: Callable[[], bool]
) -> None:
    try:
        await qemu.wait()
        if not shutdown_ok():
            raise QemuExited
    except asyncio.CancelledError:
        qemu.terminate()
        await asyncio.shield(asyncio.wait_for(qemu.wait(), 0))


async def _qmp_command(ipc: Path, command: str) -> object:
    reader, writer = await asyncio.open_unix_connection(ipc / "qmp")

    async def execute(command: str) -> object:
        writer.write((json.dumps({"execute": command}) + "\n").encode())
        await writer.drain()
        while True:
            response = json.loads(await reader.readline())
            if "event" in response:
                continue
            if "return" in response:
                return response["return"]
            raise RuntimeError(f"Got error response from qmp: {response!r}")

    # Trivial handshake (ignore them, send nothing)
    _ = json.loads(await reader.readline())
    await execute("qmp_capabilities")

    response = await execute(command)

    writer.close()
    await writer.wait_closed()

    return response


async def _qmp_quit(qmp: Path, *, hard: bool) -> None:
    await _qmp_command(qmp, "quit" if hard else "system_powerdown")


def _ssh_direct_args(
    ipc: Path, private: Path, port: int
) -> tuple[str | Path | tuple[str | Path, ...], ...]:
    options = {
        # Fake that we know the host key
        "KnownHostsCommand": "/bin/echo %H %t %K",
        # Use systemd-ssh-proxy to connect via vsock
        "ProxyCommand": f"/usr/lib/systemd/systemd-ssh-proxy vsock/{port} 22",
        "ProxyUseFdpass": "yes",
        # Try to prevent interactive prompting and/or updating known_hosts
        # files or otherwise interacting with the environment
        "BatchMode": "yes",
        "IdentitiesOnly": "yes",
        "PKCS11Provider": "none",
        "PasswordAuthentication": "no",
        "StrictHostKeyChecking": "yes",
        "UserKnownHostsFile": "/dev/null",
    }

    return (
        ("-F", "none"),  # don't use the user's config
        ("-i", private),
        *(("-o", f"{k} {v}") for k, v in options.items()),
        ("-l", "root"),
        ipc.name,  # the name is ignored but displayed in messages
    )


def _ssh_fast_args(ipc: Path) -> tuple[str | Path | tuple[str | Path, ...], ...]:
    return (
        ("-F", "none"),  # don't use the user's config
        ("-S", ipc / "ssh"),  # connect via the control socket
        ipc.name,  # the name is ignored but displayed in messages
    )


async def _run_ssh_control(
    *, ipc: Path, private: Path, port: int
) -> asyncio.subprocess.Process:
    ssh = await _spawn(
        "ssh",
        *_ssh_direct_args(ipc, private, port),
        ("-N", "-n"),  # no command, stdin disconnected
        ("-M", "-S", ipc / "ssh"),  # listen on the control socket
        stdin=asyncio.subprocess.DEVNULL,
        stdout=asyncio.subprocess.PIPE,
    )
    # ssh sends EOF after the connection succeeds
    assert ssh.stdout
    await ssh.stdout.read()

    return ssh


class VirtualMachine:
    """A handle to a running virtual machine.

    This can be used to perform operations on that machine.
    """

    """ssh command-line arguments for executing commands"""
    ssh_args: tuple[str | Path | tuple[str | Path, ...], ...]

    """ssh command-line arguments to be used to connect directly to the vsock"""
    ssh_direct_args: tuple[str | Path | tuple[str | Path, ...], ...]

    def __init__(self, ipc: Path, private: Path, port: int) -> None:
        """Don't construct VirtualMachine yourself.  Use run_vm()."""
        self.ssh_direct_args = _ssh_direct_args(ipc, private, port)
        self.ssh_args = _ssh_fast_args(ipc)
        self.ipc = ipc

    def get_id(self) -> str:
        """Get the machine identifier like `tt.0`, `tt.1`, etc."""
        return self.ipc.name

    async def _ssh_cmd(self, *args: tuple[str | Path, ...]) -> None:
        await _run("ssh", *self.ssh_args, *args)

    async def forward_port(self, spec: str) -> None:
        """Set up a port forward.

        The `spec` is the format used by `ssh -L`, and looks something like
        `2222:127.0.0.1:22`.
        """
        return await self._ssh_cmd(("-O", "forward"), ("-L", spec))

    async def cancel_port(self, spec: str) -> None:
        """Cancel a previous forward."""
        return await self._ssh_cmd(("-O", "cancel"), ("-L", spec))

    async def execute(
        self,
        cmd: str,
        *args: str | tuple[str, ...],
        check: bool = True,
        direct: bool = False,
        input: bytes | str | None = b"",  # noqa:A002  # shadows `input()` but so does subprocess module
        environment: Mapping[str, str] = {},
        stdout: int | None = asyncio.subprocess.PIPE,
    ) -> str:
        """Execute a command on the guest.

        If a single argument is given, it is expected to be a valid shell
        script.  If multiple arguments are given, they will interpreted as an
        argument vector and will be properly quoted before being sent to the guest.
        """
        if args:
            cmd = join_args(cmd, *args)

        full_command = (
            "ssh",
            *(self.ssh_direct_args if direct else self.ssh_args),
            ("--", "set -e;"),
            tuple(f"export {k}={shlex.quote(v)};" for k, v in environment.items()),
            cmd,
        )

        ssh = await _spawn(
            *full_command,
            stdin=asyncio.subprocess.PIPE,
            stdout=stdout,
        )
        input_bytes = input.encode() if isinstance(input, str) else input
        output, _ = await ssh.communicate(input_bytes)
        returncode = await ssh.wait()
        if check and returncode != 0:
            raise SubprocessError(full_command, returncode, output)
        return output.decode()

    async def qmp(self, command: str) -> object:
        """Send a QMP command to the hypervisor.

        This can be used for things like modifying the hardware configuration.
        Don't power it off this way: the correct way to stop the VM is to exit
        the context manager.
        """
        return await _qmp_command(self.ipc, command)


class QemuExited(Exception):
    """An exception thrown when qemu exits unexpectedly.

    You can request that this be suppressed by passing shutdown_ok=True to run_vm().
    """


class SubprocessError(Exception):
    """An exception thrown when a subprocess failed unexpectedly."""

    def __init__(
        self,
        args: tuple[str | Path | tuple[str | Path, ...], ...],
        returncode: int,
        output: bytes | None = None,
    ) -> None:
        """Create a SubprocessError instance.

        - args: the arguments to the command that failed
        - returncode: the non-zero return code
        """
        self.args = args
        self.returncode = returncode
        self.output = output
        super().__init__(
            f"Subprocess exited unexpectedly with return code {returncode}:\n"
            f"{pretty_print_args(*args)}\n\n"
        )


@contextlib.asynccontextmanager
async def run_vm(
    image: Path | str,
    *,
    attach_console: bool = False,
    cpus: int = 4,
    identity: tuple[Path, str] | None = None,
    memory: int | str = "4G",
    shutdown: bool = True,
    shutdown_ok: bool = False,
    sit: bool = False,
    snapshot: bool = True,
    status_messages: bool = False,
) -> AsyncGenerator[VirtualMachine]:
    """Run a VM, returning a handle that can be used to perform operations on it.

    This is meant to be used as an async context manager like so:

    image = Path("...")
    async with run_vm(image) as vm:
        await vm.execute("cat", "/usr/lib/os-release")

    The user of the context manager runs in context of an asyncio.TaskGroup and
    will be cancelled if anything unexpected happens (ssh connection lost, VM
    exiting, etc).

    When the context manager is exited the machine is taken down.

    When the machine is running it is also possible to access it from outside.
    See the documentation for the module.

    The kwargs allow customizing the behaviour:
      - attach_console: if qemu should connect the console to stdio
      - sit: if we should "sit" when an exception occurs: print the exception
        and wait for input (to allow inspecting the running VM)
      - shutdown: if the machine should be shut down on exit from the context
        manager (otherwise: wait)
      - shutdown_ok: if other shutdowns/exits are expected (ie: due to user
        interaction)
      - snapshot: if the 'snapshot' option is used on the disk (changes are
        transient)
      - status_messages: if we should do output of extra messages
    """
    async with contextlib.AsyncExitStack() as exit_stack, asyncio.TaskGroup() as tg:
        # We create a temporary directory for various sockets, ssh keys, etc.
        ipc = exit_stack.enter_context(_IpcDir())

        if identity is None:
            private, public = await _ssh_keygen(ipc)
        else:
            private, public = identity

        ssh_access = asyncio.Event()
        notify_listener, port = _vsock_listen(socket.SOCK_SEQPACKET)

        def notify(key: str, value: str) -> None:
            if status_messages:
                print(f"notify: {key}={value}")
            if (key, value) == ("X_SYSTEMD_UNIT_ACTIVE", "ssh-access.target"):
                ssh_access.set()

        notify_task = tg.create_task(_notify_server(notify_listener, notify))

        qemu = await _run_qemu(
            attach_console=attach_console,
            cpus=cpus,
            image=image,
            ipc=ipc,
            memory=memory,
            port=port,
            public=public,
            snapshot=snapshot,
        )

        tg.create_task(_wait_qemu(qemu, lambda: shutdown_ok))

        await ssh_access.wait()
        ssh = await _run_ssh_control(ipc=ipc, private=private, port=port)

        vm = VirtualMachine(ipc, private, port)

        try:
            yield vm
        except Exception as exc:
            if sit:
                print("🤦")
                traceback.print_exception(
                    exc.__class__, exc, exc.__traceback__, file=sys.stderr
                )
                # <pitti> lis: the ages old design question: does the button
                # show the current state or the future one when you press it :)
                # <lis> pitti: that's exactly my question.  by taking the one
                # with both then i don't have to choose! :D
                # <lis> although to be honest, i find your argument convincing.
                # i'll put the ⏸️ back
                # <pitti> lis: it was more of a joke -- I actually agree that a
                # play/pause button is nicer
                # <lis> too late lol
                await _wait_stdin("⏸️ ")
            raise

        if shutdown:
            shutdown_ok = True
            ssh.terminate()
            # If we're in snapshot mode then we don't have to do a clean shutdown
            await _qmp_quit(ipc, hard=snapshot)

        notify_task.cancel()


async def _async_main() -> None:
    parser = argparse.ArgumentParser(
        description="test.thing - a simple modern VM runner"
    )
    parser.add_argument(
        "--maintain", "-m", action="store_true", help="Changes are permanent"
    )
    parser.add_argument(
        "--attach", "-a", action="count", help="Attach to the VM console", default=0
    )
    parser.add_argument("--sit", "-s", action="store_true", help="Pause on exceptions")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Print verbose output"
    )
    parser.add_argument("image", type=Path, help="The path to a qcow2 VM image to run")
    args = parser.parse_args()

    async with run_vm(
        args.image,
        shutdown=not args.attach,
        shutdown_ok=True,
        attach_console=args.attach,
        status_messages=args.verbose,
        snapshot=not args.maintain,
        sit=args.sit,
    ) as vm:
        if not args.attach:
            await _wait_stdin(f"\nVM running: {vm.get_id()}\n\nEnter or EOF to exit ⏸️ ")


def _main() -> None:
    asyncio.run(_async_main())


if __name__ == "__main__":
    _main()
