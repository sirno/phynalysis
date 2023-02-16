"""Phynalysis remote client."""

import paramiko
import errno
import rich
import stat


class PhynalysisRemoteClient:
    """Remote client."""

    def __init__(self, host: str, user: str):
        """Initialize the remote client."""
        self.user: str = user
        self.host: str = host

        self._ssh_client = None
        self._sftp_client = None

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

    def exists(self, path):
        """Check if a path exists."""
        try:
            self.sftp_client.stat(path)
        except IOError as e:
            if e.errno == errno.ENOENT:
                return False
            raise
        else:
            return True

    def is_dir(self, path):
        """Check if a path is a directory."""
        return stat.S_ISDIR(self.sftp_client.stat(path).st_mode)

    def is_file(self, path):
        """Check if a path is a file."""
        return stat.S_ISREG(self.sftp_client.stat(path).st_mode)

    def mkdir(self, path):
        """Make directory."""
        self.execute(f"mkdir -p {path}", print_output=False)

    def listdir(self, path):
        """List directory."""
        return self.sftp_client.listdir(path)

    def get(self, remote_path, local_path):
        """Get a file."""
        self.sftp_client.get(remote_path, local_path)

    def put(self, local_path, remote_path):
        """Put a file."""
        self.sftp_client.put(local_path, remote_path)

    def execute(self, command, print_output=True, print_error=True):
        """Execute a command."""
        stdin, stdout, stderr = self.ssh_client.exec_command(command)

        if print_output and stdout.channel.recv_ready():
            output = stdout.read().decode("utf-8").strip()
            if output:
                rich.print(output)

        if print_error:
            error = stderr.read().decode("utf-8").strip()
            if error:
                rich.print(f"[red]{error}")

        return stdout.channel.recv_exit_status()

    def find(self, path, pattern):
        """Find files."""
        stdin, stdout, stderr = self.ssh_client.exec_command(f"fd . {path} {pattern}")
        return stdout.read().decode("utf-8").strip().split("\n")
