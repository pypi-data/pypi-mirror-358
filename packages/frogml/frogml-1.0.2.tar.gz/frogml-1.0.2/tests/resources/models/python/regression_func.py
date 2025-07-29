from sklearn.linear_model import LinearRegression


def predict(x: float) -> float:
    model = LinearRegression()
    model.fit([[5], [15], [25], [35], [45], [55]], [5, 20, 14, 32, 22, 38])
    return float(model.predict([[x]])[0])
