import math
import random
import copy

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

# 鄰近解生成：交換兩個城市
def generate_neighbor(tour):
    neighbor = tour[:]
    n = len(tour)
    i, j = random.sample(range(n), 2)
    neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
    return neighbor

# 梯度下降法 (Gradient Descent / Steepest Descent for TSP)
def gradient_descent(cities, max_iterations=10000, step_size=1):
    n = len(cities)
    # 隨機初始解
    current_tour = list(range(n))
    random.shuffle(current_tour)
    current_dist = total_distance(current_tour, cities)
    
    best_tour = current_tour[:]
    best_dist = current_dist
    
    for iteration in range(max_iterations):
        # 在鄰域中尋找梯度方向（最陡下降）
        best_neighbor_tour = None
        best_neighbor_dist = current_dist
        
        # 採樣多個鄰近解來估計梯度方向
        for _ in range(min(20, n*(n-1)//2)):
            neighbor_tour = generate_neighbor(current_tour)
            neighbor_dist = total_distance(neighbor_tour, cities)
            if neighbor_dist < best_neighbor_dist:
                best_neighbor_dist = neighbor_dist
                best_neighbor_tour = neighbor_tour
        
        # 如果找到更好的解（沿梯度下降方向）
        if best_neighbor_tour is not None and best_neighbor_dist < current_dist:
            current_tour = best_neighbor_tour
            current_dist = best_neighbor_dist
            if current_dist < best_dist:
                best_tour = current_tour[:]
                best_dist = current_dist
        else:
            # 若無改善，可嘗試隨機跳躍或終止
            pass
    
    return best_tour, best_dist

if __name__ == "__main__":
    cities = generate_cities(10)
    print("城市座標:", cities)
    tour, dist = gradient_descent(cities)
    print("梯度下降法 最佳路徑:", tour)
    print("總距離:", dist)
