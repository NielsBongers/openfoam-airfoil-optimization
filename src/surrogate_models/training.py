import json
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, mean_absolute_error, mean_squared_error
from sklearn.model_selection import GridSearchCV, train_test_split

from src.utils.logging_setup import get_logger


def create_split(df, feature_cols, target_col, test_size=0.2, random_state=42):
    X = df[feature_cols].values
    y = df[target_col].values
    return train_test_split(X, y, test_size=test_size, random_state=random_state)


def run_cv_for_models(X_cls_train, y_cls_train, X_reg_train, y_reg_train, cv=5):
    param_grid = {
        "n_estimators": [
            5,
            10,
            20,
            50,
            100,
            200,
            300,
        ],
        "max_depth": [5, 10, 15],
        "min_samples_split": [
            2,
            5,
            10,
        ],
        "min_samples_leaf": [
            1,
            2,
            4,
        ],
        "max_features": [
            None,
            "sqrt",
            "log2",
        ],
        "bootstrap": [
            True,
            False,
        ],
    }

    clf = RandomForestClassifier()
    grid_clf = GridSearchCV(clf, param_grid, cv=cv, n_jobs=-1, verbose=10)
    grid_clf.fit(X_cls_train, y_cls_train)
    best_params_cls = grid_clf.best_params_

    reg = RandomForestRegressor()
    grid_reg = GridSearchCV(reg, param_grid, cv=cv, n_jobs=-1, verbose=10)
    grid_reg.fit(X_reg_train, y_reg_train)
    best_params_reg = grid_reg.best_params_

    return best_params_cls, best_params_reg


def load_or_run_cv(
    model_params_path, X_cls_train, y_cls_train, X_reg_train, y_reg_train
):
    if model_params_path.exists():
        with open(model_params_path, "r") as f:
            saved_params = json.load(f)
        best_params_cls = saved_params["classifier"]
        best_params_reg = saved_params["regressor"]
    else:
        model_params_path.parent.mkdir(parents=True, exist_ok=True)
        best_params_cls, best_params_reg = run_cv_for_models(
            X_cls_train, y_cls_train, X_reg_train, y_reg_train
        )
        with open(model_params_path, "w") as f:
            json.dump(
                {
                    "classifier": best_params_cls,
                    "regressor": best_params_reg,
                },
                f,
            )
    return best_params_cls, best_params_reg


def train_models(dataset_path: Path = Path("results/csv/results.csv")):
    logger = get_logger(__name__)

    df = pd.read_csv(dataset_path)

    status_columns = [
        "no_clipping",
        "block_mesh",
        "check_mesh",
        "simple",
        "convergence",
    ]
    feature_columns = ["x0", "x1", "x2", "x3", "x4", "x5"]
    df["cl_cd"] = df["cl"] / df["cd"]
    df["failed"] = ~df[status_columns].all(axis=1)

    df_completed = df[~df["failed"]]

    X_cls_train, X_cls_test, y_cls_train, y_cls_test = create_split(
        df,
        feature_columns,
        "failed",
    )

    X_reg_train, X_reg_test, y_reg_train, y_reg_test = create_split(
        df_completed,
        feature_columns,
        "cl_cd",
    )

    model_params_path = Path("results/model_params/model_parameters.json")
    best_params_cls, best_params_reg = load_or_run_cv(
        model_params_path, X_cls_train, y_cls_train, X_reg_train, y_reg_train
    )

    final_cls_model = RandomForestClassifier(**best_params_cls, n_jobs=1)
    final_cls_model.fit(X_cls_train, y_cls_train)

    final_reg_model = RandomForestRegressor(**best_params_reg, n_jobs=1)
    final_reg_model.fit(X_reg_train, y_reg_train)

    y_cls_pred = final_cls_model.predict(X_cls_test)
    cls_accuracy = accuracy_score(y_cls_test, y_cls_pred)
    logger.info(f"Classification accuracy: {cls_accuracy:.4f}")

    y_reg_pred = final_reg_model.predict(X_reg_test)
    reg_mse = mean_squared_error(y_reg_test, y_reg_pred)
    reg_mae = mean_absolute_error(y_reg_test, y_reg_pred)
    logger.info(f"Regression MSE: {reg_mse:.4f}")
    logger.info(f"Regression MAE: {reg_mae:.4f}")

    return final_cls_model, final_reg_model
