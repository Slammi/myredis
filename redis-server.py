# redis-server.py

import socket
import argparse

from utils import server_response_decode, command_handler

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65429  # Port to listen on (non-privileged ports are > 1023)
MY_DICT = {}
FAKE_RESPONSE_1 = "OK"
FAKE_RESPONSE_2 = ""


# Creates socket object that binds port and listens for incoming connection.
# Returns raw decoded data if needed (for debugging ect.)
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=6379,
        help="This is the default port to connect to",
    )
    return parser.parse_args()


def listen_and_respond():
    args = parse_args()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, args.port))
        s.listen()
        # Creates infinite while statement that accepts incoming connections and transmits data between
        while True:
            conn, addr = s.accept()
            print(f"Connected by {addr}")
            data = conn.recv(1024).decode()
            # if no data is sent the statements are broken and script ends.
            if not data:
                break
            decoded_response, _ = server_response_decode(data)
            # str_decoded_response = " ".join(decoded_response)
            # parse command and either retrieve/store data or return error message
            RESP_encoded_response = command_handler(decoded_response, MY_DICT)
            conn.sendall(f"{RESP_encoded_response}".encode())
    return data


if __name__ == "__main__":
    listen_and_respond()
