import os
import math
import random
import ReadFile
import time
import CalcLength
import Gready
import Opt
import GA
import ACO
import ILS
import Result

def print_result_only(city_list, tour, length_cashe, text):
    print(f"{ text }", end=' ')
    _ = Result.result(city_list, tour, length_cashe, False)
    tour.clear()
    return tour

def main():
    basename = input("読み込む TSP ファイル名を拡張子なしで入力してください（例: att48）: ")
    city_list = []
    city_list_length = 0
    if basename != "shuffle":
        dir_name  = f"{basename}.tsp"
        file_name = f"{basename}.tsp"
        path = os.path.join(".", "ALL_tsp", dir_name, file_name)
        city_list = ReadFile.read_file(path)
        city_list_length = len(city_list)
    else:
        city_list_length = int(input("都市数を入力してください: "))
        random.seed(0)
        while len(city_list) != city_list_length:
            x = random.randint(0, city_list_length)
            y = random.randint(0, city_list_length)
            if not [x, y] in city_list:
                city_list.append([x, y])

    # 高速化のため、都市間の距離の計算結果を保存する
    length_cache = [[-1] * city_list_length for _ in range(city_list_length)]
    # 事前に距離を計算する場合に使用
    for i in range(city_list_length):
        for j in range(i + 1, city_list_length):
            _ = CalcLength.calc_straight_length(city_list, i, j, length_cache)
        print(f"都市{ i }の計算終了") if city_list_length > 5000 else None
    # 各都市に対して近い都市の順番を保存
    neighbors_rank = []
    rank = int(10 * math.log2(city_list_length))
    if rank > city_list_length:
        rank = int(city_list_length / 2)
    for i in range(city_list_length):
        neighbors = sorted(range(city_list_length), key=lambda j: length_cache[i][j])
        neighbors_rank.append(neighbors[1:])
        print(f"都市{ i }のソート完了") if city_list_length > 5000 else None

    print("実行時間計測開始")
    start = time.perf_counter()

    # 構築法
    tour = Gready.nn(city_list_length, neighbors_rank)
    # tour = Gready.time_rand_nn(city_list_length, length_cache, neighbors_rank, minuites=1)
    # tour = Gready.k_rand_nn(city_list_length, length_cache, neighbors_rank, k=100, noise_rate=0.01)
    # tour = print_result_only(city_list, tour, length_cache, "k_rand_nn")
    # tour = Gready.time_many_rand_nn(city_list, length_cache, neighbors_rank)
    # tour = Gready.ci(city_list_length, length_cache, neighbors_rank)
    # tour = print_result_only(city_list, tour, length_cache, "ci")
    # tour = Gready.rand_ci(city_list_length, tour, length_cache)
    # tour = print_result_only(city_list, tour, length_cache, "rand_ci")
    # tour = Gready.many_ci(city_list_length, length_cache)
    # tour = print_result_only(city_list, tour, length_cache, "many_ci")
    # tour = GA.GA(
    #     city_list,
    #     city_list_length,
    #     length_cache,
    #     neighbors_rank,
    #     rank,
    #     pop_size=50,
    #     generations=100,
    #     minuites=60,
    #     elite_size=4,
    #     tournament_size=6,
    #     mutation_rate=0.05,
    #     animate=True,
    #     pause_time=0.01
    # )
    # tour = print_result_only(city_list, tour, length_cache, "GA")
    # tour = ACO.ACO(
    #     city_list_length,
    #     length_cache,
    #     neighbors_rank,
    #     rank,
    #     times=100,
    #     ants_num=100,
    #     alpha=1.0,
    #     beta=5.0,
    #     rho=0.3,
    #     Q=100.0
    # )
    # tour = ACO.multi_ACO(
    #     city_list_length,
    #     length_cache,
    #     neighbors_rank,
    #     rank,
    #     times=10000*city_list_length,
    #     minuites=30,
    #     ants_num=city_list_length,
    #     alpha=1.0,
    #     beta=2.0,
    #     rho=0.9,
    #     Q=100.0
    # )
    # tour = print_result_only(city_list, tour, length_cache, "multi_ACO")
    # tour = ACO.ACS(
    #     city_list_length,
    #     length_cache,
    #     neighbors_rank,
    #     rank,
    #     times=10000*city_list_length,
    #     minuites=30,
    #     ants_num=city_list_length,
    #     alpha=1.0,
    #     beta=10.0,
    #     rho_global=0.9,
    #     rho_local=0.9,
    #     Q=100.0,
    #     isPrint=True
    # )
    # tour = ACO.MMAS(
    #     city_list_length,
    #     length_cache,
    #     neighbors_rank,
    #     rank,
    #     times=1000*city_list_length,
    #     minuites=15,
    #     ants_num=city_list_length,
    #     alpha=1.0,
    #     beta=2.0,
    #     delta=0.5,
    #     rho=0.98,
    #     Q=1.0,
    #     p_best=0.05,
    #     isPrint=True
    # )
    # tour = print_result_only(city_list, tour, length_cache, "MMAS")

    print("構築後", end='     ')
    base_length = Result.result(city_list, tour, length_cache, isShow=False)

    # 改善法
    # tour = Opt.two_opt(city_list_length, tour, length_cache, isPrint=True)
    # tour = Opt.first_two_opt(city_list_length, tour, length_cache, isPrint=True)
    # tour = Opt.DL_two_opt(city_list_length, tour, length_cache, isPrint=True)
    # tour = Opt.DL_first_two_opt(city_list_length, tour, length_cache, isPrint=True)
    # tour = Opt.fast_two_opt(city_list_length, tour, length_cache, neighbors_rank, rank, isPrint=True)

    # tour = Opt.first_two_or_1m(city_list_length, tour, length_cache, m=3, isPrint=True)
    # tour = Opt.fast_two_or_1m(city_list_length, tour, length_cache, neighbors_rank, rank, isPrint=True)
    # tour = Opt.fast_three_or_1m(city_list_length, tour, length_cache, neighbors_rank, rank)
    tour = ILS.ILS(city_list_length, tour, length_cache, neighbors_rank, rank, minuites=5, interval=50)
    # tour = ILS.Dynamic_Interval_ILS(city_list, tour, length_cache, neighbors_rank, rank, minuites=3, interval=50)

    print()
    print("改善後    ", end=' ')
    improved_length = Result.result(city_list, tour, length_cache, isShow=False)

    end = time.perf_counter()
    if basename == "shuffle":
        print(f"実行時間計測終了 { basename }{ city_list_length }")
    else:
        print(f"実行時間計測終了 { basename }")

    print(f"実行時間: {end - start:.2f}sec")

    # 改善評価
    if base_length >= improved_length:
        improved_rate = (base_length - improved_length) / base_length * 100
        print(f"改善評価: {improved_rate:.2f}% 改善")
    else:
        improved_rate = (improved_length - base_length) / base_length * 100
        print(f"改善評価: {improved_rate:.2f}% 改悪")
    
    # 巡回路の描画
    _ = Result.result(city_list, tour, length_cache, isShow=True)

if __name__ == "__main__":
    main()