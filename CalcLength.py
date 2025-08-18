import math

def calc_straight_length(city_list, pre, next, length_cache):
    if length_cache[pre][next] == -1:
        dx = city_list[pre][0] - city_list[next][0]
        dy = city_list[pre][1] - city_list[next][1]
        # 厳密に距離を計算する際は下3行をコメントアウトすること
        # raw = math.hypot(dx, dy)
        # dist = int(raw + 0.5)
        # length_cache[pre][next] = length_cache[next][pre] = dist
        length_cache[pre][next] = length_cache[next][pre] = math.hypot(dx, dy)
    return length_cache[pre][next]

def calc_tour_length(tour, length_cache):
    total = 0
    for i in range(len(tour)):
        cur = tour[i]
        nxt = tour[(i + 1) % len(tour)]
        total += length_cache[cur][nxt]
    return total
