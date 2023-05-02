import argparse
import socket


from utils import generate_redis_formatted_array, server_response_decode

HOST = "127.0.0.1"  # Local host IP
PORT = 6380  # Current port used by the server


def main():
    # Generates redis formatted array from CLI input.
    args = parse_args()
    redis_format_client_message = generate_redis_formatted_array(
        args.key_or_value, args.message
    )
    # Opens connection with server and facilitates send/receive of client message/server response.
    server_connect_and_communicate(redis_format_client_message, port=args.port)


def parse_args():
    # Start argparse for accepting commands from client
    parser = argparse.ArgumentParser(
        description="This will print a statement passed as argument",
        epilog="Why are you even reading the help page for this?",
    )

    # required argument for 3 commands [GET, SET, DEL] and its proceeding argument providing keys to be retrieved, set or deleted.
    parser.add_argument(
        "message",
        type=str,
        choices=["GET", "SET", "DEL"],
        default="You didn't input anything",
    )

    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=PORT,
        help="This is the default port to connect to",
    )
    parser.add_argument("key_or_value", type=str, nargs="+")
    return parser.parse_args()


def server_connect_and_communicate(
    redis_formatted_cli_message, port, host="127.0.0.1", buffer_size=1024
):
    # Function that will open connection with server on specificied HOST and PORT, transmits encoded message,
    # and provides server response. Message must be encoded into Redis format before passing to this function.
    with socket.socket() as s:
        s.connect((host, port))
        s.sendall(redis_formatted_cli_message.encode())
        response = s.recv(buffer_size).decode()
        server_response, _ = server_response_decode(response)
        print(server_response)


if __name__ == "__main__":
    main()
