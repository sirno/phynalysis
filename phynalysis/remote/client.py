"""Phynalysis remote client."""

import paramiko
import errno
import rich
import scp
import stat


class PhynalysisRemoteClient:
    """Remote client."""

    def __init__(self, host: str, user: str):
        """Initialize the remote client."""
        self.user: str = user
        self.host: str = host

        self._ssh_client = None
        self._sftp_client = None
        self._scp_client = None

        self._sftp_client = None

    @property
    def ssh_client(self):
        """SSH client."""
        if self._ssh_client is None:
            self._ssh_client = paramiko.SSHClient()
            self._ssh_client.load_system_host_keys()
            self._ssh_client.connect(self.host, username=self.user)

        return self._ssh_client

    @property
    def sftp_client(self):
        """SFTP client."""
        if self._sftp_client is None:
            self._sftp_client = self.ssh_client.open_sftp()

        return self._sftp_client

    @property
    def scp_client(self):
        """SCP client."""
        if self._scp_client is None:
            self._scp_client = scp.SCPClient(self.ssh_client.get_transport())

        return self._scp_client

    def exists(self, path: str):
        """Check if a path exists."""
        try:
            self.sftp_client.stat(path)
        except IOError as e:
            if e.errno == errno.ENOENT:
                return False
            raise
        else:
            return True

    def is_dir(self, path: str):
        """Check if a path is a directory."""
        return stat.S_ISDIR(self.sftp_client.stat(path).st_mode)

    def is_file(self, path: str):
        """Check if a path is a file."""
        return stat.S_ISREG(self.sftp_client.stat(path).st_mode)

    def mkdir(self, path: str):
        """Make directory."""
        self.execute(f"mkdir -p {path}", print_output=False)

    def mkdirs(self, paths: list[str]):
        """Make directories."""
        self.execute(f"mkdir -p {' '.join(paths)}", print_output=False)

    def listdir(self, path: str):
        """List directory."""
        return self.sftp_client.listdir(path)

    def get(self, remote_path: str, local_path: str):
        """Get a file."""
        self.scp_client.get(remote_path, local_path)

    def put(self, local_path: str, remote_path: str):
        """Put a file."""
        self.scp_client.put(local_path, remote_path)

    def execute(
        self,
        command: str,
        print_output: bool = True,
        print_error: bool = True,
    ):
        """Execute a command."""
        stdin, stdout, stderr = self.ssh_client.exec_command(command)

        exit_code = stdout.channel.recv_exit_status()

        if print_output and stdout.channel.recv_ready():
            output = stdout.read().decode("utf-8").strip()
            if output:
                rich.print(output)

        if print_error or exit_code != 0:
            error = stderr.read().decode("utf-8").strip()
            if error:
                rich.print(f"[red]{error}")

        return stdout.channel.recv_exit_status()

    def find(self, path: str, pattern: str):
        """Find files."""
        stdin, stdout, stderr = self.ssh_client.exec_command(f"fd . {path} {pattern}")
        return stdout.read().decode("utf-8").strip().split("\n")
