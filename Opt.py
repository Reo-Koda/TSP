import CalcLength

INF = 1e1000
EPS = 1e-9

def two_opt(city_list_length, tour, length_cache, isPrint=True):
    while True:
        cnt = 0
        max_num = -1
        for i in range(city_list_length - 3):
            j = i + 1
            for k in range(i + 2, city_list_length):
                l = (k + 1) % city_list_length
                
                a = tour[i]
                b = tour[j]
                c = tour[k]
                d = tour[l]
                ab_length = length_cache[a][b]
                cd_length = length_cache[c][d]
                ac_length = length_cache[a][c]
                bd_length = length_cache[b][d]
                calc_num = (ab_length + cd_length) - (ac_length + bd_length)
                
                if calc_num > EPS and max_num < calc_num:
                    cnt += 1
                    max_num = calc_num
                    g, h = j, k

        if cnt != 0:
            tour[g:h+1] = reversed(tour[g:h+1])
            print("-", end="", flush=True) if isPrint else None
        else:
            break

    return tour

def fast_two_opt(city_list_length, tour, length_cache, neighbors_rank, rank, isPrint=True):
    n = city_list_length
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
                ab_length = length_cache[city_a][city_b]
                cd_length = length_cache[city_c][city_d]
                ac_length = length_cache[city_a][city_c]
                bd_length = length_cache[city_b][city_d]

                calc_num = (ab_length + cd_length) - (ac_length + bd_length)

                if calc_num > EPS and calc_num > max_num:
                    cnt += 1
                    max_num = calc_num
                    g, h = j, pos[city_k]

        if cnt != 0:
            tour[g:h+1] = reversed(tour[g:h+1])
            print("-", end="", flush=True) if isPrint else None
        else:
            break

    return tour

def first_two_opt(city_list_length, tour, length_cache, isPrint=True):
    improved = True
    while improved:
        improved = False
        for i in range(city_list_length - 3):
            j = i + 1
            for k in range(i + 2, city_list_length):
                l = (k + 1) % city_list_length
                
                a = tour[i]
                b = tour[j]
                c = tour[k]
                d = tour[l]
                ab_length = length_cache[a][b]
                cd_length = length_cache[c][d]
                ac_length = length_cache[a][c]
                bd_length = length_cache[b][d]
                calc_num = (ab_length + cd_length) - (ac_length + bd_length)
                if calc_num > 0:
                    tour[j:k+1] = reversed(tour[j:k+1])
                    improved = True
                    print("-", end="", flush=True) if isPrint else None

    return tour

def DL_two_opt(city_list_length, tour, length_cache, isPrint=True):
    dont_look = [False for _ in range(city_list_length)]
    improved = True

    while improved:
        improved = False
        max_num = -1
        for i in range(city_list_length):
            if dont_look[tour[i]]:
                continue
            found_improve = False

            i_nxt = (i + 1) % city_list_length
            a = tour[i]
            b = tour[i_nxt]
            # i から何個ずらすかで for 文を回す
            for off in range(2, city_list_length - 1):
                k = (i + off) % city_list_length
                l = (k + 1) % city_list_length

                c = tour[k]
                d = tour[l]
                ab_length = length_cache[a][b]
                cd_length = length_cache[c][d]
                ac_length = length_cache[a][c]
                bd_length = length_cache[b][d]
                calc_num = (ab_length + cd_length) - (ac_length + bd_length)

                if calc_num > EPS and max_num < calc_num:
                    improved = True
                    max_num = calc_num
                    g, h = i_nxt, k

                    found_improve = True
                elif calc_num > 0:
                    found_improve = True
        
            if not found_improve:
                dont_look[tour[i]] = True

        if improved:
            city_g1 = tour[g-1]
            city_g = tour[g]
            city_h = tour[h]
            city_h1 = tour[(h + 1) % city_list_length]
            if g < h:
                tour[g:h+1] = reversed(tour[g:h+1])
            else:
                A = list(reversed(tour[g:]))
                B = tour[h+1:g]
                C = list(reversed(tour[:h+1]))
                tour[:] = A + B + C
            
            dont_look[city_g1] = False
            dont_look[city_g] = False
            dont_look[city_h] = False
            dont_look[city_h1] = False
            print("-", end="", flush=True) if isPrint else None
    return tour

def DL_first_two_opt(city_list_length, tour, length_cache, isPrint=True):
    dont_look = [False for _ in range(city_list_length)]
    improved = True

    while improved:
        improved = False
        for i in range(city_list_length):
            if dont_look[tour[i]]:
                continue
            found_improve = False

            i_nxt = (i + 1) % city_list_length
            a = tour[i]
            b = tour[i_nxt]
            # i から何個ずらすかで for 文を回す
            for off in range(2, city_list_length - 1):
                k = (i + off) % city_list_length
                l = (k + 1) % city_list_length

                c = tour[k]
                d = tour[l]
                ab_length = length_cache[a][b]
                cd_length = length_cache[c][d]
                ac_length = length_cache[a][c]
                bd_length = length_cache[b][d]
                calc_num = (ab_length + cd_length) - (ac_length + bd_length)
                
                if calc_num > 0:
                    improved = True
                    found_improve = True
                    g, h = i_nxt, k

                    city_g1 = tour[g-1]
                    city_g = tour[g]
                    city_h = tour[h]
                    city_h1 = tour[(h + 1) % city_list_length]
                    if g < h:
                        tour[g:h+1] = reversed(tour[g:h+1])
                    else:
                        A = list(reversed(tour[g:]))
                        B = tour[h+1:g]
                        C = list(reversed(tour[:h+1]))
                        tour[:] = A + B + C
                    
                    dont_look[city_g1] = False
                    dont_look[city_g] = False
                    dont_look[city_h] = False
                    dont_look[city_h1] = False
                    print("-", end="", flush=True) if isPrint else None
                    # print(CalcLength.calc_tour_length(tour, length_cache))
                    break
        
            if not found_improve:
                dont_look[tour[i]] = True

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

def calc_3opt_length(length_cache, p1, p2, q1, q2, r1, r2):
    p1p2_length = length_cache[p1][p2]
    q1q2_length = length_cache[q1][q2]
    r1r2_length = length_cache[r1][r2]
    calc_length = p1p2_length + q1q2_length + r1r2_length
    return calc_length

def three_opt(city_list_length, tour, length_cache):
    n = city_list_length
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

                    pre_length = calc_3opt_length(length_cache, a1, a2, b1, b2, c1, c2)
                    three_opt_patterns = generate_3opt_patterns(pos_a2, pos_b1, pos_b2, pos_c1, pos_c2, pos_a1)
                    for pattern in three_opt_patterns:
                        calc_length = calc_3opt_length(length_cache, tour[pattern[0]], tour[pattern[1]], tour[pattern[2]], tour[pattern[3]], tour[pattern[4]], tour[pattern[5]])
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

def fast_three_opt(city_list_length, tour, length_cache, neighbors_rank, rank, isPrint=True):
    n = city_list_length
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
                    pre_length = calc_3opt_length(length_cache, a1, a2, b1, b2, c1, c2)
                    three_opt_patterns = generate_3opt_patterns(a2_pos, b1_pos, b2_pos, c1_pos, c2_pos, a1_pos)
                    for pattern in three_opt_patterns:
                        calc_length = calc_3opt_length(length_cache, tour[pattern[0]], tour[pattern[1]], tour[pattern[2]], tour[pattern[3]], tour[pattern[4]], tour[pattern[5]])

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
        print("=", end="", flush=True) if isPrint else None

    return tour

def or_opt(city_list_length, tour, length_cache, index, isPrint=True):
    n = city_list_length
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
                ab_length = length_cache[a][b]
                pq_length = length_cache[p][q]
                rl_length = length_cache[r][l]
                ar_length = length_cache[a][r]
                qb_length = length_cache[q][b]
                pl_length = length_cache[p][l]

                calc_num = (ab_length + pq_length + rl_length) - (ar_length + qb_length + pl_length)

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
            print("-", end="", flush=True) if isPrint else None

    return tour

def fast_or_opt(city_list_length, tour, index, length_cache, neighbors_rank, rank, isPrint=True):
    n = city_list_length
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
                ab_length = length_cache[a][b]
                pq_length = length_cache[tour[pos_p]][tour[pos_q]]
                rl_length = length_cache[r][tour[pos_l]]
                ar_length = length_cache[a][r]
                qb_length = length_cache[tour[pos_q]][b]
                pl_length = length_cache[tour[pos_p]][tour[pos_l]]
                calc_length = ab_length + pq_length + rl_length - (ar_length + qb_length + pl_length)

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
            print("-", end="", flush=True) if isPrint else None

    return tour

def first_or_opt(city_list_length, tour, length_cache, index, isPrint=True):
    n = city_list_length
    improved = True
    while improved:
        improved = False
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
                ab_length = length_cache[a][b]
                pq_length = length_cache[p][q]
                rl_length = length_cache[r][l]
                ar_length = length_cache[a][r]
                qb_length = length_cache[q][b]
                pl_length = length_cache[p][l]

                calc_num = (ab_length + pq_length + rl_length) - (ar_length + qb_length + pl_length)

                if calc_num > EPS:
                    g, h = i_1, j_1

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
                    improved = True
                    print("-", end="", flush=True) if isPrint else None

    return tour

def two_or_1m(city_list_length, tour, length_cashe, m=3, isPrint=True):
    min_length = CalcLength.calc_tour_length(tour, length_cashe)
    while True:
        tour = two_opt(city_list_length, tour, length_cashe, isPrint=isPrint)
        for index in range(1, m+1):
            tour = or_opt(city_list_length, tour, length_cashe, index, isPrint=isPrint)

        tmp_length = CalcLength.calc_tour_length(tour, length_cashe)
        if min_length > tmp_length:
            min_length = tmp_length
        else:
            break
    
    return tour

def fast_two_or_1m(city_list_length, tour, length_cache, neighbors_rank, rank, m=3, isPrint=True):
    min_length = CalcLength.calc_tour_length(tour, length_cache)
    while True:
        tour = fast_two_opt(city_list_length, tour, length_cache, neighbors_rank, rank, isPrint=isPrint)
        for index in range(1, m+1):
            tour = fast_or_opt(city_list_length, tour, index, length_cache, neighbors_rank, rank, isPrint=isPrint)

        tmp_length = CalcLength.calc_tour_length(tour, length_cache)
        if min_length > tmp_length:
            min_length = tmp_length
        else:
            break
    
    return tour

def first_two_or_1m(city_list_length, tour, length_cache, m=3, isPrint=True):
    min_length = CalcLength.calc_tour_length(tour, length_cache)
    while True:
        tour = first_two_opt(city_list_length, tour, length_cache, isPrint=isPrint)
        for index in range(1, m+1):
            tour = first_or_opt(city_list_length, tour, length_cache, index, isPrint=isPrint)

        tmp_length = CalcLength.calc_tour_length(tour, length_cache)
        if min_length > tmp_length:
            min_length = tmp_length
        else:
            break
    
    return tour

def fast_three_or_1m(city_list_length, tour, length_cache, neighbors_rank, rank, m=3):
    min_length = CalcLength.calc_tour_length(tour, length_cache)
    while True:
        tour = fast_three_opt(city_list_length, tour, length_cache, neighbors_rank, rank)
        for index in range(1, m+1):
            tour = fast_or_opt(city_list_length, tour, index, length_cache, neighbors_rank, rank)

        tmp_length = CalcLength.calc_tour_length(tour, length_cache)
        if min_length > tmp_length:
            min_length = tmp_length
        else:
            break
    
    return tour