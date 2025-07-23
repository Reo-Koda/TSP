import os
import random
import time
import math
import Opt
import CalcLength
from concurrent.futures import ProcessPoolExecutor, as_completed

def initialize_pheromone(n):
    init_val = 1.
    return [[init_val for _ in range(n)] for _ in range(n)]

def choose_next_city(current, unvisited, pheromone, heuristic, alpha, beta):
    # 分母を計算
    denom = 0.0
    for j in unvisited:
        denom += (pheromone[current][j]**alpha) * (heuristic[current][j]**beta)
    # 確率に従い選択
    r = random.random()
    cumulative = 0.0
    for j in unvisited:
        prob = (pheromone[current][j]**alpha) * (heuristic[current][j]**beta) / denom
        cumulative += prob
        if r <= cumulative:
            return j
    return unvisited[-1] # 万一の保険

class Ant:
    def __init__(self):
        self.tour = []
        self.tour_length = None

    def move(self, city_list, n, length_cache, pheromone, heuristic, alpha, beta):
        start = random.randrange(n)
        self.tour = [start]
        unvisited = set(range(n)) - {start}
        while unvisited:
            current = self.tour[-1]
            next = choose_next_city(current, list(unvisited), pheromone, heuristic, alpha, beta)
            self.tour.append(next)
            unvisited.remove(next)
        self.tour_length = CalcLength.calc_tour_length(city_list, self.tour, length_cache)

    def improve(self, city_list, length_cache, neighbors_rank, rank):
        self.tour = Opt.fast_two_or_1m(city_list, self.tour, length_cache, neighbors_rank, rank)
        # self.tour = Opt.fast_three_or_1m(city_list, self.tour, length_cache, neighbors_rank, rank)
        self.tour_length = CalcLength.calc_tour_length(city_list, self.tour, length_cache)

def update_pheromone(pheromone, ants, rho, Q):
    n = len(pheromone)
    # 蒸発
    for i in range(n):
        for j in range(n):
            # pheromone[i][j] *= rho
            pheromone[i][j] = max(pheromone[i][j] * rho, 2e-16)
    # 補充
    for ant in ants:
        deposit = Q / ant.tour_length
        tour_num = len(ant.tour)
        for i in range(tour_num):
            a, b = ant.tour[i], ant.tour[(i+1) % tour_num]
            pheromone[a][b] += deposit
            pheromone[b][a] += deposit

def ACO(city_list, length_cache, neighbors_rank, rank, times=100, ants_num=50, alpha=1.0, beta=5.0, rho=0.5, Q=100.0):
    """
    times    # 繰り返す回数
    ants_num # アリの数
    alpha    # フェロモン影響度
    beta     # ヒューリスティック影響度
    rho      # 蒸発率
    Q        # フェロモン補充定数
    """
    n = len(city_list)
    pheromone = initialize_pheromone(n)
    heuristic = [[1. / length_cache[i][j] if length_cache[i][j] != 0 else float('inf') for j in range(n)] for i in range(n)]

    # アリの初期化
    ants = [Ant() for _ in range(ants_num)]

    best_tour, min_length = None, float('inf')
    cnt = 0
    for phase in range(times):
        improved = False
        # アリによる巡回路の構築
        for ant in ants:
            ant.move(city_list, n, length_cache, pheromone, heuristic, alpha, beta)
            if min_length > ant.tour_length:
                # ant.improve(city_list, length_cache, neighbors_rank, rank)
                min_length, best_tour = ant.tour_length, ant.tour.copy()
                improved = True
        print(f"phase{phase:>3}: {min_length:.4f}")
        if improved:
            cnt = 0
        else:
            cnt += 1
        if cnt == 50:
            break
        if phase % 25 == 0 and phase != 0:
            rho *= 0.5
            alpha *= 1.2
            beta = max(beta*0.6, 1.0)
            print(alpha, beta)
        # フェロモン更新
        update_pheromone(pheromone, ants, rho, Q)

    return best_tour

def run_ant_move(size, city_list, n, length_cache, pheromone, heuristic, alpha, beta):
    ants = [Ant() for _ in range(size)]
    for ant in ants:
        ant.move(city_list, n, length_cache, pheromone, heuristic, alpha, beta)
    return ants

def multi_ACO(city_list, length_cache, neighbors_rank, rank, times=100, minuites=5, ants_num=50, alpha=1.0, beta=5.0, rho=0.5, Q=100.0):
    """
    times    # 繰り返す回数
    ants_num # アリの数
    alpha    # フェロモン影響度
    beta     # ヒューリスティック影響度
    rho      # 蒸発率
    Q        # フェロモン補充定数
    """
    n = len(city_list)
    pheromone = initialize_pheromone(n)
    heuristic = [[1. / length_cache[i][j] if length_cache[i][j] != 0 else float('inf') for j in range(n)] for i in range(n)]

    best_tour, min_length = None, float('inf')
    cnt = 0
    # 並列処理を用いてアリによる巡回路の構築
    max_workers = max_workers = min(ants_num, os.cpu_count() or 1)
    batch_size  = math.ceil(ants_num / max_workers)
    print(f"max_workers: { max_workers }")
    t_start = time.perf_counter()
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        for phase in range(times):
            improved = False
            ants = []
            remaining = ants_num
            futures = []

            # 各ワーカーにバッチを割り当て
            while remaining > 0:
                size = min(max_workers, remaining)
                futures.append(executor.submit(
                    run_ant_move,
                    size,
                    city_list,
                    n,
                    length_cache,
                    pheromone,
                    heuristic,
                    alpha,
                    beta
                ))
                remaining -= size

            # for _ in range(max_workers):
            #     size = min(batch_size, remaining)
            #     futures.append(executor.submit(
            #         run_ant_move,
            #         size,
            #         city_list, n,
            #         length_cache,
            #         pheromone,
            #         heuristic,
            #         alpha, beta
            #     ))
            #     remaining -= size

            # 結果を集めてベスト更新
            for future in as_completed(futures):
                batch = future.result()
                ants.extend(batch)
                for ant in batch:
                    if ant.tour_length < min_length:
                        # ant.improve(city_list, length_cache, neighbors_rank, rank)
                        min_length = ant.tour_length
                        best_tour  = ant.tour.copy()
                        improved   = True
            if improved:
                cnt = 0
            else:
                cnt += 1
            if cnt % 25 == 0 and cnt != 0:
                # rho = max(rho*0.9, 0.1)
                rho = 0.14
                # alpha = min(alpha*1.05, 5.0)
                # alpha = min(alpha*1.4, 5.0)
                alpha = 1.41
                # beta = max(beta*0.5, 1.0)
                beta = 1.0
            print(f"cnt: {cnt:>3}, rho: {rho:.2f}, alpha: {alpha:.2f}, beta: {beta:.2f}")
            # 指定した時間になったらbreak
            if time.perf_counter() - t_start > minuites * 60:
                break

            print(f"phase{phase:>3}: {min_length:.4f}")
            # フェロモン更新
            update_pheromone(pheromone, ants, rho, Q)

    return best_tour
