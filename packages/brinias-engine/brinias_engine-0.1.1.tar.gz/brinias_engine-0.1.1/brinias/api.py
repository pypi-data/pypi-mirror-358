# brinias/api.py

import os
import pickle
import numpy as np
import pandas as pd
import importlib.util
from sklearn.metrics import accuracy_score, mean_squared_error, r2_score
import matplotlib.pyplot as plt
from typing import Dict, Any

from .core import Brinias
# CORRECTED: Import the right functions from the right file
from .file_utils import fit_and_transform_data, transform_new_data

def train_model(
    csv_path: str,
    target_column: str,
    output_dir: str = "brinias_model_files",
    generations: int = 120,
    pop_size: int = 100,
    cv_folds: int = 5,
    seed: int = 42,
    show_plot: bool = True,
):
    """ Trains a Brinias model on a dataset. """
    os.makedirs(output_dir, exist_ok=True)

    print("--- Loading and Preprocessing Data ---")
    # CORRECTED: Call the correct function
    X, y, feature_names, task_type = fit_and_transform_data(csv_path, target_column, output_dir)

    print(f"Data loaded. Found {X.shape[0]} samples and {X.shape[1]} features.")
    print(f"Task type detected: {task_type}")

    model = Brinias(
        n_features=X.shape[1],
        feature_names=feature_names,
        task=task_type,
        generations=generations,
        pop_size=pop_size,
        cv_folds=cv_folds,
        seed=seed
    )

    print("\n--- Starting Brinias Evolutionary Search ---")
    model.fit(X, y)

    print("\n--- Saving Model and Artifacts ---")
    model.save_history(os.path.join(output_dir, "evolution_history.csv"))
    model.export_to_python(os.path.join(output_dir, "generated_model.py"))
    with open(os.path.join(output_dir, "equation.txt"), "w") as f:
        f.write(model.expression_str())
    print(f"Artifacts saved in: {output_dir}")

    print("\n--- Evaluating Model Performance ---")
    if task_type == "classification":
        raw_predictions = np.array([model.best_func(*row) for row in X])
        thresholds = np.linspace(min(raw_predictions), max(raw_predictions), 200)
        best_acc, best_thresh = 0, 0.5
        for t in thresholds:
            acc = accuracy_score(y, (raw_predictions > t).astype(int))
            if acc > best_acc: best_acc, best_thresh = acc, t
        with open(os.path.join(output_dir, "threshold.pkl"), "wb") as f: pickle.dump(best_thresh, f)
        print(f"Best Threshold: {best_thresh:.4f}")
        print(f"Accuracy with Best Threshold: {best_acc:.4f}")
    else:
        predictions = model.predict(X)
        mse = mean_squared_error(y, predictions)
        r2 = r2_score(y, predictions)
        print(f"MSE: {mse:.4f}")
        print(f"R² Score: {r2:.4f}")

    if show_plot:
        plt.figure(figsize=(10, 6))
        plt.plot(y, 'o', label="Actual", alpha=0.6)
        plt.plot(model.predict(X), 'o', label="Predicted", alpha=0.6)
        plt.title("Actual vs. Predicted on Training Data")
        plt.legend()
        plt.show()

    print("\n✅ Training Complete.")
    return model


def make_prediction(input_data: Dict[str, Any], model_dir: str = "brinias_model_files"):
    """ Makes a prediction using a saved Brinias model. """
    print("--- Loading Model and Artifacts ---")
    model_path = os.path.join(model_dir, "generated_model.py")
    spec = importlib.util.spec_from_file_location("generated_model", model_path)
    generated_model = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(generated_model)

    print("--- Preprocessing Input Data ---")
    input_df = pd.DataFrame([input_data])
    X_transformed = transform_new_data(input_df, model_dir)

    print("--- Making Prediction ---")
    raw_prediction = generated_model.model(*X_transformed[0])

    print("--- Formatting Output ---")
    with open(os.path.join(model_dir, "task_type.pkl"), "rb") as f:
        task_type = pickle.load(f)

    if task_type == "regression":
        return {"prediction_type": "regression", "predicted_value": raw_prediction}
    else: # classification
        with open(os.path.join(model_dir, "threshold.pkl"), "rb") as f:
            threshold = pickle.load(f)
        predicted_class = int(raw_prediction > threshold)

        output = {"prediction_type": "classification", "predicted_class": predicted_class, "raw_score": raw_prediction}

        try:
            le_path = os.path.join(model_dir, "label_encoder.pkl")
            with open(le_path, "rb") as f: le = pickle.load(f)
            output["predicted_label"] = le.inverse_transform([predicted_class])[0]
        except FileNotFoundError:
            output["predicted_label"] = f"Class_{predicted_class}"

        return output