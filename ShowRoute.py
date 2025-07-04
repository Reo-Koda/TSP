import matplotlib.pyplot as plt

def show_route(city_list, tour):
    tour_x = [city_list[i][0] for i in tour]
    tour_x.append(city_list[tour[0]][0])
    tour_y = [city_list[i][1] for i in tour]
    tour_y.append(city_list[tour[0]][1])

    plt.figure(figsize=(8, 8))
    plt.plot(tour_x, tour_y, marker="o")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.axis("equal")

    plt.show()