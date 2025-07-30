import numpy as np
import pandas as pd

class MultipleLinearRegression:
    def __init__(self):
        self.coefficients = None
        self.intercept = None
        self.steps_df = None
        self.sse = None
        self.ssr = None
        self.mse = None
        self.n = None
        self.p = None

    def fit(self, X, y):
        X = np.array(X)
        y = np.array(y)

        # 使用者若以變數為列，需轉置為 (n_samples, n_features)
        if X.shape[0] < X.shape[1]:
            X = X.T

        self.n, self.p = X.shape

        X_with_intercept = np.column_stack((np.ones(self.n), X))
        beta = np.linalg.pinv(X_with_intercept) @ y

        self.intercept = beta[0]
        self.coefficients = beta[1:]

        y_hat = X_with_intercept @ beta
        residuals = y - y_hat
        y_bar = np.mean(y)
        y_hat_dev = y_hat - y_bar

        self.sse = np.sum(residuals ** 2)
        self.ssr = np.sum(y_hat_dev ** 2)
        self.mse = self.sse / (self.n - self.p - 1)

        self.steps_df = pd.DataFrame(X, columns=[f'x{i+1}' for i in range(self.p)])
        self.steps_df['y'] = y
        self.steps_df['ŷ'] = y_hat
        self.steps_df['ŷ - ȳ'] = y_hat_dev
        self.steps_df['residual'] = residuals

    def summary(self):
        print(f"Intercept (b0) = {self.intercept:.4f}")
        for i, coef in enumerate(self.coefficients):
            print(f"Slope (b{i+1}) = {coef:.4f}")
        print(f"SSE = {self.sse:.4f}")
        print(f"SSR = {self.ssr:.4f}")
        print(f"MSE = {self.mse:.4f}")

    def show_steps(self):
        print(self.steps_df.to_string(index=False))
