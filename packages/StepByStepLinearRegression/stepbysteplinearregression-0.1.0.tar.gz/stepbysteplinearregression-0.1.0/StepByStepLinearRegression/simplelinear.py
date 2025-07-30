import numpy as np
import pandas as pd

class SimpleLinearRegression:
    def __init__(self):
        self.x_bar = None
        self.y_bar = None
        self.slope = None
        self.intercept = None
        self.steps_df = None
        self.sse = None
        self.ssr = None
        self.mse = None
        self.n = None


    def fit(self, x, y):
        x = np.array(x)
        y = np.array(y)
        self.n = len(x)

        self.x_bar = np.mean(x)
        self.y_bar = np.mean(y)

        x_dev = x - self.x_bar
        y_dev = y - self.y_bar
        xy_dev = x_dev * y_dev
        xx_dev = x_dev ** 2

        s_xy = np.sum(xy_dev)
        s_xx = np.sum(xx_dev)

        self.slope = s_xy / s_xx
        self.intercept = self.y_bar - self.slope * self.x_bar

        y_hat = self.intercept + self.slope * x
        residuals = y - y_hat
        y_hat_dev = y_hat - self.y_bar

        self.sse = np.sum(residuals ** 2)
        self.mse = self.sse / (len(x)-2)        
        self.ssr = np.sum(y_hat_dev ** 2)

        self.steps_df = pd.DataFrame({
            'x': x,
            'y': y,
            'x - x̄': x_dev,
            'y - ȳ': y_dev,
            '(x - x̄)(y - ȳ)': xy_dev,
            '(x - x̄)^2': xx_dev,
            'ŷ': y_hat,
            'residual': residuals,
            'ŷ - ȳ': y_hat_dev
        })

    def summary(self):
        print(f"x̄ = {self.x_bar:.4f}, ȳ = {self.y_bar:.4f}")
        print(f"Slope (b1) = {self.slope:.4f}")
        print(f"Intercept (b0) = {self.intercept:.4f}")
        print(f"SSR = {self.ssr:.4f}")
        print(f"SSE = {self.sse:.4f}")
        print(f"MSE = {self.mse:.4f}")

    def show_steps(self):
        print(self.steps_df.to_string(index=False))