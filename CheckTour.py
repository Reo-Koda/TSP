import sys

def print_error(text):
    print(f"Error: { text }")
    sys.exit()

def has_duplicates(seq):
    return len(seq) != len(set(seq))

def check_tour(city_list, tour):
    if len(city_list) != len(tour):
        print_error("巡回路内の都市の数が合いません")

    if has_duplicates(tour):
        print_error("巡回路内に重複した都市があります")