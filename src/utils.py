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


def index_finder(info, chat_id):
    for group in info:
        if chat_id == group['chat_id']:
            return info.index(group)


def time_convert(time_string):
    time_list = time_string.split(":")
    hour = int(time_list[0])
    minute = int(time_list[1])
    try:
        second = time_list[2]
    except:
        second = "00"
    hour += 2
    minute += 30
    if hour > 24:
        hour -= 24
    if minute > 60:
        minute -= 60

    def sTurn(variable):
        if variable < 10:
            return f"0{variable}"
        else:
            return f"{variable}"

    fHour = sTurn(hour)
    fMinute = sTurn(minute)
    final = f"{fHour}:{fMinute}:{second}"

    return final
