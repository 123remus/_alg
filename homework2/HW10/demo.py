from numerical import (
    derivative,
    gradient,
    integral,
    integral_1d,
    monte_carlo_integral,
    sparse_integral,
    sum_of_squares,
)


def main():
    print("=== 1. 單變數數值微分 ===")
    cube = lambda x: x ** 3
    for method in ("central", "forward", "backward"):
        value = derivative(cube, 2.0, h=1e-5, method=method)
        print(f"d/dx x^3 at x=2 ({method:8s}) = {value:.10f}  解析解 = 12")

    print("\n=== 2. n 變數梯度 ===")
    for point in ((1.0,), (1.0, 1.0, 1.0), (0.5,) * 100):
        g = gradient(sum_of_squares, point)
        print(f"n={len(point):3d}  grad(x1^2+...+xn^2)[:3] = {tuple(round(v, 8) for v in g[:3])}  解析解 = {(2 * point[0]):.1f}")

    print("\n=== 3~6. 超體積積分：1 / 2 / 5 / 100 維 ===")
    print(f"{'n':>4}  {'解析解 n/3':>12}  {'數值積分':>14}  {'誤差':>12}  方法")
    grid_steps = {1: 10_000, 2: 200, 5: 12}
    for n in (1, 2, 5, 100):
        exact = n / 3
        low, high = (0.0,) * n, (1.0,) * n
        if n in grid_steps:
            value = integral(sum_of_squares, low, high, steps=grid_steps[n])
            method = f"黎曼網格 {grid_steps[n]}^{n}"
        else:
            value = integral(sum_of_squares, low, high)
            method = "稀疏網格 (全網格不可行)"
        print(f"{n:>4}  {exact:>12.8f}  {value:>14.8f}  {value - exact:>+12.2e}  {method}")

    print("\n=== 7. 全網格在 100 維的限制 ===")
    print(f"每維 2 等分需要 2^100 = {2 ** 100} 個點，遠遠超出可計算範圍")
    try:
        integral(sum_of_squares, (0.0,) * 100, (1.0,) * 100, steps=2, method="grid", max_cells=2_000_000)
    except ValueError as error:
        print(f"預期中的錯誤：{error}")
    print(f"稀疏網格 100 維結果 = {sparse_integral(sum_of_squares, (0.0,) * 100, (1.0,) * 100):.10f}  (解析解 = 100/3)")

    print("\n=== 8. 蒙地卡羅 n 維積分 ===")
    print(f"{'n':>4}  {'解析解 n/3':>12}  {'蒙地卡羅':>14}  {'標準誤差':>12}  {'差值':>12}")
    for n in (1, 2, 5, 100):
        low, high = (0.0,) * n, (1.0,) * n
        value, error = monte_carlo_integral(
            sum_of_squares, low, high, samples=100_000, seed=42, with_error=True
        )
        exact = n / 3
        print(f"{n:>4}  {exact:>12.8f}  {value:>14.8f}  {error:>12.8f}  {value - exact:>+12.8f}")

    print("\n=== 9. 其他方法的交叉驗證 ===")
    for method in ("midpoint", "left", "right", "trapezoid", "simpson"):
        value = integral_1d(lambda x: x * x, 0.0, 1.0, steps=1000, method=method)
        print(f"1D {method:9s} = {value:.10f}  (解析解 1/3)")


if __name__ == "__main__":
    main()
