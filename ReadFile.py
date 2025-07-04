def read_file(path):
    canRead = False
    city_list = []

    with open(path, "r") as file_object:
        for line in file_object:
            if line.strip() == "EOF":
                canRead = False
            if canRead:
                _, a, b = map(float, line.strip().split())
                city_list.append([a, b])
            if line.strip() == "NODE_COORD_SECTION":
                canRead = True

    return city_list
