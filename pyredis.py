import argparse
import socket


from utils import server_response_decode

HOST = "127.0.0.1"  # Local host IP
PORT = 6379  # Current port used by the Redis server
SPACING = "\r\n"
ARRAY_START = "*"
BULK_STR_START = "$"
BUFFER_SIZE = 1024


def main():
    # Generates redis formatted array from CLI input.
    args = parse_args()
    redis_format_client_message = generate_redis_formatted_array(
        args.key_or_value, args.message
    )

    # Opens connection with server and facilitates send/receive of client message/server response.
    server_connect_and_communicate(redis_format_client_message)


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
    # Potential future command when working with the need to change ports:

    # parser.add_argument('--port','-p',type=int,default=6379, help='This is the default port to connect to')
    parser.add_argument("key_or_value", type=str, nargs="+")
    return parser.parse_args()


def generate_redis_formatted_array(key_or_value, cli_message):
    # Creates dictionary that stores strings of user input with their character length
    # (also a string) for generation of bulk strings and array to be passed to Redis server.
    input_to_length = {item: len(item) for item in key_or_value}
    command_length = len(cli_message)
    total_length = 1 + len(key_or_value)
    encoded_message_start = f"{ARRAY_START}{total_length}{SPACING}{BULK_STR_START}{command_length}{SPACING}{cli_message}{SPACING}"

    # Creates and returns redis formatted array to send to Redis server
    for key, value in input_to_length.items():
        encoded_message_start += f"{BULK_STR_START}{value}{SPACING}{key}{SPACING}"
    return encoded_message_start


def server_connect_and_communicate(redis_formatted_cli_message):
    # Function that will open connection with server on specificied HOST and PORT, transmits encoded message,
    # and provides server response. Message must be encoded into Redis format before passing to this function.
    with socket.socket() as s:
        s.connect((HOST, PORT))
        s.sendall(redis_formatted_cli_message.encode())
        response = s.recv(BUFFER_SIZE).decode()
        server_response, _ = server_response_decode(response)
        print(server_response)


if __name__ == "__main__":
    main()
