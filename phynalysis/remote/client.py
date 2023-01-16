"""Phynalysis remote client."""

import paramiko
import errno


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

    def mkdir(self, path):
        """Make directory."""
        self.ssh_client.exec_command(f"mkdir -p {path}")

    def put(self, local_path, remote_path):
        """Put a file."""
        self.sftp_client.put(local_path, remote_path)
