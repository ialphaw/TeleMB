import ast


def is_start(info, chat_id):
    for item in info:
        if chat_id == item['chat_id']:
            if item['start']:
                return True
    return False


def read_info():
    file = open('info.txt', 'r')
    info_file = file.read()
    info = ast.literal_eval(info_file)
    print(info)
    return info


def write_info(info):
    file = open('info.txt', 'w')
    file.write(str(info))
    print(info)
