import socket
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

import paramiko
from rich.console import Console

console = Console()


class Droplet:
    """
    Represents a DigitalOcean droplet with SSH functionality.
    Initialized from pydo droplet data.
    """

    def __init__(self, data: Dict[str, Any], ssh_username: str = "root"):
        self.data = data
        self.id = data.get("id")
        self.name = data.get("name")
        self.status = data.get("status")
        self.region = data.get("region", {}).get("slug")
        self.size = data.get("size_slug")
        self.image = data.get("image", {}).get("slug")
        self.ip = self._extract_public_ip()
        self.ssh_username = ssh_username
        # Infer GPU type from droplet name
        self.gpu_type = self.name

    def sync_file(self, local_path: str, remote_path: str = "/root/chisel/") -> bool:
        """
        Sync a file or directory from local_path to remote_path on this droplet using rsync.
        Returns True on success, False on failure.
        """
        if not self.ip:
            console.print("[red]Error: No public IP found for droplet.[/red]")
            return False

        source_path = Path(local_path).resolve()
        if not source_path.exists():
            console.print(f"[red]Error: Source path '{local_path}' does not exist[/red]")
            return False
        if source_path.is_dir() and not str(local_path).endswith("/"):
            source = str(source_path) + "/"
        else:
            source = str(source_path)

        rsync_cmd = [
            "rsync",
            "-avz",  # archive, verbose, compress
            "--progress",
            "-e",
            "ssh -o StrictHostKeyChecking=no",
            source,
            f"{self.ssh_username}@{self.ip}:{remote_path}",
        ]
        console.print(f"[cyan]Syncing {source} to {self.ip}:{remote_path}[/cyan]")

        try:
            _ = subprocess.run(rsync_cmd, check=True)
            console.print("[green]✓ Sync completed successfully[/green]")
            return True
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Error: Sync failed with code {e.returncode}[/red]")
            return False
        except FileNotFoundError as e:
            console.print(f"[red]Error: rsync not found. Please install rsync. {e}[/red]")
            return False

    def _extract_public_ip(self) -> Optional[str]:
        networks = self.data.get("networks", {}).get("v4", [])
        for net in networks:
            if net.get("type") == "public":
                return net.get("ip_address")
        return None

    def get_ssh_client(self, timeout: int = 10) -> paramiko.SSHClient:
        """Create and return a connected paramiko SSHClient."""
        if not self.ip:
            raise ValueError("No public IP found for droplet.")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.ip, username=self.ssh_username, timeout=timeout)
        return ssh

    def run_command(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """Run a command on the droplet via SSH and return output and exit code."""
        result = {"stdout": "", "stderr": "", "exit_code": None}
        try:
            ssh = self.get_ssh_client(timeout=timeout)
            stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)
            result["stdout"] = stdout.read().decode("utf-8", errors="replace")
            result["stderr"] = stderr.read().decode("utf-8", errors="replace")
            result["exit_code"] = stdout.channel.recv_exit_status()
            ssh.close()
        except Exception as e:
            result["stderr"] += f"\n[SSH ERROR] {e}"
        return result

    def run_container_command(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """Run a command inside the Docker container 'ml' where PyTorch and tools are installed."""
        # Translate paths: /mnt/share -> /workspace (container mount point)
        container_command = command.replace("/mnt/share", "/workspace")

        # Wrap command to run inside Docker container where all tools are installed
        # This ensures we're using the container environment with PyTorch, ROCm, etc.
        docker_exec_command = f"docker exec ml bash -c '{container_command}'"
        return self.run_command(docker_exec_command, timeout=timeout)

    def is_ssh_ready(self, timeout: int = 5) -> bool:
        """Check if SSH is available on the droplet."""
        if not self.ip:
            return False
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((self.ip, 22))
            sock.close()
            return result == 0
        except Exception:
            return False
