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

# 模擬退火法 (Simulated Annealing)
def simulated_annealing(cities, initial_temp=10000, cooling_rate=0.995, max_iterations=10000):
    n = len(cities)
    # 隨機初始解
    current_tour = list(range(n))
    random.shuffle(current_tour)
    current_dist = total_distance(current_tour, cities)
    
    best_tour = current_tour[:]
    best_dist = current_dist
    
    temperature = initial_temp
    
    for iteration in range(max_iterations):
        # 生成鄰近解
        neighbor_tour = generate_neighbor(current_tour)
        neighbor_dist = total_distance(neighbor_tour, cities)
        
        # 計算能量差
        delta = neighbor_dist - current_dist
        
        # 如果更好，或以機率接受較差的解
        if delta < 0 or random.random() < math.exp(-delta / temperature):
            current_tour = neighbor_tour
            current_dist = neighbor_dist
            if current_dist < best_dist:
                best_tour = current_tour[:]
                best_dist = current_dist
        
        # 降溫
        temperature *= cooling_rate
    
    return best_tour, best_dist

if __name__ == "__main__":
    cities = generate_cities(10)
    print("城市座標:", cities)
    tour, dist = simulated_annealing(cities)
    print("模擬退火法 最佳路徑:", tour)
    print("總距離:", dist)
