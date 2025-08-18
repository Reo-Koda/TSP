import ShowRoute
import CalcLength
import CheckTour

def result(city_list, tour, length_cashe, isShow=True):
    CheckTour.check_tour(city_list, tour)
    calc_length = CalcLength.calc_tour_length(tour, length_cashe)
    print(f"巡回路長：{calc_length:.4f}")
    if isShow:
        ShowRoute.show_route(city_list, tour)
    return calc_length