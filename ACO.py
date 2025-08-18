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

    def move(self, n, length_cache, pheromone, heuristic, alpha, beta):
        start = random.randrange(n)
        self.tour = [start]
        unvisited = set(range(n)) - {start}
        while unvisited:
            current = self.tour[-1]
            next = choose_next_city(current, list(unvisited), pheromone, heuristic, alpha, beta)
            self.tour.append(next)
            unvisited.remove(next)
        self.tour_length = CalcLength.calc_tour_length(self.tour, length_cache)
    
    def ACS_move(self, n, length_cache, pheromone, heuristic, alpha, beta, base_pheromone, rho):
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
        self.tour_length = CalcLength.calc_tour_length(self.tour, length_cache)

    def improve(self, city_list_length, length_cache, neighbors_rank, rank):
        self.tour = Opt.fast_two_or_1m(city_list_length, self.tour, length_cache, neighbors_rank, rank)
        # self.tour = Opt.fast_three_or_1m(city_list_length, self.tour, length_cache, neighbors_rank, rank)
        self.tour_length = CalcLength.calc_tour_length(self.tour, length_cache)

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
    
    '''
    エリート戦略をとった AS では、
    deposit = e / min_length
    としてある。このとき、e は最良解をとったアリの数。
    よって Q は 1.0 で固定されていた可能性が出た。

    ※ エリート蟻を過剰に使用すると、探索が早期に非最適解の周辺に集中し、探索の早期停滞を引き起こす可能性があります。
       探索の停滞は[14]で「すべての蟻が同じ経路をたどり、同じ解を繰り返し構築し、より良い解が見つからなくなる状況」と定義されています。
    '''

def update_max_min_pheromone(pheromone, n, tour, min_length, rho, Q, max_pheromone, min_pheromone):
    # 蒸発
    for i in range(n):
        for j in range(n):
            pheromone[i][j] = max(pheromone[i][j] * rho, min_pheromone)
    # 補充
    deposit = Q / min_length
    for i in range(n):
        a, b = tour[i], tour[(i+1) % n]
        pheromone[a][b] = min(pheromone[a][b] + deposit, max_pheromone)
        pheromone[b][a] = min(pheromone[b][a] + deposit, max_pheromone)

def PTS(pheromone, n, max_pheromone, delta):
    for i in range(n):
        for j in range(n):
            pheromone[i][j] = min(pheromone[i][j] + delta * (max_pheromone - pheromone[i][j]), max_pheromone)

def ACO(city_list_length, length_cache, neighbors_rank, rank, times=100, ants_num=50, alpha=1.0, beta=5.0, rho=0.5, Q=100.0):
    """
    times    # 繰り返す回数
    ants_num # アリの数
    alpha    # フェロモン影響度
    beta     # ヒューリスティック影響度
    rho      # 蒸発率
    Q        # フェロモン補充定数
    """
    n = city_list_length
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
            ant.move(n, length_cache, pheromone, heuristic, alpha, beta)
            if min_length > ant.tour_length:
                # ant.improve(city_list_length, length_cache, neighbors_rank, rank)
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

def run_ant_move(size, n, length_cache, pheromone, heuristic, alpha, beta):
    ants = [Ant() for _ in range(size)]
    for ant in ants:
        ant.move(n, length_cache, pheromone, heuristic, alpha, beta)
    return ants

def run_ant_ACS_move(size, n, length_cache, pheromone, heuristic, alpha, beta, base_pheromone, rho):
    ants = [Ant() for _ in range(size)]
    for ant in ants:
        ant.ACS_move(n, length_cache, pheromone, heuristic, alpha, beta, base_pheromone, rho)
    return ants

def multi_ACO(city_list_length, length_cache, neighbors_rank, rank, times=100, minuites=5, ants_num=50, alpha=1.0, beta=5.0, rho=0.5, Q=100.0):
    """
    times    # 繰り返す回数
    ants_num # アリの数
    alpha    # フェロモン影響度
    beta     # ヒューリスティック影響度
    rho      # 蒸発率
    Q        # フェロモン補充定数


    収束したかどうかの判断として、すべての蟻が同じ経路をたどるがある
    """
    n = city_list_length
    pheromone = initialize_pheromone(n)
    # 事前にフェロモンの状態をある程度進める際に使用
    tmp_tour = Gready.ci(city_list_length, length_cache, neighbors_rank)
    tmp_length = CalcLength.calc_tour_length(tmp_tour, length_cache)
    print(tmp_length)
    Q = tmp_length
    deposit = Q*1000 / tmp_length
    for i in range(n):
        a, b = tmp_tour[i], tmp_tour[(i+1) % n]
        pheromone[a][b] += deposit
        pheromone[b][a] += deposit
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
            #         n,
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
            # 指定した時間になったらbreak
            if time.perf_counter() - t_start > minuites * 60:
                print(f"phase { phase } time out")
                break

            print(f"phase{phase:>6}: {min_length:.4f}") if improved or phase % 1000 == 0 else None
            # フェロモン更新
            update_pheromone(pheromone, n, ants, rho, Q)

    return best_tour

# 以下は並列処理を基本とする
def ACS(city_list_length, length_cache, neighbors_rank, rank, times=100, minuites=5, ants_num=50, alpha=1.0, beta=5.0, rho_global=0.9, rho_local=0.9, Q=100.0, isPrint=True):
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
    n = city_list_length
    # フェロモンの初期化
    tmp_tour = Gready.k_rand_nn(city_list_length, length_cache, neighbors_rank, k=3, noise_rate=0.01)
    tmp_length = CalcLength.calc_tour_length(tmp_tour, length_cache)
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

            print(f"phase{phase:>6}: {min_length:.4f}") if (improved or phase % 1000 == 0) and isPrint else None
            # フェロモン更新
            update_pheromone_best_only(pheromone, n, best_tour, min_length, rho_global, Q)

    return best_tour

# フェロモンが収束したかどうかをチェックする関数
# def check_pheromone(best_tour, pheromone, n):
#     EPS = 1e-6
#     sum_pheromone = max_pheromone * (n - 1) + min_pheromone * (n**2)

def MMAS(city_list_length, length_cache, neighbors_rank, rank, times=100, minuites=5, ants_num=50, alpha=1.0, beta=2.0, delta=0.5, rho=0.98, Q=1.0, p_best=0.05, isPrint=True):
    """
    MAX-MIN Ant System
    フェロモンの上限と下限を設定することで、フェロモンの更新の際にフェロモンが極端に大きくなったり小さくなったりすることを防ぐことができる
    初期フェロモン値は「上限」に設定され、局所解に陥ったと判断した際にはフェロモンを「上限」にリセットする。 「下限」に設定することもあり、その場合「上限」に設定した場合と比べて最初の反復におけるフェロモンの偏りが激しくなることが知られている。
    結果的に「上限」に設定したほうが良い結果を得られる。
    更新に用いるフェロモンは、それまでの反復で得た最良解、もしくは各反復で得た最良解 （各反復で得た最良解を用いたほうがうまくいくことが知られている）
    「 反復処理中またはアルゴリズムの実行中に見つかった最良の解を有効活用するため、各反復処理後には1匹の蟻のみがフェロモンを分泌します。
    この蟻は、現在の反復処理で最良の解を見つけた蟻（反復処理最良蟻）または実験開始から最も良い解を見つけた蟻（グローバル最良蟻）のいずれかです。
      一般的に、フェロモン経路の更新に それまでの反復で得た最良解 を独占的に使用することは、MMAS にはあまり適していないようです。
    しかし、フェロモン経路の下限値を低く設定すると、それまでの反復で得た最良解 を使用した場合のパフォーマンスが大幅に向上します」
    フェロモンの蒸発率は 0 に近い値にすることが多い
    pheromone(t+1) = rho*pheromone(t) + best_pheromone
    best_pheromone = 1 / min_length (min_length は全体、または各反復における最良解の経路長)

    全体における最良解 のみを使用する場合、検索が迅速にこの解の周辺に集中し、より良い解の探索が制限されるため、低品質な解に陥る危険性があります。この危険性は、フェロモン経路の更新に 各反復における最良解 を選択することで軽減されます。
    これは、反復ごとの最良解が反復ごとに大きく異なる可能性があり、より多くの解の構成要素が偶発的に強化を受けるためです。

    混合戦略を使用することも可能です。
    例えば、フェロモンの更新に 各反復における最良解 をデフォルトとして選択し、全体における最良解 は一定の反復回数ごとにのみ使用するといった方法です。
    実際、MMASとローカル検索を組み合わせて一部の大きなTSPやQAPベンチマークインスタンスを解く場合、
    最良の戦略は、探索中にフェロモン更新における 全体における最良解 の使用頻度を増加させる動的混合戦略の採用であるようです

    max_pheromone = 1 / ( (1 - rho) * min_length)
    min_length は 全体における最良解 の経路長

    min_pheromone = max_pheromone * ( 1 - p_best**(1/n) ) / ( (n/2 - 1) * p_best**(1/n) )
    n は都市数
    p_best は停滞状態で最良解を選択する確率であり、パラメータとして設定される。

    最初の max_pheromone の値は任意に高い値を設定し、反復するごとに max_pheromone を更新していく。
    アルゴリズムの最初の反復処理において解の探索範囲を拡大するため選択されている。

    論文では alpha = 1.0, beta = 2.0, ants_num = 都市数, rho = 0.98, p_best = 0.05
    rho の値により、比較的遅い収束をもたらす蒸発率であることがわかる
    フェロモンの更新は、反復で最良の結果を出したアリのみを用いて行う
    アリの移動において、距離の降順で並べられた最も近い隣人を含む 20 個の候補リストを使用 (最大でも 20近傍となる)
    候補リスト内の都市がすべて訪問済みだった場合、未訪問の都市の中で (pheromone[current][j]**alpha) * (heuristic[current][j]**beta) / denom が最大の都市を選び移動することにする

    ツアーの構築回数が少ない場合、ρ の値が小さいほどより良いツアーが見つかることがわかります
    ツアー構築の数が多くなる場合、高いρ値を使用する方が有利

    フェロモン経路の低い解の要素が選択される確率を高めることで探索を容易にすることを目的に、
    Pheromone Trail Smoothing (PTS) を施す工夫が考えられる。 論文において、有効であることが示されている
    以下の計算を行うことで PTS を行う。
    pheromone(t) = pheromone(t) + δ * (max_pheromone(t) - pheromone(t))  (0 < δ < 1)
    δ = 1 ならば フェロモン経路の初期化になり、δ = 0 ならば、PTS を行わないことを示す。 論文では δ = 0.5 を使用
    PTS は、長距離の走行が許可されている場合に特に興味深い手法です。
    これは、検索空間のより効率的な探索に役立つからです。
    同時に、PTS により、MMAS は、下位のフェロモン経路の特定の選択に対する感度が低下します。

    局所探索も併用する場合
    f gb が1回の実行内で時間の経過とともに増加する混合戦略を用いることで、最高の性能が得られました。
    これを実現するために、フェロモントレイルの更新をs gb とs ib の間で交互に行う特定のスケジュールを適用しました。
    最初の25回の反復では、s ib のみを使用してフェロモントレイルを更新します。
    f gb は、25 < t 75 (tは反復回数カウンター) の場合は5、75 < t 125 の場合は3、125 < t 250 の場合は2、t > 250 の場合は1に設定します。
    フェロモントレイルの更新において、反復最適解から全体最適解へと重点を徐々に移すことで、
    探索初期における探索空間のより強力な探索から、実行後期における全体的な最適解のより強力な活用への移行を実現します。
    パラメータは以下のように設定した。
    ants_num = 25 (すべてのアリが解に対して局所探索を適用)
    rho = 0.8, alpha = 1.0, beta = 2.0
    アリの移動において、距離の降順で並べられた最も近い隣人を含む 20 個の候補リストを使用 (最大でも 20近傍となる)
    候補リスト内の都市がすべて訪問済みだった場合、未訪問の都市の中で (pheromone[current][j]**alpha) * (heuristic[current][j]**beta) / denom が最大の都市を選び移動することにする
    min_pheromone = max_pheromone / (2 * n)
    p_best = 0.005

    再初期化を設定する際の条件
    最良解に含まれないほぼすべてのフェロモン経路が min_pheromone に非常に近い（100回ごとに計算） かつ 50回の反復で改善された解が見つからなかった場合
    フェロモントレイルの再初期化後に、s gb の代わりにフェロモントレイルの再初期化以降に見つかった最良解を使用すると、探索の多様化がさらに高まります
    """
    n = city_list_length
    # フェロモンの初期化
    max_pheromone = 10.0
    min_pheromone = max_pheromone * ( 1 - p_best**(1/n) ) / ( (n/2 - 1) * p_best**(1/n) )
    pheromone = initialize_pheromone(n, init_val=max_pheromone)
    # ヒューリスティック距離を定義
    heuristic = [[1. / length_cache[i][j] if length_cache[i][j] != 0 else float('inf') for j in range(n)] for i in range(n)]

    # 未改善回数の初期化
    fail_cnt = 0

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
            iter_best_ant_tour = None
            iter_best_ant_tour_length = float('inf')

            # 各ワーカーにバッチを割り当て
            while remaining > 0:
                size = min(max_workers, remaining)
                futures.append(executor.submit(
                    run_ant_move,
                    size,
                    n,
                    length_cache,
                    pheromone,
                    heuristic,
                    alpha,
                    beta
                ))
                remaining -= size

            # 結果を集めて反復における最良解を発見
            for future in as_completed(futures):
                batch = future.result()
                ants.extend(batch)
                for ant in batch:
                    if ant.tour_length < iter_best_ant_tour_length:
                        iter_best_ant_tour_length = ant.tour_length
                        iter_best_ant_tour  = ant.tour.copy()
            
            # ベストを更新
            if iter_best_ant_tour_length < min_length:
                min_length = iter_best_ant_tour_length
                best_tour = iter_best_ant_tour.copy()
                improved = True

            # 指定した時間になったらbreak
            if time.perf_counter() - t_start > minuites * 60:
                print(f"phase { phase } time out")
                break

            print(f"phase{phase:>6}: {min_length:.4f} {iter_best_ant_tour_length:.4f}") if (improved or phase % 1000 == 0) and isPrint else None
            # フェロモン更新
            update_max_min_pheromone(pheromone, n, iter_best_ant_tour, iter_best_ant_tour_length, rho, Q, max_pheromone, min_pheromone)
            # フェロモンの最大最小の更新
            if improved == True:
                max_pheromone = 1 / ( (1 - rho) * min_length)
                min_pheromone = max_pheromone * ( 1 - p_best**(1/n) ) / ( (n/2 - 1) * p_best**(1/n) )
                fail_cnt = 0
            else:
                fail_cnt += 1

            # フェロモンに対して PTS を実施
            if fail_cnt != 0 and fail_cnt % 5000 == 0:
                PTS(pheromone, n, max_pheromone, delta)

    return best_tour

