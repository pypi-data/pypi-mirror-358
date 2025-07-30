def get_data(data: str, start: str, end: str, data_les: int):
    # data = "303030314203022B30303030303030314203022B30303030"
    # start = "02"
    # end = "03"
    # data_les = 12 * 2
    data_les = int(data_les)
    if len(data) < data_les:
        return None
    #
    for i in range(0, len(data) - int(data_les), 2):
        if data[i:i + 2] == start:
            if data[i + data_les - 2:i + data_les] == end:
                return data[i:i + data_les]
    #
    return None


if __name__ == '__main__':
    print(get_data("", "", "", 1))
