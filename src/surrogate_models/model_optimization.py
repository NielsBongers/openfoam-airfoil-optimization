import numpy as np
from scipy.optimize import differential_evolution
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

from src.surrogate_models.training import train_models
from src.utils.logging_setup import get_logger


def funct(
    x: np.array, models: dict[str : RandomForestClassifier | RandomForestRegressor]
) -> float:
    logger = get_logger(__name__)

    x = x.reshape(1, -1)

    cls_model: RandomForestClassifier = models["cls_model"]
    reg_model: RandomForestRegressor = models["reg_model"]

    predicted_failure = cls_model.predict(X=x)

    if predicted_failure:
        return np.inf

    cl_predicted = reg_model.predict(X=x)

    logger.info(f"Model result: {cl_predicted.item()}")

    return -cl_predicted.item()


def run_surrogate_model():
    logger = get_logger(__name__)
    cls_model, reg_model = train_models()

    models = {"cls_model": cls_model, "reg_model": reg_model}

    bounds = [
        (-1.4400, -0.1027),
        (-1.2552, 1.2923),
        (-0.8296, 0.4836),
        (0.0359, 1.3246),
        (-0.1423, 1.4558),
        (-0.3631, 1.4440),
    ]

    res = differential_evolution(
        funct,
        bounds,
        strategy="best1bin",
        maxiter=1000,
        popsize=60,  # I picked 10x the parameter count.
        tol=1e-10,
        workers=-1,
        seed=42 + 1,
        args=(models,),
        updating="deferred",
    )

    logger.info(f"Optimization result:\n{res}")
