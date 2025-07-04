import os
import ReadFile
import CalcLength
import Result

basename = input("読み込む TSP ファイル名を拡張子なしで入力してください（例: att48）: ")
dir_name  = f"{basename}.tsp"
file_name = f"{basename}.tsp"
path = os.path.join(".", "ALL_tsp", dir_name, file_name)
city_list = ReadFile.read_file(path)

ans_dir_name  = f"{basename}.opt.tour"
ans_file_name = f"{basename}.opt.tour"
ans_path = os.path.join(".", "ALL_tsp", ans_dir_name, ans_file_name)

canRead = False
ans_tour = []
with open(ans_path, "r") as file_object:
    for line in file_object:
        if line.strip() == "-1":
            canRead = False
        if canRead:
            ans_tour.append(int(line.strip()) - 1)
        if line.strip() == "TOUR_SECTION":
            canRead = True

# 高速化のため、都市間の距離の計算結果を保存する
length_cashe = [[-1] * len(city_list) for _ in range(len(city_list))]
# 事前に距離を計算する場合に使用
for i in range(len(city_list)):
    for j in range(i + 1, len(city_list)):
        _ = CalcLength.calc_straight_length(city_list, i, j, length_cashe)

length = Result.result(city_list, ans_tour, length_cashe)