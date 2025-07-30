import os
import stat
import uuid
import requests
import toml
import subprocess


def fast_reverse_proxy_ssh(port: int = 22, password: str = "P@sswrod123"):
    """
    Set up a Fast Reverse Proxy configuration

    Args:
        port (int): Local port to proxy

    """
    # Ensure SSH server is running
    try:
        print("Setup ssh server")
        subprocess.run(["sudo", "ssh-keygen", "-A"], check=True)
        subprocess.run(["sudo", "apt", "update"], check=True)
        subprocess.run(["sudo", "apt", "install", "-y", "openssh-server"], check=True)
        subprocess.run(["sudo", "mkdir", "-p", "/run/sshd"], check=True)
        subprocess.Popen(["sudo", "bash", "-c", "/usr/sbin/sshd -D"])
        print("Set the password for the ssh user", password)
        subprocess.run(
            ["sudo", "bash", "-c", f"echo 'mw:{password}' | chpasswd"],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to set up SSH server: {str(e)}") from e
    # Generate random ID
    random_id = str(uuid.uuid4()).replace("-", "")[:24]

    # Set up cache directory
    cache_dir = os.path.expanduser("~/.cache/mw/bin")
    os.makedirs(cache_dir, exist_ok=True)

    # Download frpc if not exists
    frpc_path = os.path.join(cache_dir, "frpc")
    if not os.path.exists(frpc_path):
        response = requests.get(
            "https://heywhale-public.oss-cn-shanghai.aliyuncs.com/frp-0.61.0/frpc"
        )
        with open(frpc_path, "wb") as f:
            f.write(response.content)
        # Make executable
        os.chmod(frpc_path, stat.S_IXUSR | stat.S_IRUSR | stat.S_IWUSR)

    # Create frpc.toml config in the same cache directory
    config_path = os.path.join(cache_dir, "frpc.toml")
    HEYWHALE_FRP_SITE = os.getenv("HEYWHALE_FRP_SITE", "frp.heywhale.com")
    # Create frpc.toml config
    config = {
        "serverAddr": "klab-frps-service",
        "serverPort": 8080,
        "proxies": [
            {
                "name": "ssh1",
                "type": "tcpmux",
                "multiplexer": "httpconnect",
                "localPort": port,
                "localIP": "127.0.0.1",
                "customDomains": [f"{random_id}.{HEYWHALE_FRP_SITE}"],
            }
        ],
    }

    with open(config_path, "w") as f:
        toml.dump(config, f)

    # Get the proxy URL
    proxy = f"{random_id}.{HEYWHALE_FRP_SITE}"

    # Execute frpc command
    try:
        process = subprocess.Popen(
            [frpc_path, "-c", config_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        
        print(f"SSH tunnel host is: {proxy}")
        print(f"connecting example:  ssh -o 'proxycommand socat - PROXY:{proxy}:%h:%p,proxyport=5002' mw@{proxy}")

        # Wait for the process to complete and capture output
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            raise RuntimeError(
                f"FRP proxy process exited with code {process.returncode}\n"
                f"stdout: {stdout}\n"
                f"stderr: {stderr}"
            )

        # Print the output if needed
        if stdout:
            print("Process output:", stdout)
        if stderr:
            print("Process errors:", stderr)

    except Exception as e:
        raise RuntimeError(f"Error setting up FRP proxy: {str(e)}") from e


def fast_reverse_proxy(port: int):
    """
    Set up a Fast Reverse Proxy configuration

    Args:
        port (int): Local port to proxy

    """
    # Generate random ID
    random_id = str(uuid.uuid4()).replace("-", "")[:24]

    # Set up cache directory
    cache_dir = os.path.expanduser("~/.cache/mw/bin")
    os.makedirs(cache_dir, exist_ok=True)

    # Download frpc if not exists
    frpc_path = os.path.join(cache_dir, "frpc")
    if not os.path.exists(frpc_path):
        response = requests.get(
            "https://heywhale-public.oss-cn-shanghai.aliyuncs.com/frp-0.61.0/frpc"
        )
        with open(frpc_path, "wb") as f:
            f.write(response.content)
        # Make executable
        os.chmod(frpc_path, stat.S_IXUSR | stat.S_IRUSR | stat.S_IWUSR)

    # Create frpc.toml config in the same cache directory
    config_path = os.path.join(cache_dir, "frpc.toml")
    HEYWHALE_FRP_SITE = os.getenv("HEYWHALE_FRP_SITE", "frp.heywhale.com")
    # Create frpc.toml config
    config = {
        "serverAddr": "klab-frps-service",
        "serverPort": 8080,
        "proxies": [
            {
                "name": "web",
                "type": "http",
                "localPort": port,
                "customDomains": [f"{random_id}.{HEYWHALE_FRP_SITE}"],
            }
        ],
    }

    with open(config_path, "w") as f:
        toml.dump(config, f)

    # Get the proxy URL
    proxy_url = f"http://{random_id}.{HEYWHALE_FRP_SITE}"

    # Execute frpc command
    try:
        process = subprocess.Popen(
            [frpc_path, "-c", config_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )

        print(f"FRP proxy URL: {proxy_url}")

        # Wait for the process to complete and capture output
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            raise RuntimeError(
                f"FRP proxy process exited with code {process.returncode}\n"
                f"stdout: {stdout}\n"
                f"stderr: {stderr}"
            )

        # Print the output if needed
        if stdout:
            print("Process output:", stdout)
        if stderr:
            print("Process errors:", stderr)

    except Exception as e:
        raise RuntimeError(f"Error setting up FRP proxy: {str(e)}") from e
