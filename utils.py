SEPARATOR = "\r\n"
ARRAY_START = "*"
BULK_STR_START = "$"
BUFFER_SIZE = 1024
ARRAY_ERROR_MESSAGE = "Additional input required"
# GET_TOO_MUCH_INPUT_ERROR = "-ERR unknown command" f"{message[2:]}"
MY_DICT = {}
NIL_REPLY = "$-1\r\n"
OKAY = "+OK\r\n"
PORT = 65429

import argparse, socket


def server_response_decode(message):
    # splits message into list after removing 1st character (ie. *, +, -, :,ect) on \r\n.
    # message_parts[0] = 1st section w/o 1st character and the message_parts[1] = the entire rest of the message.
    message_parts = message[1:].split(SEPARATOR, maxsplit=1)

    # Array if statement start
    if message[0] == ARRAY_START:
        array_len = int(message_parts[0])
        array_list = []

        # The rest of the message split from start of function OR what remains after each iteration through the function.
        remainder = message_parts[1]

        # for loop based on the number of elements provided in the array.
        # takes first part of message and decodes into hooman. Transfers the rest of the message into remainder.
        # array_list at end will contain each decoded part into hooman.
        for _ in range(array_len):
            value, remainder = server_response_decode(remainder)
            array_list.append(value)
        return array_list, remainder

    elif message[0] == "+":
        # print("simple string")
        value = message_parts[0]
        remainder = message_parts[1]

    elif message[0] == "-":
        # print("error")
        value = f"(error) {message_parts[0]}"
        remainder = message_parts[1]

    elif message[0] == BULK_STR_START:  # remember nil responses are sent as $-1
        # print("bulk string")
        b_string_len = int(message_parts[0])
        if b_string_len == -1:
            value = "(nil)"
            remainder = message_parts[1]
        else:
            value = message_parts[1][:b_string_len]
            remainder = message_parts[1][b_string_len + 2 :]

    elif message[0] == ":":  # responses should start with '(integer)'
        # print("integer")
        value = f"(integer) {message_parts[0]}"
        remainder = message_parts[1]
    return value, remainder


def generate_redis_formatted_array(key_or_value, cli_message):
    # Generates start of array taking length of list based on number of arguments passed to it.
    command_length = len(cli_message)
    total_length = 1 + len(key_or_value)
    encoded_message_start = f"{ARRAY_START}{total_length}{SEPARATOR}{BULK_STR_START}{command_length}{SEPARATOR}{cli_message}{SEPARATOR}"

    # Creates and returns redis formatted array to send to Redis server
    for key in key_or_value:
        encoded_message_start += (
            f"{BULK_STR_START}{len(key)}{SEPARATOR}{key}{SEPARATOR}"
        )
    return encoded_message_start


def command_handler(message, dict):
    # generates bulk string, simple string, null reply and integer reply.
    if type(message) != list:
        return f"-ERR unkown command {*message,}{SEPARATOR}"
    if message[0] == "GET":
        if len(message) > 2:
            return f"-ERR unkown command {*message[2:],}{SEPARATOR}"
        elif message[1] not in dict:
            return NIL_REPLY
        elif message[1] in dict:
            value_len = len(dict[message[1]])
            return f"${value_len}{SEPARATOR}{dict[message[1]]}{SEPARATOR}"
    if message[0] == "DEL":
        count = 0
        del_len = len(message) - 1
        for i in range(del_len):
            if message[i + 1] in dict:
                del dict[message[i + 1]]
                count += 1
        return f":{count}{SEPARATOR}"
    if message[0] == "SET":
        if len(message) >= 4:
            if message[3] == "GET":
                if message[1] in dict:
                    old_key_len = len(dict[message[1]])
                    old_key = dict[message[1]]
                    old_key_BS = f"${old_key_len}{SEPARATOR}{old_key}{SEPARATOR}"
                    dict.update({message[1]: message[2]})
                    return old_key_BS
                else:
                    dict[message[1]] = message[2]
                    return NIL_REPLY
            if message[3] == "NX":
                if message[1] in dict:
                    return NIL_REPLY
                else:
                    dict[message[1]] = message[2]
                    return OKAY
            if message[3] == "XX":
                if message[1] in dict:
                    dict.update({message[1]: message[2]})
                    return OKAY
                else:
                    return NIL_REPLY
        elif len(message) == 3:
            if message[1] in dict:
                dict.update({message[1]: message[2]})
                return OKAY
            else:
                dict[message[1]] = message[2]
                return OKAY
    return f"-ERR unknown command '{' '.join(message)}'{SEPARATOR}"


# this will likely need to be updated as other message types arise, however given
# that command_handler already converts most of replies into RESP format this is not needed currently
# may consider transfering this part into command_handler if other types dont arise.
def server_response_encode(cmd_hndlr_message):
    if type(cmd_hndlr_message) == int:
        return f":{cmd_hndlr_message}\r\n"
    else:
        return cmd_hndlr_message
