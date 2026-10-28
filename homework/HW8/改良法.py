import math
import random
import copy

# TSP Problem Setup
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

# 2-opt改良法 (Local Search Improvement)
def two_opt_improvement(cities, initial_tour=None, max_iterations=1000):
    n = len(cities)
    if initial_tour is None:
        tour = list(range(n))
        random.shuffle(tour)
    else:
        tour = list(initial_tour)
    
    best_tour = tour[:]
    best_dist = total_distance(best_tour, cities)
    improved = True
    iterations = 0
    
    while improved and iterations < max_iterations:
        improved = False
        iterations += 1
        for i in range(n-1):
            for j in range(i+2, n):
                if j == n-1 and i == 0:
                    continue
                new_tour = best_tour[:]
                # 2-opt: reverse segment i+1 to j
                new_tour[i+1:j+1] = reversed(best_tour[i+1:j+1])
                new_dist = total_distance(new_tour, cities)
                if new_dist < best_dist:
                    best_tour = new_tour
                    best_dist = new_dist
                    improved = True
                    break
            if improved:
                break
    
    return best_tour, best_dist

if __name__ == "__main__":
    cities = generate_cities(10)
    print("城市座標:", cities)
    tour, dist = two_opt_improvement(cities)
    print("改良法(2-opt) 最佳路徑:", tour)
    print("總距離:", dist)
