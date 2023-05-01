# redis-server.py

import socket

from utils import server_response_decode

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65430  # Port to listen on (non-privileged ports are > 1023)
MY_DICT = {}

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    while True:
        conn, addr = s.accept()
        print(f"Connected by {addr}")
        data = conn.recv(1024).decode()
        if not data:
            break
        decoded_response, _ = server_response_decode(data)
        str_decoded_response = " ".join(decoded_response)
        # parse command and either retrieve/store data or return error message
        conn.sendall(str_decoded_response.encode())
