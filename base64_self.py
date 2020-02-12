def __get_byte64_char(byte):
    if byte < 0:
        pass
    if byte < 26:
        return chr(ord("A") + byte)
    elif byte < 52:
        return chr(ord("a") + byte - 26)
    elif byte < 62:
        return chr(ord("0") + byte - 52)
    elif byte == 62:
        return "+"
    elif byte == 63:
        return "/"
    elif byte == 64:
        return "="

def __get_byte_list(file_name):
    res = None
    with open(file_name, "rb") as f:
        res = f.read()
    return list(res)

def encode_to_base64(byte_list):
    res = []

    curr_byte = 0
    curr_fill_of_byte = 0

    for i in byte_list:
        shift_point = 2 + curr_fill_of_byte
        curr_byte += i >> shift_point
        res.append(__get_byte64_char(curr_byte))

        curr_byte = (i << 6 - shift_point) % 0b1000000
        curr_fill_of_byte = shift_point

        if curr_fill_of_byte == 6:
            res.append(__get_byte64_char(curr_byte))

            curr_fill_of_byte = 0
            curr_byte = 0
    
    if curr_fill_of_byte > 0:
        res.append(__get_byte64_char(curr_byte))
        for i in range(0, (6 - curr_fill_of_byte) // 2):
            res.append(__get_byte64_char(64))
    return "".join(res)


def main(file_list):
    for f_name in file_list:
        byte_list = __get_byte_list(f_name)
        print(encode_to_base64(byte_list))
        


if __name__ == "__main__":
    filels = ["hymn.txt"]#, "wiki.txt", "quest_ansv.txt"]
    main(filels)