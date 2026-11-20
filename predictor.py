"""Tiny pre-trained Iris classifier used to keep the teaching image lightweight.

The coefficients come from a logistic-regression model trained beforehand on Iris.
No ML training library is required at runtime.
"""
from typing import Sequence

COEFFICIENTS = [
    [-0.42023936, 0.96693058, -2.51894415, -1.08459466],
    [0.53186946, -0.31526881, -0.20410552, -0.94276181],
    [-0.11163009, -0.65166176, 2.72304967, 2.02735647],
]
INTERCEPTS = [9.84168898, 2.22450596, -12.06619494]


def predict_iris(features: Sequence[float]) -> int:
    scores = [
        intercept + sum(weight * value for weight, value in zip(weights, features))
        for weights, intercept in zip(COEFFICIENTS, INTERCEPTS)
    ]
    return max(range(len(scores)), key=scores.__getitem__)
