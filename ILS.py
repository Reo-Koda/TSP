import time
import CalcLength
import Opt
import Kick

INF = 1e1000

# 経路が入ったtour配列を引数として渡す
def ILS(city_list_length, tour, length_cache, neighbors_rank, rank, minuites=3, interval=50):
    try_cnt = 0 # デバッグ用
    fail_cnt = 0
    min_length = CalcLength.calc_tour_length(tour, length_cache)
    weight_sum = Kick.save_weight_sum(length_cache) # 重み付きダブルブリッジ操作のために作成
    temp_tour = []
    store = tour.copy()
    store_length = min_length

    t_start = time.perf_counter()

    while time.perf_counter() - t_start < minuites * 60:
        if fail_cnt <= interval:
            temp_tour = store.copy()
        
        # キック操作
        if fail_cnt == interval:
            temp_tour = Kick.LNS_Kick(city_list_length, temp_tour, length_cache, destroy_num=int(city_list_length*0.3)) # 局所探索外へのキックに有用
            # temp_tour = Kick.scramble(temp_tour)
        else:
            temp_tour = Kick.double_bridge(temp_tour)
            # temp_tour = Kick.random_swap_section(temp_tour)
            # temp_tour = Kick.translocation(temp_tour)

        # 局所最適解の探索
        temp_tour = Opt.fast_two_or_1m(city_list_length, temp_tour, length_cache, neighbors_rank, rank)
        if fail_cnt > int(interval / 2):
            temp_tour = Opt.fast_three_or_1m(city_list_length, temp_tour, length_cache, neighbors_rank, int(rank/2))

        # 改善が長く見られなかったら、改悪を許容する
        calc_length = CalcLength.calc_tour_length(temp_tour, length_cache)
        if min_length > calc_length:
            min_length = calc_length
            tour = temp_tour.copy()
            store_length = calc_length
            store = temp_tour.copy()
            fail_cnt = 0
        elif store_length > calc_length:
            store_length = calc_length
            store = temp_tour.copy()
            if fail_cnt == interval:
                fail_cnt = 0
        elif fail_cnt == interval:
            store_length = calc_length
            store = temp_tour.copy()
            fail_cnt = 0
        else:
            fail_cnt += 1
        
        # デバッグ用
        print(f"最短経路長: {min_length:.4f}, 探索経路長: {calc_length:.4f}, 未改善回数: {fail_cnt:>2}")
        try_cnt += 1
    print(f"試行回数: { try_cnt }")
        
    return tour

# 動的に interval 変数を変化させる
def Dynamic_Interval_ILS(city_list, tour, length_cache, neighbors_rank, rank, minuites=3, interval=50):
    try_cnt = 0 # デバッグ用
    fail_cnt = 0
    init_interval = interval
    min_length = CalcLength.calc_tour_length(city_list, tour, length_cache)
    weight_sum = Kick.save_weight_sum(length_cache) # 重み付きダブルブリッジ操作のために作成
    temp_tour = []
    store = tour.copy()
    store_length = min_length

    t_start = time.perf_counter()

    while time.perf_counter() - t_start < minuites * 60:
        if fail_cnt <= interval:
            temp_tour = store.copy()
        
        # キック操作
        if fail_cnt == interval:
            temp_tour = Kick.LNS_Kick(city_list, temp_tour, length_cache, destroy_num=int(len(temp_tour)*0.3)) # 局所探索外へのキックに有用
            # temp_tour = Kick.scramble(temp_tour)
        else:
            temp_tour = Kick.double_bridge(temp_tour, length_cache, weight_sum)
            # temp_tour = Kick.random_swap_section(temp_tour)
            # temp_tour = Kick.translocation(temp_tour)

        # 局所最適解の探索
        temp_tour = Opt.fast_two_or_1m(city_list, temp_tour, length_cache, neighbors_rank, rank)
        if fail_cnt > int(interval / 2):
            temp_tour = Opt.fast_three_or_1m(city_list, temp_tour, length_cache, neighbors_rank, int(rank/2))

        # 改善が長く見られなかったら、改悪を許容する
        calc_length = CalcLength.calc_tour_length(city_list, temp_tour, length_cache)
        if min_length > calc_length:
            min_length = calc_length
            tour = temp_tour.copy()
            store_length = calc_length
            store = temp_tour.copy()
            fail_cnt = 0
            if interval < init_interval:
                interval += 5
        elif store_length > calc_length:
            store_length = calc_length
            store = temp_tour.copy()
            if fail_cnt == interval:
                fail_cnt = 0
        elif fail_cnt == interval:
            store_length = calc_length
            store = temp_tour.copy()
            fail_cnt = 0
            interval = int(interval * 0.7) if interval >= 20 else interval
            print("上限", interval)
        else:
            fail_cnt += 1
        
        # デバッグ用
        print(f"最短経路長: {min_length:.4f}, 探索経路長: {calc_length:.4f}, 未改善回数: {fail_cnt:>2}")
        try_cnt += 1
    print(f"試行回数: { try_cnt }")
        
    return tour