import paramiko

class SFTPConnector:
    def __init__(self, host, port, username, password):
        self.transport = paramiko.Transport((host, port))
        self.transport.connect(username=username, password=password)
        self.sftp = paramiko.SFTPClient.from_transport(self.transport)

    def upload_file(self, local_path, remote_path):
        self.sftp.put(local_path, remote_path)

    def download_file(self, remote_path, local_path):
        self.sftp.get(remote_path, local_path)

    def close(self):
        self.sftp.close()
        self.transport.close()