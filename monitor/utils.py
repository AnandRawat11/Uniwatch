import paramiko
import os

def setup_server_with_ansible(ip_address, ssh_user='ubuntu'):
    """
    Ab yeh function Ansible ki jagah direct Paramiko (SSH) use karega.
    Naam 'setup_server_with_ansible' hi rakha hai taaki views.py mein change na karna pade.
    """
    # Windows mein automatically tumhari .ssh/id_rsa file utha lega
    key_path = os.path.expanduser('~/.ssh/id_rsa')
    logs = f"Starting native SSH setup for {ip_address}...\n"
    
    try:
        # SSH Connection Setup
        key = paramiko.RSAKey.from_private_key_file(key_path)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        logs += f"Connecting to {ip_address} as {ssh_user}...\n"
        ssh.connect(hostname=ip_address, username=ssh_user, pkey=key, timeout=10)
        logs += "SSH Connection Successful!\n\n"
        
        # Node Exporter Install & Setup Commands
        setup_commands = [
            "sudo useradd --system --no-create-home --shell /bin/false node_exporter || true",  # || true ensures it doesn't fail if user already exists
            "wget -qO- https://github.com/prometheus/node_exporter/releases/download/v1.7.0/node_exporter-1.7.0.linux-amd64.tar.gz | tar xvz -C /tmp/",
            "sudo mv /tmp/node_exporter-1.7.0.linux-amd64/node_exporter /usr/local/bin/",
            "sudo bash -c 'cat <<EOF > /etc/systemd/system/node_exporter.service\n[Unit]\nDescription=Node Exporter\n\n[Service]\nUser=node_exporter\nExecStart=/usr/local/bin/node_exporter\n\n[Install]\nWantedBy=multi-user.target\nEOF'",
            "sudo systemctl daemon-reload",
            "sudo systemctl start node_exporter",
            "sudo systemctl enable node_exporter"
        ]
        
        # Ek-ek karke command run karenge aur unka status check karenge
        for cmd in setup_commands:
            stdin, stdout, stderr = ssh.exec_command(cmd)
            exit_status = stdout.channel.recv_exit_status()  # Wait for command to finish
            
            if exit_status == 0:
                # Command successfully chal gayi (sirf command ka pehla word log mein dikhayenge clean dikhne ke liye)
                logs += f"[SUCCESS] {cmd.split()[0]} command executed.\n"
            else:
                # Agar koi error aayi
                error_msg = stderr.read().decode().strip()
                logs += f"[ERROR] Command failed!\nDetails: {error_msg}\n"
                return False, logs
                
        logs += "\nNode Exporter is successfully installed and running!"
        return True, logs
        
    except Exception as e:
        logs += f"[CRITICAL ERROR] Connection or execution failed: {str(e)}"
        return False, logs
        
    finally:
        # Hamesha connection close karna achi practice hai
        try:
            ssh.close()
        except:
            pass