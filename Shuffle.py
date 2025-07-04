import random
import time
import CalcLength

INF = 1e1000

# 以下、経路が入ったtour配列を引数として渡す
def shuffle(tour):
    return random.sample(tour, len(tour))

# 指定の時間分シャッフルし、最もよい巡回路を得る
def time_shuffle(city_list, tour, length_cashe, minuites=3):
    min_length = INF
    result_tour = []
    t_start = time.perf_counter()
    while time.perf_counter() - t_start < minuites * 60:
        tour = shuffle(tour)
        calc_length = CalcLength.calc_tour_length(city_list, tour, length_cashe)
        if min_length > calc_length:
            min_length = calc_length
            result_tour = tour
        
    return result_tour
