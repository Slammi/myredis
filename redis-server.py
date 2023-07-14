# redis-server.py

import socket
import argparse
import threading
import time

from utils import server_response_decode, SEPARATOR, BULK_STR_START

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 6380  # Port to listen on (non-privileged ports are > 1023)
DATA_DICT = {}  # Dictionary for storage of data on "Redis" server
TIME_DICT = {}  # Dictionary for storing key and time (value) for SET time based options
BUFFER_SIZE = 1024
NIL_REPLY = "$-1" + SEPARATOR
SYNTAX_ERROR_MSG = "-ERR syntax error" + SEPARATOR
TIME_OPTIONS = set(["EX", "PX", "EXAT", "PXAT", "KEEPTTL"])
SET_OPTIONS = set(TIME_OPTIONS + ["XX", "NX", "GET"])
OKAY = "+OK" + SEPARATOR


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=PORT,
        help="This is the default port to connect to",
    )
    return parser.parse_args()


def listen_and_respond():
    args = parse_args()
    with socket.socket() as s:
        s.bind((HOST, args.port))
        s.listen()
        # Creates infinite while statement that accepts incoming connections and transmits data between
        while True:
            conn, addr = s.accept()
            # print(f"Connected by {addr}")
            data = conn.recv(BUFFER_SIZE).decode()
            # if no data is sent the statements are broken and script ends.
            if not data:
                break
            decoded_response, _ = server_response_decode(data)
            # parse command and either retrieve/store data or return error message
            RESP_encoded_response = command_handler(decoded_response)
            conn.sendall(f"{RESP_encoded_response}".encode())
    return data


def unknown_command_error_response(message):
    return f"-ERR unknown command '{' '.join(message)}'{SEPARATOR}"


def bulk_string_response(length, response):
    return f"{BULK_STR_START}{length}{SEPARATOR}{response}{SEPARATOR}"


def command_handler(message):
    # generates bulk string, simple string, null reply and integer reply.
    if type(message) != list:
        return unknown_command_error_response(message)
    if message[0] == "GET":
        if len(message) != 2:
            return unknown_command_error_response(message)
        if message[1] not in DATA_DICT:
            return NIL_REPLY
        value_len = len(DATA_DICT[message[1]])
        return bulk_string_response(value_len, DATA_DICT[message[1]])
    if message[0] == "DEL":
        count = 0
        for part in message[1:]:
            if part in DATA_DICT:
                del DATA_DICT[part]
                count += 1
        return f":{count}{SEPARATOR}"
    if message[0] == "SET":
        if len(message) >= 4:
            set_options = message[3:]
            # (TODO: COMMANDS AFTER SET OPTIONS WILL NOT THROW ERRORS EVEN IF THEY ARE GARBAGE. WILL NEED TO IMPLEMENT
            # POSITIONAL/INDEX BASED PARSING IN FUTURE TO ADDRESS THIS ISSUE)
            # Immediate exit for syntax errors with options that don't work together
            # (MAY WANT TO ADD MORE SPECIFIC ERROR MESSAGES IN FUTURE)
            if "NX" in set_options and "XX" in set_options:
                return SYNTAX_ERROR_MSG
            if len(set(set_options).intersection(TIME_OPTIONS)) > 1:
                return SYNTAX_ERROR_MSG

            # check first for XX and NX conditions are met for set operation;
            # then check for other options
            # (ALSO NEED TO IMPLEMENT FUTHER NESTED IF STATEMENTS FOR TIME OPTIONS)

            # XX only sets if key already exists; returns nil reply if set not performed
            if "XX" in set_options:
                # GET command returns pervious value if key exists or nil reply if key doesn't exist
                if "GET" in set_options:
                    if message[1] in DATA_DICT:
                        old_value_len = len(DATA_DICT[message[1]])
                        old_value = DATA_DICT[message[1]]
                        old_value_bulk_string = bulk_string_response(
                            old_value_len, old_value
                        )
                        DATA_DICT.update({message[1]: message[2]})
                        return old_value_bulk_string

                    return NIL_REPLY
                if message[1] in DATA_DICT:
                    DATA_DICT.update({message[1]: message[2]})
                    return OKAY
                return NIL_REPLY
            # NX only sets if key does not exist; returns nil reply if set not performed
            if "NX" in set_options:
                if "GET" in set_options:
                    # returns current value but does not set new value as key already existed; Get overides nil reply from NX
                    if message[1] in DATA_DICT:
                        current_value_len = len(DATA_DICT[message[1]])
                        current_value = DATA_DICT[message[1]]
                        current_value_bulk_string = bulk_string_response(
                            current_value_len, current_value
                        )
                        return current_value_bulk_string
                    # sets new key:value but returns nil as GET was used and no key:value existed previously
                    if message[1] not in DATA_DICT:
                        DATA_DICT[message[1]] = message[2]
                        return NIL_REPLY
            if "GET" in set_options:
                # returns current value but does not set new value as key already existed; Get overides nil reply from NX
                if message[1] in DATA_DICT:
                    current_value_len = len(DATA_DICT[message[1]])
                    current_value = DATA_DICT[message[1]]
                    current_value_bulk_string = bulk_string_response(
                        current_value_len, current_value
                    )
                    DATA_DICT.update({message[1]: message[2]})
                    return current_value_bulk_string
                return NIL_REPLY
        elif len(message) == 3:
            DATA_DICT[message[1]] = message[2]
            return OKAY
    return unknown_command_error_response(message)


def timeout_loop():
    while True:
        for key, value in TIME_DICT.items():
            TIME_DICT[key] -= 1
            if value <= 0:
                DATA_DICT.pop(key)
                TIME_DICT.pop(key)
        time.sleep(0.001)


if __name__ == "__main__":
    listen_and_respond()
