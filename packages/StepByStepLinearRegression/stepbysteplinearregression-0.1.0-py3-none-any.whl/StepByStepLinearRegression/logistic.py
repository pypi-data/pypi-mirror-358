import numpy as np
import pandas as pd

class LogisticRegression:
    def __init__(self):
        self.x_bar = None
        self.y_star_bar = None
        self.slope = None
        self.intercept = None
        self.steps_df = None

    def fit(self, x, y):
        x = np.array(x)
        y = np.array(y)

        # 分組: 計算每組內的轉換值和權重
        groups = {}
        for xi, yi in zip(x, y):
            if xi not in groups:
                groups[xi] = {'n': 0, 'sum_y': 0}
            groups[xi]['n'] += 1
            groups[xi]['sum_y'] += yi

        x_new = []
        y_star = []
        weights = []

        for xi in sorted(groups):
            nj = groups[xi]['n']
            pj = groups[xi]['sum_y'] / nj

            if pj in [0, 1]:
                continue  # 避免 log(0) 無法計算

            y_star_j = np.log(pj / (1 - pj))
            wj = nj * pj * (1 - pj)

            x_new.append(xi)
            y_star.append(y_star_j)
            weights.append(wj)

        x_new = np.array(x_new)
        y_star = np.array(y_star)
        weights = np.array(weights)

        self.x_bar = np.average(x_new, weights=weights)
        self.y_star_bar = np.average(y_star, weights=weights)

        x_dev = x_new - self.x_bar
        y_dev = y_star - self.y_star_bar

        s_xy = np.sum(weights * x_dev * y_dev)
        s_xx = np.sum(weights * x_dev**2)

        self.slope = s_xy / s_xx
        self.intercept = self.y_star_bar - self.slope * self.x_bar

        self.steps_df = pd.DataFrame({
            'x_group': x_new,
            'y*': y_star,
            'w': weights,
            'x - x̄': x_dev,
            'y* - ȳ*': y_dev,
            'w(x - x̄)(y* - ȳ*)': weights * x_dev * y_dev,
            'w(x - x̄)^2': weights * x_dev**2
        })

    def summary(self):
        print(f"x̄ = {self.x_bar:.4f}, ȳ* = {self.y_star_bar:.4f}")
        print(f"Slope (b1) = {self.slope:.4f}")
        print(f"Intercept (b0) = {self.intercept:.4f}")
        print(f"Logit Model: ln(p/(1 - p)) = {self.intercept:.4f} + {self.slope:.4f} * x")

    def show_steps(self):
        print(self.steps_df.to_string(index=False))
