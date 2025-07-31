import os
import random
import time
import math
import Opt
import CalcLength
import Gready
from concurrent.futures import ProcessPoolExecutor, as_completed

def initialize_pheromone(n, init_val=1.):
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

def choose_next_city_eps(current, unvisited, pheromone, heuristic, alpha, beta):
    EPSILON = 0.3
    # 分母を計算 & 最大値の都市を探索
    denom = 0.0
    max_tau = -1
    for j in unvisited:
        tau = (pheromone[current][j]**alpha) * (heuristic[current][j]**beta)
        denom += tau
        if max_tau < tau:
            max_tau = tau
            next_city = j
    if random.random() < EPSILON:
        return next_city
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
    
    def ACS_move(self, city_list, n, length_cache, pheromone, heuristic, alpha, beta, base_pheromone, rho):
        start = random.randrange(n)
        self.tour = [start]
        unvisited = set(range(n)) - {start}
        while unvisited:
            current = self.tour[-1]
            next = choose_next_city_eps(current, list(unvisited), pheromone, heuristic, alpha, beta)
            self.tour.append(next)
            # フェロモンの変動
            pheromone[current][next] = rho*pheromone[current][next] + (1 - rho)*base_pheromone
            unvisited.remove(next)
        self.tour_length = CalcLength.calc_tour_length(city_list, self.tour, length_cache)

    def improve(self, city_list, length_cache, neighbors_rank, rank):
        self.tour = Opt.fast_two_or_1m(city_list, self.tour, length_cache, neighbors_rank, rank)
        # self.tour = Opt.fast_three_or_1m(city_list, self.tour, length_cache, neighbors_rank, rank)
        self.tour_length = CalcLength.calc_tour_length(city_list, self.tour, length_cache)

def update_pheromone(pheromone, n, ants, rho, Q):
    # 蒸発
    for i in range(n):
        for j in range(n):
            # pheromone[i][j] *= rho
            pheromone[i][j] = max(pheromone[i][j] * rho, 2e-16)
    # 補充
    for ant in ants:
        deposit = Q / ant.tour_length
        for i in range(n):
            a, b = ant.tour[i], ant.tour[(i+1) % n]
            pheromone[a][b] += deposit
            pheromone[b][a] += deposit

def update_pheromone_best_only(pheromone, n, tour, min_length, rho, Q):
    # 蒸発
    for i in range(n):
        for j in range(n):
            pheromone[i][j] = max(pheromone[i][j] * rho, 2e-16)
    # 補充
    deposit = Q / min_length
    for i in range(n):
        a, b = tour[i], tour[(i+1) % n]
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
        update_pheromone(pheromone, n, ants, rho, Q)

    return best_tour

def run_ant_move(size, city_list, n, length_cache, pheromone, heuristic, alpha, beta):
    ants = [Ant() for _ in range(size)]
    for ant in ants:
        ant.move(city_list, n, length_cache, pheromone, heuristic, alpha, beta)
    return ants

def run_ant_ACS_move(size, city_list, n, length_cache, pheromone, heuristic, alpha, beta, base_pheromone, rho):
    ants = [Ant() for _ in range(size)]
    for ant in ants:
        ant.ACS_move(city_list, n, length_cache, pheromone, heuristic, alpha, beta, base_pheromone, rho)
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
            # if improved:
            #     cnt = 0
            # else:
            #     cnt += 1
            # if cnt % 25 == 0 and cnt != 0:
            #     # rho = max(rho*0.9, 0.1)
            #     rho = 0.14
            #     # alpha = min(alpha*1.05, 5.0)
            #     # alpha = min(alpha*1.4, 5.0)
            #     alpha = 1.41
            #     # beta = max(beta*0.5, 1.0)
            #     beta = 1.0
            # print(f"cnt: {cnt:>3}, rho: {rho:.2f}, alpha: {alpha:.2f}, beta: {beta:.2f}")
            # 指定した時間になったらbreak
            if time.perf_counter() - t_start > minuites * 60:
                print(f"phase { phase } time out")
                break

            print(f"phase{phase:>3}: {min_length:.4f}") if improved else None
            # フェロモン更新
            update_pheromone(pheromone, n, ants, rho, Q)

    return best_tour

# 以下は並列処理を基本とする
def ACS(city_list, length_cache, neighbors_rank, rank, times=100, minuites=5, ants_num=50, alpha=1.0, beta=5.0, rho_global=0.9, rho_local=0.9, Q=100.0, isPrint=True):
    """
    Ant Colony System
    アリが巡回路を生成する際、ε-greedy法のように確率 ε で (pheromone[current][j]**alpha) * (heuristic[current][j]**beta) / denom の最大値を選び、
    確率 (1- ε) で、従来の選び方をする方法

    最良解のみでフェロモンを更新することで、探索の集中化を促す
    初期フェロモン濃度は、1 / (n*Lnn) を用いることが推奨される
    このとき、n は都市数、Lnn は適当な都市から出発した最近近傍法による巡回経路長となる

    アリが移動する都市を選んだ直後に選択された経路に対して、pheromone(t+1) = rho*pheromone(t) + (1 + rho)*base_pheromone
    を行い、基準値(base_pheromone) を維持するようにフェロモンを変化させることで探索の多様性を生む
    このとき、基準値である base_pheromone は初期フェロモン濃度にすることが推奨される

    最後に、最良解のみでフェロモンを更新する際の蒸発率を rho_global とし、基準値あたりで変動を起こす際の蒸発率を rho_local として、
    どちらも 0.9 が用いられることが多い
    """
    n = len(city_list)
    # フェロモンの初期化
    tmp_tour = Gready.k_rand_nn(city_list, length_cache, neighbors_rank, k=3, noise_rate=0.01)
    tmp_length = CalcLength.calc_tour_length(city_list, tmp_tour, length_cache)
    base_pheromone = 1/(n*tmp_length)
    pheromone = initialize_pheromone(n, init_val=base_pheromone)
    # ヒューリスティック距離を定義
    heuristic = [[1. / length_cache[i][j] if length_cache[i][j] != 0 else float('inf') for j in range(n)] for i in range(n)]

    best_tour, min_length = None, float('inf')
    # 並列処理を用いてアリによる巡回路の構築
    max_workers = max_workers = min(ants_num, os.cpu_count() or 1)
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
                    run_ant_ACS_move,
                    size,
                    city_list,
                    n,
                    length_cache,
                    pheromone,
                    heuristic,
                    alpha,
                    beta,
                    base_pheromone,
                    rho_local
                ))
                remaining -= size

            # 結果を集めてベスト更新
            for future in as_completed(futures):
                batch = future.result()
                ants.extend(batch)
                for ant in batch:
                    if ant.tour_length < min_length:
                        min_length = ant.tour_length
                        best_tour  = ant.tour.copy()
                        improved   = True

            # 指定した時間になったらbreak
            if time.perf_counter() - t_start > minuites * 60:
                print(f"phase { phase } time out")
                break

            print(f"phase{phase:>3}: {min_length:.4f}") if improved and isPrint else None
            # フェロモン更新
            update_pheromone_best_only(pheromone, n, best_tour, min_length, rho_global, Q)

    return best_tour
