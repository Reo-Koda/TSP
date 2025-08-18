import random
import CheckTour
import CalcLength

INF = 1e1000

def random_swap(tour):
    a, b = random.sample(range(len(tour)), 2)
    tour[a], tour[b] = tour[b], tour[a]
    return tour

def random_swap_section(tour):
    a, a1, b, b1 = sorted(random.sample(range(len(tour)), 4))
    new_tour = tour[:a] + tour[b:b1 + 1] + tour[a1 + 1:b] + tour[a:a1 + 1] + tour[b1 + 1:]
    return new_tour

def random_reverse(tour):
    a, b = sorted(random.sample(range(len(tour)), 2))
    
    temp_tour = tour[a:b+1][::-1]
    new_tour = tour[:a] + temp_tour + tour[b+1:]
    return new_tour

def translocation(tour):
    n = len(tour)
    a, b = sorted(random.sample(range(n), 2))
    candidates = list(range(0, a)) + list(range(b+1, n+1))
    r = random.choice(candidates)

    temp_tour = tour[a:b+1]
    new_tour = tour[:a] + tour[b+1:]
    new_tour[r:r] = temp_tour
    return new_tour

def scramble(tour):
    a, b = sorted(random.sample(range(len(tour)), 2))
    
    temp_tour = random.sample(tour[a:b+1], b+1-a)
    new_tour = tour[:a] + temp_tour + tour[b+1:]
    return new_tour

def set_random_abcd_1(tour):
    d2 = random.randint(7, len(tour) - 1)
    d1 = d2 - 1

    c2 = random.randint(5, d1 - 1)
    c1 = c2 - 1
    
    b2 = random.randint(3, c1 - 1)
    b1 = b2 - 1

    a2 = random.randint(1, b1 - 1)
    a1 = a2 - 1
    return a1, a2, b1, b2, c1, c2, d1, d2

def set_random_abcd_2(tour):
    n = len(tour)
    while True:
        a1, b1, c1, d1 = sorted(random.sample(range(n - 1), 4))
        a2, b2, c2, d2 = a1+1, b1+1, c1+1, d1+1
        if a2 == b1 or b2 == c1 or c2 == d1:
            continue
        else:
            break
    return a1, a2, b1, b2, c1, c2, d1, d2

# 点 i からの辺の長さを重みとして、その和を保存する
def save_weight_sum(length_cache):
    n = len(length_cache)
    weight_sum = [0 for _ in range(n)]
    for i in range(n):
        weight_sum[i] = sum(length_cache[i])
    return weight_sum

def set_abcd_weighted(tour, length_cache, weight_sum):
    n = len(tour)
    samples = set()
    while len(samples) < 8:
        sum_p = 0
        r = random.random()
        for i, w in enumerate(weight_sum):
            if i+1 == n:
                continue
            p = length_cache[i][i+1] / w
            sum_p += p
            if r <= sum_p:
                samples.add(i)
                samples.add(i+1)
                break

    print(samples)
    a1, a2, b1, b2, c1, c2, d1, d2 = sorted(samples)
    return a1, a2, b1, b2, c1, c2, d1, d2
    
def double_bridge(tour):
    # a1, a2, b1, b2, c1, c2, d1, d2 = set_random_abcd_1(tour) # 偏りが激しい
    a1, a2, b1, b2, c1, c2, d1, d2 = set_random_abcd_2(tour) # 試行回数が少なくなる
    # a1, a2, b1, b2, c1, c2, d1, d2 = set_abcd_weighted(tour, length_cache, weight_sum)
    # print(a1, a2, b1, b2, c1, c2, d1, d2)

    temp_tour = []
    for i in range(c2, d1 + 1):
        temp_tour.append(tour[i])
    for i in range(b2, c1 + 1):
        temp_tour.append(tour[i])
    for i in range(a2, b1 + 1):
        temp_tour.append(tour[i])
    for i in range(d2, a1 + 1 + len(tour)):
        temp_tour.append(tour[i % len(tour)])
    
    return temp_tour

# LNS(大規模近傍探索)特有のキック操作
def destroy(city_list_length, tour, destroy_num):
    n = city_list_length
    removed_indices = set(random.sample(range(n), destroy_num))
    partial = [tour[i] for i in range(n) if i not in removed_indices]
    removed = [tour[i] for i in removed_indices]
    return partial, removed

# 貪欲最小挿入修復
def greedy_repair(city_list_length, tour, length_cache, removed):
    tour_size = len(tour)
    while city_list_length != tour_size:
        # 挿入都市と挿入辺の決定
        min_lemgth = INF
        for i in range(tour_size):
            a = tour[i]
            b = tour[(i + 1) % tour_size]
            for j in removed:
                aj_lemgth = length_cache[a][j]
                jb_lemgth = length_cache[j][b]
                ab_length = length_cache[a][b]
                calc_length = aj_lemgth + jb_lemgth - ab_length
                if min_lemgth > calc_length:
                    min_lemgth = calc_length
                    g, h = (i + 1) % tour_size, j
        
        tour.insert(g, h)
        removed.remove(h)
        tour_size += 1
    
    return tour

# 後悔挿入修復
def regret_repair(city_list, tour, length_cache, removed, k=2):
    c_len = len(city_list)
    while c_len != len(tour):
        # 挿入コストの保存リストの初期化
        removed_cost = [[0 for _ in range(c_len)] for _ in range(len(removed))]
        # 挿入都市と挿入辺の決定
        for i in range(len(tour)):
            a = tour[i]
            b = tour[(i + 1) % len(tour)]

            # 挿入コストの計算
            j_cnt = 0
            for j in removed:
                aj_lemgth = CalcLength.calc_straight_length(city_list, a, j, length_cache)
                jb_lemgth = CalcLength.calc_straight_length(city_list, j, b, length_cache)
                ab_length = CalcLength.calc_straight_length(city_list, a, b, length_cache)
                calc_length = aj_lemgth + jb_lemgth - ab_length
                removed_cost[i][j_cnt] = calc_length
                j_cnt += 1

        
        
        # tour.insert(g, h)
        # removed.remove(h)
    
    return tour

def LNS_Kick(city_list_length, tour, length_cache, destroy_num):
    partial, removed = destroy(city_list_length, tour, destroy_num)
    tour = greedy_repair(city_list_length, partial, length_cache, removed)
    return tour

def kick(tour, kicknum):
    r = random.random()
    if r < 0.1:
        tour = random_swap_section(tour)
    #     tour = scramble(tour)
    # elif r < 0.3:
    else:
        tour = double_bridge(tour)


    return tour