SEPARATOR = "\r\n"


def server_response_decode(message):
    # splits message into list after removing 1st character (ie. *, +, -, :,ect) on \r\n.
    # message_parts[0] = 1st section w/o 1st character and the message_parts[1] = the entire rest of the message.
    message_parts = message[1:].split(SEPARATOR, maxsplit=1)

    # Array if loop start
    if message[0] == "*":
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
        print("simple string")
        value = message_parts[0]
        remainder = message_parts[1]

    elif message[0] == "-":
        print("error")
        value = message_parts[0]
        remainder = message_parts[1]

    elif message[0] == "$":  # remember nil responses are sent as $-1
        print("bulk string")
        if message_parts[0] == "-1":
            value = "(nil)"
            remainder = message_parts[1]
        else:
            b_string_len = int(message_parts[0])
            value = message_parts[1][:b_string_len]
            remainder = message_parts[1][b_string_len + 1 :]

    elif message[0] == ":":  # responses should start with '(integer)'
        print("integer")
        value = int(message_parts[0])
        remainder = message_parts[1]
    return value, remainder
