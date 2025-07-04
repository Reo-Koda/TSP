import random
import time
import CalcLength
import CheckTour

INF = 1e1000

# 以下、空のtour配列を引数として渡す
# 最近近傍法の実装
def nn(city_list, neighbors_rank, start=0):
    tour = []
    tour.append(start)
    for i in range(len(city_list) - 1):
        t = tour[i]
        min_cnt = 0
        while True:
            if neighbors_rank[t][min_cnt] in tour:
                min_cnt += 1
            else:
                break
        tour.append(neighbors_rank[t][min_cnt])

    return tour

# 多スタート最近近傍法の実装
def many_nn(city_list, length_cashe, neighbors_rank):
    tour = []
    min_length = INF
    for start in range(len(city_list)): # すべての都市からの結果を見る
        tmp_tour = nn(city_list, neighbors_rank, start)
        calc_length = CalcLength.calc_tour_length(city_list, tmp_tour, length_cashe)
        if min_length > calc_length:
            min_length = calc_length
            tour = tmp_tour
        # print(f"試行回数: {start}")

    return tour

# 1%の確率でより遠い都市に移動する最近近傍法(以下, ランダム最近近傍法)の実装
def rand_nn(city_list, neighbors_rank, start=0, noise_rate=0.01):
    tour = []
    tour.append(start)
    rank = len(neighbors_rank[0])
    for i in range(len(city_list) - 1):
        t = tour[i]
        min_cnt = 0
        while True:
            min_cnt = min_cnt % rank
            if neighbors_rank[t][min_cnt] in tour:
                min_cnt += 1
            elif random.random() < noise_rate:
                min_cnt += 1
            else:
                break
        tour.append(neighbors_rank[t][min_cnt])
    return tour

# 指定した時間、ランダム最近近傍法を実行し続ける
def time_rand_nn(city_list, length_cashe, neighbors_rank, noise_rate=0.01, minuites=3):
    n = len(city_list)
    tour = []
    min_length = INF
    t_start = time.perf_counter()
    while time.perf_counter() - t_start < minuites * 60:
        tmp_tour = []
        start = random.randint(0, n - 1)
        tmp_tour = rand_nn(city_list, neighbors_rank, start, noise_rate)
        calc_length = CalcLength.calc_tour_length(city_list, tmp_tour, length_cashe)
        if min_length > calc_length:
            min_length = calc_length
            tour = tmp_tour.copy()

    return tour

# 多スタートランダム最近近傍法の実装
def many_rand_nn(city_list, tour, length_cashe, neighbors_rank, noise_rate=0.01):
    min_length = INF
    for start in range(len(city_list)): # すべての都市からの結果を見る
        tmp_tour = rand_nn(city_list, neighbors_rank, start, noise_rate)
        calc_length = CalcLength.calc_tour_length(city_list, tmp_tour, length_cashe)
        if min_length > calc_length:
            min_length = calc_length
            tour = tmp_tour

    return tour

# 指定の個数分の出発地点で多スタートランダム最近近傍法の実装
def k_rand_nn(city_list, length_cashe, neighbors_rank, rank, k=3, noise_rate=0.01):
    n = len(city_list)
    if k > n - 1:
        k = n - 1
    tour = []
    min_length = INF
    for start in random.sample([x for x in range(len(city_list))], k): # k個分の都市の結果を見る
        tmp_tour = rand_nn(city_list, neighbors_rank, start, noise_rate)
        calc_length = CalcLength.calc_tour_length(city_list, tmp_tour, length_cashe)
        if min_length > calc_length:
            min_length = calc_length
            tour = tmp_tour

    return tour

# 指定した時間、多スタートランダム最近近傍法を実行し続ける
def time_many_rand_nn(city_list, tour, length_cashe, neighbors_rank, noise_rate=0.01, minuites=3):
    min_length = INF
    t_start = time.perf_counter()
    while time.perf_counter() - t_start < minuites * 60:
        tmp_tour = []
        tmp_tour = many_rand_nn(city_list, tmp_tour, length_cashe, neighbors_rank, noise_rate)
        calc_length = CalcLength.calc_tour_length(city_list, tmp_tour, length_cashe)
        if min_length > calc_length:
            min_length = calc_length
            tour = tmp_tour

    return tour

def select_two(city_list, length_cashe, neighbors_rank):
    tour = []
    max_i, max_j = 0, 0
    max_length = -1
    for i in range(len(city_list)):
        j = neighbors_rank[i][-1]
        calc_length = CalcLength.calc_straight_length(city_list, i, j, length_cashe)
        if max_length < calc_length:
            max_length = calc_length
            max_i, max_j = i, neighbors_rank[i][len(neighbors_rank[i]) - 1]
    tour.append(max_i)
    tour.append(max_j)
    return tour

# 最安挿入法の実装
def ci(city_list, length_cashe, neighbors_rank):
    # 最も遠い2都市を最小部分巡回路にする
    tour = select_two(city_list, length_cashe, neighbors_rank)

    while len(city_list) != len(tour):
        # 挿入都市と挿入辺の決定
        min_lemgth = INF
        for i in range(len(tour)):
            a = tour[i]
            b = tour[(i + 1) % len(tour)]
            for j in range(len(city_list)):
                if j in tour:
                    continue
                aj_lemgth = CalcLength.calc_straight_length(city_list, a, j, length_cashe)
                jb_lemgth = CalcLength.calc_straight_length(city_list, j, b, length_cashe)
                ab_length = CalcLength.calc_straight_length(city_list, a, b, length_cashe)
                calc_length = aj_lemgth + jb_lemgth - ab_length
                if min_lemgth > calc_length:
                    min_lemgth = calc_length
                    g, h = (i + 1) % len(tour), j
        
        tour.insert(g, h)
    
    return tour

# ランダムに選ばれた2都市を最小部分巡回路にして初期解を指定の個数生成し、最良のtour配列を返す最安挿入法
def rand_ci(city_list, length_cashe, times=4):
    tour = []
    n = len(city_list)
    min_tour = INF
    for _ in range(times):
        city1 = city2 = 0
        while city1 == city2:
            city1 = random.randint(0, n - 1)
            city2 = random.randint(0, n - 1)
        temp_tour = [city1, city2]

        while n != len(temp_tour):
            # 挿入都市と挿入辺の決定
            min_lemgth = INF
            for i in range(len(temp_tour)):
                a = temp_tour[i]
                b = temp_tour[(i + 1) % len(temp_tour)]
                for j in range(n):
                    if j in temp_tour:
                        continue
                    aj_lemgth = CalcLength.calc_straight_length(city_list, a, j, length_cashe)
                    jb_lemgth = CalcLength.calc_straight_length(city_list, j, b, length_cashe)
                    ab_length = CalcLength.calc_straight_length(city_list, a, b, length_cashe)
                    calc_length = aj_lemgth + jb_lemgth - ab_length
                    if min_lemgth > calc_length:
                        min_lemgth = calc_length
                        g, h = (i + 1) % len(temp_tour), j
            
            temp_tour.insert(g, h)
        calc_tour = CalcLength.calc_tour_length(city_list, temp_tour, length_cashe)
        if min_tour > calc_tour:
            min_tour = calc_tour
            tour = temp_tour
    return tour

# 指定した時間初期解を生成し続け、最良のtour配列を返す最安挿入法
def many_ci(city_list, tour, length_cashe, minuites=3):
    min_tour = INF
    t_start = time.perf_counter()
    while time.perf_counter() - t_start < minuites * 60:
        city1 = city2 = 0
        while city1 == city2:
            city1 = random.randint(0, len(city_list) - 1)
            city2 = random.randint(0, len(city_list) - 1)
        temp_tour = [city1, city2]

        while len(city_list) != len(temp_tour):
            # 挿入都市と挿入辺の決定
            min_lemgth = INF
            for i in range(len(temp_tour)):
                a = temp_tour[i]
                b = temp_tour[(i + 1) % len(temp_tour)]
                for j in range(len(city_list)):
                    if j in temp_tour:
                        continue
                    aj_lemgth = CalcLength.calc_straight_length(city_list, a, j, length_cashe)
                    jb_lemgth = CalcLength.calc_straight_length(city_list, j, b, length_cashe)
                    ab_length = CalcLength.calc_straight_length(city_list, a, b, length_cashe)
                    calc_length = aj_lemgth + jb_lemgth - ab_length
                    if min_lemgth > calc_length:
                        min_lemgth = calc_length
                        g, h = (i + 1) % len(temp_tour), j
            
            temp_tour.insert(g, h)
        calc_tour = CalcLength.calc_tour_length(city_list, temp_tour, length_cashe)
        if min_tour > calc_tour:
            min_tour = calc_tour
            tour = temp_tour
    return tour