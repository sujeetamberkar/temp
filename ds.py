import socket
import time
import os
import zipfile
def receive_file(file_path, host, port):
    """
    Receives a file over TCP and saves it to the specified path.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, port))
        sock.listen(1)
        print(f"Waiting for file on {host}:{port}...")
        conn, _ = sock.accept()
        with conn:
            with open(file_path, 'wb') as file:
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    file.write(data)
            print(f"Received file saved as {file_path}.")

def send_file(file_path, target_servers, max_attempts=5, retry_delay=2):
    """
    Attempts to send the specified file to each target server in the target_servers list.
    Retries a maximum of max_attempts times with a delay of retry_delay seconds between attempts.
    """
    for host, port in target_servers:
        for attempt in range(1, max_attempts + 1):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.connect((host, port))
                    with open(file_path, 'rb') as file:
                        sock.sendfile(file)
                    print(f"Successfully sent {file_path} to {host}:{port}")
                    break  # Success, no need to retry
            except ConnectionRefusedError:
                print(f"Attempt {attempt} failed: Connection to {host}:{port} refused.")
                if attempt < max_attempts:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    print(f"Failed to send {file_path} to {host}:{port} after {max_attempts} attempts.")
def receive_and_unzip_files(host, port, output_dir):
    """
    Listens for incoming zip files from x.py, y.py, and z.py, saves them, and unzips them into the specified output directory.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(3)  # Expecting 3 connections
    print(f"Waiting for zip files on {host}:{port}...")

    for _ in range(3):  # Expecting 3 files in total
        conn, addr = server_socket.accept()
        with conn:
            print(f"Connection established with {addr}")
            received_zip = os.path.join(output_dir, f"received_{addr[1]}.zip")
            with open(received_zip, 'wb') as file:
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    file.write(data)
            print(f"File received and saved as {received_zip}")
            unzip_file(received_zip, output_dir)
            os.remove(received_zip)  # Delete the zip file after extraction

def unzip_file(zip_path, extract_to):
    """
    Unzips the file at zip_path to the directory specified by extract_to.
    """
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print(f"Files from {zip_path} have been extracted to {extract_to}")


def zip_directory(directory_name, zip_name):
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(directory_name):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, arcname=os.path.relpath(file_path, start=directory_name))
    print(f"Directory {directory_name} zipped into {zip_name}")


if __name__ == "__main__":
    file_path = 'received_data.zip'
    receive_host = 'localhost'
    receive_port = 12345

    # Target servers where the file should be sent after receipt
    target_servers = [
        ('localhost', 12346),  # Server for x.py
        ('localhost', 12347),  # Server for y.py
        ('localhost', 12348)   # Server for z.py
    ]

    # Step 1: Receive a file from a client
    receive_file(file_path, receive_host, receive_port)
    
    # Step 2: Forward the file to the target servers
    send_file(file_path, target_servers)
    common_output_dir = 'Common_Output'  # Directory where files from x, y, z are extracted
    receive_and_unzip_files('localhost', 12349, common_output_dir)
    final_zip_name = 'final_output.zip'
    zip_directory('Common_Output', final_zip_name)
    send_file(final_zip_name, [('localhost', 12350)])











