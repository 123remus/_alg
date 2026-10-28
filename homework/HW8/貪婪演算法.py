import math
import random

def distance(city1, city2):
    return math.sqrt((city1[0]-city2[0])**2 + (city1[1]-city2[1])**2)

def total_distance(tour, cities):
    dist = 0
    n = len(tour)
    for i in range(n):
        dist += distance(cities[tour[i]], cities[tour[(i+1)%n]])
    return dist

def generate_cities(n=10):
    random.seed(123)
    cities = []
    for i in range(n):
        cities.append((random.randint(0, 100), random.randint(0, 100)))
    return cities

# 貪婪演算法 (最近鄰居演算法 Nearest Neighbor)
def greedy_algorithm(cities, start=None):
    n = len(cities)
    if start is None:
        start = 0
    unvisited = set(range(n))
    tour = [start]
    unvisited.remove(start)
    current = start
    
    while unvisited:
        # 找到最近的未訪問城市
        nearest = None
        min_dist = float('inf')
        for city in unvisited:
            d = distance(cities[current], cities[city])
            if d < min_dist:
                min_dist = d
                nearest = city
        # 移動到最近的城市
        tour.append(nearest)
        unvisited.remove(nearest)
        current = nearest
    
    tour_dist = total_distance(tour, cities)
    return tour, tour_dist

if __name__ == "__main__":
    cities = generate_cities(10)
    print("城市座標:", cities)
    tour, dist = greedy_algorithm(cities)
    print("貪婪演算法(最近鄰居) 最佳路徑:", tour)
    print("總距離:", dist)
