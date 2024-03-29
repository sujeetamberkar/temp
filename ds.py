import socket
import time

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




