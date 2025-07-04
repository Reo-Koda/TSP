import CalcLength
import CheckTour
import Kick

INF = 1e1000

def two_opt(city_list, tour, length_cashe):
    while True:
        cnt = 0
        max_num = -1
        for i in range(len(tour) - 3):
            j = i + 1
            for k in range(i + 2, len(tour)):
                l = (k + 1) % len(tour)
                
                a = tour[i]
                b = tour[j]
                c = tour[k]
                d = tour[l]
                ab_length = CalcLength.calc_straight_length(city_list, a, b, length_cashe)
                cd_length = CalcLength.calc_straight_length(city_list, c, d, length_cashe)
                ac_length = CalcLength.calc_straight_length(city_list, a, c, length_cashe)
                bd_length = CalcLength.calc_straight_length(city_list, b, d, length_cashe)
                calc_num = (ab_length + cd_length) - (ac_length + bd_length)
                EPS = 1e-9
                if calc_num > EPS and max_num < calc_num:
                    cnt += 1
                    max_num = calc_num
                    g, h = j, k

        if cnt != 0:
            tour[g:h+1] = reversed(tour[g:h+1])
            print("-", end="", flush=True)
        else:
            break

    return tour

def fast_two_opt(city_list, tour, length_cache, neighbors_rank, rank):
    n = len(tour)
    pos = [0] * n
    
    while True:
        for i, city in enumerate(tour):
            pos[city] = i
        cnt = 0
        max_num = -1
        for i in range(n):
            j = (i + 1) % n
            city_a = tour[i]
            city_b = tour[j]
            for city_k in neighbors_rank[city_a][:rank]: # 上位 rank 個の都市で探索
                l = (pos[city_k] + 1) % n

                if l == i or j >= pos[city_k]:
                    continue
                
                city_c = city_k
                city_d = tour[l]
                ab_length = CalcLength.calc_straight_length(city_list, city_a, city_b, length_cache)
                cd_length = CalcLength.calc_straight_length(city_list, city_c, city_d, length_cache)
                ac_length = CalcLength.calc_straight_length(city_list, city_a, city_c, length_cache)
                bd_length = CalcLength.calc_straight_length(city_list, city_b, city_d, length_cache)

                calc_num = (ab_length + cd_length) - (ac_length + bd_length)
                EPS = 1e-9
                if calc_num > EPS and calc_num > max_num:
                    cnt += 1
                    max_num = calc_num
                    g, h = j, pos[city_k]

        if cnt != 0:
            tour[g:h+1] = reversed(tour[g:h+1])
            # print(CalcLength.calc_tour_length(city_list, tour, length_cache))
            print("-", end="", flush=True)
        else:
            break

    return tour

def generate_3opt_patterns(a1, a2, b1, b2, c1, c2):
    # i1->j, j1->k, k1->i の組み合わせ
    #   A      B      C
    patterns = []
    # pattern 1. A C B
    patterns.append([a2, c1, c2, b1, b2, a1, 1])
    # pattern 2. A C(reverse) B
    patterns.append([a2, c2, c1, b1, b2, a1, 2])
    # pattern 3. A C B(reverse)
    patterns.append([a2, c1, c2, b2, b1, a1, 3])
    # pattern 4. A C(reverse) B(reverse)
    patterns.append([a2, c2, c1, b2, b1, a1, 4])
    # pattern 5. A B(reverse) C
    patterns.append([a2, b2, b1, c1, c2, a1, 5])
    # pattern 6. A B C(reverse)
    patterns.append([a2, b1, b2, c2, c1, a1, 6])
    # pattern 7. A B(reverse) C(reverse)
    patterns.append([a2, b2, b1, c2, c1, a1, 7])

    return patterns

def calc_3opt_length(city_list, length_cache, p1, p2, q1, q2, r1, r2):
    p1p2_length = CalcLength.calc_straight_length(city_list, p1, p2, length_cache)
    q1q2_length = CalcLength.calc_straight_length(city_list, q1, q2, length_cache)
    r1r2_length = CalcLength.calc_straight_length(city_list, r1, r2, length_cache)
    calc_length = p1p2_length + q1q2_length + r1r2_length
    return calc_length

def three_opt(city_list, tour, length_cache):
    n = len(tour)
    while True:
        cnt = 0
        p_num = 0
        max_length = -1
        A, B, C = [], [], []
        for pos_a1 in range(n - 5):
            for pos_b1 in range(pos_a1 + 2, n - 3):
                for pos_c1 in range(pos_b1 + 2, n - 1):
                    pos_a2, pos_b2, pos_c2 = pos_a1 + 1, pos_b1 + 1, pos_c1 + 1
                    a1 = tour[pos_a1]
                    a2 = tour[pos_a2]
                    b1 = tour[pos_b1]
                    b2 = tour[pos_b2]
                    c1 = tour[pos_c1]
                    c2 = tour[pos_c2]

                    pre_length = calc_3opt_length(city_list, length_cache, a1, a2, b1, b2, c1, c2)
                    three_opt_patterns = generate_3opt_patterns(pos_a2, pos_b1, pos_b2, pos_c1, pos_c2, pos_a1)
                    for pattern in three_opt_patterns:
                        calc_length = calc_3opt_length(city_list, length_cache, tour[pattern[0]], tour[pattern[1]], tour[pattern[2]], tour[pattern[3]], tour[pattern[4]], tour[pattern[5]])
                        if pre_length > calc_length:
                            if max_length < pre_length - calc_length:
                                cnt += 1
                                max_length = pre_length - calc_length
                                p_num = pattern[6]

                                A = tour[pos_a2:pos_b2]
                                B = tour[pos_b2:pos_c2]
                                C = tour[pos_c2:] + tour[:pos_a2]
        
        if cnt == 0:
            break

        if p_num == 1:
            new_tour = A + C + B
        elif p_num == 2:
            new_tour = A + C[::-1] + B
        elif p_num == 3:
            new_tour = A + C + B[::-1]
        elif p_num == 4:
            new_tour = A + C[::-1] + B[::-1]
        elif p_num == 5:
            new_tour = A + B[::-1] + C
        elif p_num == 6:
            new_tour = A + B + C[::-1]
        elif p_num == 7:
            new_tour = A + B[::-1] + C[::-1]
        else:
            new_tour = []

        tour[:] = new_tour
        # print(CalcLength.calc_tour_length(city_list, tour, length_cache))

    return tour

def fast_three_opt(city_list, tour, length_cache, neighbors_rank, rank):
    n = len(tour)
    pos = [0] * n

    while True:
        for i, city in enumerate(tour):
            pos[city] = i
        cnt = 0
        p_num = 0
        max_length = -1
        A, B, C = [], [], []
        for a1_pos in range(n):
            a2_pos = (a1_pos + 1) % n
            a1 = tour[a1_pos]
            a2 = tour[a2_pos]
            for b1 in neighbors_rank[tour[a1_pos]][:rank]:
                b1_pos = pos[b1]
                b2_pos = (pos[b1] + 1) % n
                b1 = tour[b1_pos]
                b2 = tour[b2_pos]
                for c1 in neighbors_rank[tour[a2_pos]][:rank]:
                    c1_pos = pos[c1]
                    c2_pos = (pos[c1] + 1) % n

                    # 順序チェック
                    if not (a1_pos < a2_pos < b1_pos < b2_pos < c1_pos < c2_pos):
                        continue

                    c1 = tour[c1_pos]
                    c2 = tour[c2_pos]
                    pre_length = calc_3opt_length(city_list, length_cache, a1, a2, b1, b2, c1, c2)
                    three_opt_patterns = generate_3opt_patterns(a2_pos, b1_pos, b2_pos, c1_pos, c2_pos, a1_pos)
                    for pattern in three_opt_patterns:
                        calc_length = calc_3opt_length(city_list, length_cache, tour[pattern[0]], tour[pattern[1]], tour[pattern[2]], tour[pattern[3]], tour[pattern[4]], tour[pattern[5]])
                        EPS = 1e-9
                        if pre_length - calc_length > EPS and pre_length - calc_length > max_length:
                            cnt += 1
                            max_length = pre_length - calc_length
                            p_num = pattern[6]

                            A = tour[a2_pos:b2_pos]
                            B = tour[b2_pos:c2_pos]
                            C = tour[c2_pos:] + tour[:a2_pos]
        
        if cnt == 0:
            break

        if p_num == 1:
            new_tour = A + C + B
        elif p_num == 2:
            new_tour = A + C[::-1] + B
        elif p_num == 3:
            new_tour = A + C + B[::-1]
        elif p_num == 4:
            new_tour = A + C[::-1] + B[::-1]
        elif p_num == 5:
            new_tour = A + B[::-1] + C
        elif p_num == 6:
            new_tour = A + B + C[::-1]
        elif p_num == 7:
            new_tour = A + B[::-1] + C[::-1]
        else:
            new_tour = []

        tour[:] = new_tour
        # print(CalcLength.calc_tour_length(city_list, tour, length_cache))
        print("=", end="", flush=True)

    return tour

def or_opt(city_list, tour, length_cache, index):
    n = len(tour)
    improved = True
    while improved:
        improved = False
        max_num = -1
        for i in range(n):
            i_1 = (i + 1) % n
            for j in range(i + 2, i - 1 + n - index):
                j_0 = j % n
                j_1 = (j + 1) % n
                j_index = (j + index) % n
                j_index1 = (j + index + 1) % n
                
                a = tour[i]
                b = tour[i_1]
                p = tour[j_0]
                q = tour[j_1]
                r = tour[j_index]
                l = tour[j_index1]
                ab_length = CalcLength.calc_straight_length(city_list, a, b, length_cache)
                pq_length = CalcLength.calc_straight_length(city_list, p, q, length_cache)
                rl_length = CalcLength.calc_straight_length(city_list, r, l, length_cache)
                ar_length = CalcLength.calc_straight_length(city_list, a, r, length_cache)
                qb_length = CalcLength.calc_straight_length(city_list, q, b, length_cache)
                pl_length = CalcLength.calc_straight_length(city_list, p, l, length_cache)

                calc_num = (ab_length + pq_length + rl_length) - (ar_length + qb_length + pl_length)
                EPS = 1e-9
                if calc_num > EPS and calc_num > max_num:
                    max_num = calc_num
                    g, h = i_1, j_1
                    improved = True


        if improved:
            tmp_tour = []
            for k in range(h, h + index):
                tmp_tour.append(tour[k % n])

            k = h
            while True:
                tour[k % n] = tour[(k + index) % n]
                k += 1
                if ((k + index) % n == g % n):
                    break
            
            k = (g - index + n) % n
            tmp_cnt = len(tmp_tour)
            while True:
                tmp_cnt -= 1
                tour[k % n] = tmp_tour[tmp_cnt]
                k += 1
                if tmp_cnt == 0:
                    break
            print("-", end="", flush=True)

    return tour

def fast_or_opt(city_list, tour, index, length_cache, neighbors_rank, rank):
    n = len(tour)
    pos = [0] * n
    improved = True
    while improved:
        improved = False
        max_num = -1
        for i, city in enumerate(tour):
            pos[city] = i
        # ① 各辺 (a→b) について
        for i in range(n):
            i_1 = (i + 1) % n
            a, b = tour[i], tour[i_1]

            # ② 挿入先候補 r を「a の近傍 rank 件」から選ぶ
            for r in neighbors_rank[a][:rank]:
                pos_l = (pos[r] + 1) % n
                pos_p = (pos[r] - index + n) % n
                pos_q = (pos_p + 1) % n
                # 順序チェック
                if   i < i_1 and i_1 < pos_p and pos_p < pos_q and pos_q < pos[r] and pos[r] < pos_l:
                    pass
                elif i_1 < pos_p and pos_p < pos_q and pos_q < pos[r] and pos[r] < pos_l and pos_l < i:
                    pass
                elif pos_p < pos_q and pos_q < pos[r] and pos[r] < pos_l and pos_l < i and i < i_1:
                    pass
                elif pos_q < pos[r] and pos[r] < pos_l and pos_l < i and i < i_1 and i_1 < pos_p:
                    pass
                elif pos[r] < pos_l and pos_l < i and i < i_1 and i_1 < pos_p and pos_p < pos_q:
                    pass
                elif pos_l < i and i < i_1 and i_1 < pos_p and pos_p < pos_q and pos_q < pos[r]:
                    pass
                else:
                    continue

                # ここで距離差 Δ を計算して改善なら実行
                ab_length = CalcLength.calc_straight_length(city_list, a, b, length_cache)
                pq_length = CalcLength.calc_straight_length(city_list, tour[pos_p], tour[pos_q], length_cache)
                rl_length = CalcLength.calc_straight_length(city_list, r, tour[pos_l], length_cache)
                ar_length = CalcLength.calc_straight_length(city_list, a, r, length_cache)
                qb_length = CalcLength.calc_straight_length(city_list, tour[pos_q], b, length_cache)
                pl_length = CalcLength.calc_straight_length(city_list, tour[pos_p], tour[pos_l], length_cache)
                calc_length = ab_length + pq_length + rl_length - (ar_length + qb_length + pl_length)
                EPS = 1e-9
                if calc_length > EPS and calc_length > max_num:
                    max_num = calc_length
                    improved = True
                    g, h = i_1, pos_q

        if improved:
            tmp_tour = []
            for k in range(h, h + index):
                tmp_tour.append(tour[k % n])

            k = h
            while True:
                tour[k % n] = tour[(k + index) % n]
                k += 1
                if ((k + index) % n == g % n):
                    break
            
            k = (g - index + n) % n
            tmp_cnt = len(tmp_tour)
            while True:
                tmp_cnt -= 1
                tour[k % n] = tmp_tour[tmp_cnt]
                k += 1
                if tmp_cnt == 0:
                    break
            # print(CalcLength.calc_tour_length(city_list, tour, length_cache))
            print("-", end="", flush=True)

    return tour

def two_or_1m(city_list, tour, length_cashe, m=3):
    min_length = CalcLength.calc_tour_length(city_list, tour, length_cashe)
    while True:
        tour = two_opt(city_list, tour, length_cashe)
        for index in range(1, m+1):
            tour = or_opt(city_list, tour, length_cashe, index)

        tmp_length = CalcLength.calc_tour_length(city_list, tour, length_cashe)
        if min_length > tmp_length:
            min_length = tmp_length
        else:
            break
    
    return tour

def fast_two_or_1m(city_list, tour, length_cache, neighbors_rank, rank, m=3):
    min_length = CalcLength.calc_tour_length(city_list, tour, length_cache)
    while True:
        tour = fast_two_opt(city_list, tour, length_cache, neighbors_rank, rank)
        for index in range(1, m+1):
            tour = fast_or_opt(city_list, tour, index, length_cache, neighbors_rank, rank)

        tmp_length = CalcLength.calc_tour_length(city_list, tour, length_cache)
        if min_length > tmp_length:
            min_length = tmp_length
        else:
            break
    
    return tour

def fast_three_or_1m(city_list, tour, length_cache, neighbors_rank, rank, m=3):
    min_length = CalcLength.calc_tour_length(city_list, tour, length_cache)
    while True:
        tour = fast_three_opt(city_list, tour, length_cache, neighbors_rank, rank)
        for index in range(1, m+1):
            tour = fast_or_opt(city_list, tour, index, length_cache, neighbors_rank, rank)

        tmp_length = CalcLength.calc_tour_length(city_list, tour, length_cache)
        if min_length > tmp_length:
            min_length = tmp_length
        else:
            break
    
    return tour