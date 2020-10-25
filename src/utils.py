def is_start(info, chat_id):
    for item in info:
        if chat_id == item['chat_id']:
            if item['start']:
                return True
    return False
