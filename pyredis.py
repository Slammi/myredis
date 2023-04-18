import argparse


def redis_test():
    parser = argparse.ArgumentParser(
        description="This will print a statement passed as argument",
        epilog="Why are you even reading the help page for this?",
    )

    parser.add_argument(
        "message",
        type=str,
        choices=["GET", "SET", "DEL"],
        default="You didn't input anything",
    )
    parser.add_argument("key_or_value", type=str, nargs="+")
    # parser.add_argument('--get','-g',nargs=1,type=str,help='Default get command. User input must be string')
    # parser.add_argument('--set','-s',type=str, help='Default set command. User input must be string')
    # parser.add_argument('--del','-d',help='Default delete command.')
    # parser.add_argument('--port','-p',type=int,default=6379, help='This is the default port to connect to')
    args = parser.parse_args()
    print(args.message)
    print(args.key_or_value)
    print(len(args.key_or_value))
    input_to_length = {item: len(item) for item in args.key_or_value}
    # print(input_to_length)
    # print(args.port)
    # print(args.get)

    key_or_value_num = len(args.key_or_value)
    command_length = len(args.message)
    total_length = 1 + key_or_value_num
    print(total_length)
    spacing = "\r\n"
    message_start = f"*{total_length}\r\n${command_length}\r\n"

    # print(get_length)
    client_encode = f"{message_start}"
    for key, value in input_to_length.items():
        client_encode = client_encode + f"${value}\r\n{key}\r\n"
    print(client_encode)

    # f"*{total_length}\r\n${command_length}\r\n{args.message}\r\n${argument_length}"
    # pyredis.py GET hello world
    # *3\r\n$3\r\nGET\r\n$5\r\n\hello\r\n$5\r\nworld\r\n
    # print(client_encode)


# redis_test("hello world")


if __name__ == "__main__":
    redis_test()
