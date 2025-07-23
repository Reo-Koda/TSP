import matplotlib.pyplot as plt
import random
import time
import CalcLength
import Gready
import Opt
import Kick

class Individual:
    def __init__(self, city_list, length_cache, neighbors_rank):
        n = len(city_list)
        genes_base = [x for x in range(n)]
        if random.random() < 0.3:
            start = random.randint(0, n-1)
            self.genes = Gready.rand_nn(city_list, neighbors_rank, start, noise_rate=0.01)
        # elif random.random() < 0.4:
        #     self.genes = Gready.rand_ci(city_list, length_cache, times=1)
        else:
            self.genes = random.sample(genes_base, len(genes_base))

        self.fitness = None
    
    def evaluate(self, city_list, length_cache):
        self.fitness = CalcLength.calc_tour_length(city_list, self.genes, length_cache)
        return self.fitness
    
    def improve(self, city_list, length_cache, neighbors_rank, rank):
        self.genes = Opt.fast_two_or_1m(city_list, self.genes, length_cache, neighbors_rank, rank)
        if random.random() < 0.1:
            self.genes = Opt.fast_three_or_1m(city_list, self.genes, length_cache, neighbors_rank, int(rank/2))
    
    def mutate(self, city_list, length_cache, stop_cnt):
        # 最初のバージョン
        # # self.genes = Kick.kick(self.genes, stop_cnt)
        # if stop_cnt < 4:
        #     self.genes = Kick.random_reverse(self.genes)
        #     self.genes = Kick.translocation(self.genes)
        # else:
        #     self.genes = Kick.random_swap_section(self.genes)
        #     # self.genes = Kick.scramble(self.genes)

        #     r = random.random()
        #     if r < 0.1:
        #         print(" double_bridge ", end="", flush=True)
        #         self.genes = Kick.double_bridge(self.genes)
        #         self.genes = Kick.double_bridge(self.genes)
        
        # 別のバージョン
        if stop_cnt < 4:
            self.genes = Kick.double_bridge(self.genes)
        else:
            self.genes = Kick.LNS_Kick(city_list, self.genes, length_cache, destroy_num=int(len(self.genes)*0.3))

def init_population(pop_size, city_list, length_cache, neighbors_rank):
    return [Individual(city_list, length_cache, neighbors_rank) for _ in range(pop_size)]

def tournament_selection(population, tour_size=3):
    contenders = random.sample(population, tour_size)
    return min(contenders, key=lambda ind: ind.fitness)

def order_crossover(p1, p2, city_list, length_cache, neighbors_rank):
    n = len(p1.genes)
    # 交叉点を二つ選ぶ
    i, j = sorted(random.sample(range(n), 2))
    child = [-1] * n
    # 区間コピー
    child[i:j+1] = p1.genes[i:j+1]
    # 残りを p2 の順序で埋める
    fill_pos = (j + 1) % n
    for gene in p2.genes[j+1:] + p2.genes[:j+1]:
        if gene not in child:
            child[fill_pos] = gene
            fill_pos = (fill_pos + 1) % n
    offspring = Individual(city_list, length_cache, neighbors_rank)
    offspring.genes = child
    return offspring

def next_generation(population, city_list, length_cache, neighbors_rank, rank, gen, stop_cnt, elite_size=5, tournament_size=3, mutation_rate=0.02):
    # 評価済み population
    # エリート保存
    population.sort(key=lambda ind: ind.fitness)
    next_pop = population[:elite_size]
    # 残りを生成
    while len(next_pop) < len(population):
        parent1 = tournament_selection(population, tournament_size)
        parent2 = tournament_selection(population, tournament_size)
        child = order_crossover(parent1, parent2, city_list, length_cache, neighbors_rank)
        if random.random() < mutation_rate: # 確率で突然変異
            print(f"変異開始 {len(next_pop):>3} / {len(population):>3}", end=" -", flush=True)
            child.mutate(city_list, length_cache, stop_cnt)
            child.improve(city_list, length_cache, neighbors_rank, rank)
            print(">  変異終了")
        elif gen % 10 == 0 or random.random() < 0.2: # 通常一つの遺伝子につき30%の確率で局所探索を行う 全体の遺伝子に局所探索を行うのは10回に1回
            print(f"改善開始 {len(next_pop):>3} / {len(population):>3}", end=" -", flush=True)
            child.improve(city_list, length_cache, neighbors_rank, rank)
            print(f">  改善終了")
        child.evaluate(city_list, length_cache)
        next_pop.append(child)
    return next_pop

def GA(city_list, length_cache, neighbors_rank, rank, pop_size=50, generations=200, minuites=10, elite_size=5, tournament_size=3, mutation_rate=0.02, animate=False, pause_time=0.01):
    # 初期集団生成 & 評価
    print("遺伝子の初期化", end=" --->  ", flush=True)
    population = init_population(pop_size, city_list, length_cache, neighbors_rank)
    print("完了")
    print("遺伝子の評価", end=" ", flush=True)
    for ind in population:
        ind.evaluate(city_list, length_cache)
        print("-", end="")
    print(">  完了")

    best = min(population, key=lambda ind: ind.fitness)
    print(f"初期世代: best distance = {best.fitness:.2f}")

    if animate:
        plt.ion()
        fig, ax = plt.subplots()
        # 座標リストに変換
        xs = [city_list[i][0] for i in best.genes] + [city_list[best.genes[0]][0]]
        ys = [city_list[i][1] for i in best.genes] + [city_list[best.genes[0]][1]]
        line, = ax.plot(xs, ys, '-o')
        ax.set_title(f'世代数 0: {best.fitness:.2f}')
        plt.show()

    t_start = time.perf_counter()
    stop_cnt = 0
    for gen in range(1, generations + 1):
        population = next_generation(population, city_list, length_cache, neighbors_rank, rank, gen, stop_cnt, elite_size, tournament_size, mutation_rate)
        current_best = min(population, key=lambda ind: ind.fitness)
        if current_best.fitness < best.fitness:
            best = current_best
            stop_cnt = 0
            print(f"世代数 {gen:>4}: best distance = {best.fitness:.2f}")
        else:
            stop_cnt += 1
            print(f"世代数 {gen:>4}: best distance is not found")
        
        if animate:
            # 座標更新
            xs = [city_list[i][0] for i in current_best.genes] + [city_list[current_best.genes[0]][0]]
            ys = [city_list[i][1] for i in current_best.genes] + [city_list[current_best.genes[0]][1]]
            line.set_data(xs, ys)
            ax.set_title(f'Gen {gen}: {current_best.fitness:.2f}')
            ax.relim(); ax.autoscale_view()
            fig.canvas.draw()
            plt.pause(pause_time)
        
        # 指定した時間になったらbreak
        if time.perf_counter() - t_start > minuites * 60:
            break
    
    if animate:
        plt.ioff()
    return best.genes

