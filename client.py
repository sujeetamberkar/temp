import os
import socket
import zipfile

def zip_files(input_dir, output_zip):
    """
    Zips all files in the specified input directory and saves the zip file with the given name.
    """
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(input_dir):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, input_dir))

def send_file(file_path, host, port):
    """
    Sends the specified file to the given host and port using a TCP socket.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, port))
        with open(file_path, 'rb') as file:
            sock.sendfile(file)
        print(f"File {file_path} has been sent to {host}:{port}")
def receive_and_unzip_file(file_path, host, port, extract_to):
    """
    Receives a file over TCP and saves it to the specified path, then unzips it.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
            print(f"Received file saved as {file_path}")
    
    # Unzip the received file
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print(f"File {file_path} has been unzipped to {extract_to}")

if __name__ == "__main__":
    input_dir = 'User_Input'  # Directory to zip
    output_zip = 'user_input.zip'  # Output zip file name
    host = 'localhost'  # Server's IP address (change if needed)
    port = 12345  # Server's port number

    # Ensure the 'User_Input' directory exists
    if not os.path.exists(input_dir):
        print(f"The directory {input_dir} does not exist. Please create it and try again.")
    else:
        zip_files(input_dir, output_zip)  # Zip the files
        send_file(output_zip, host, port)  # Send the zip file
    
    file_path = 'received_final_output.zip'
    host = 'localhost'  # Listening host
    port = 12350  # Listening port
    extract_to = 'User_Output'  # Extraction directory

    # Ensure the extraction directory exists
    if not os.path.exists(extract_to):
        os.makedirs(extract_to)
    
    receive_and_unzip_file(file_path, host, port, extract_to)

