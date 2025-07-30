
# Brinias-engine: Symbolic Modeling Engine

Brinias-engine is a powerful Python library that uses Genetic Programming to automatically discover mathematical formulas that model your data. It can be used for both regression (predicting a number) and classification (predicting a category) tasks.

The key output is a simple, human-readable mathematical equation that represents the learned model.

### Core Features

*   **Symbolic Regression & Classification:** Finds the underlying formula in your data.
*   **Automated Feature Preprocessing:** Handles numerical, categorical, and text data automatically.
*   **Simple API:** Train a model and make predictions with just two main functions.
*   **Portable Models:** Exports the final formula into a standalone Python file (`generated_model.py`) that can be used anywhere without needing the `brinias-engine` library itself.
*   **Transparent & Interpretable:** The final model is a clear equation, not a black box.

## What is the Output? An Example Equation

Unlike traditional "black box" models (like deep neural networks), the primary output of `Brinias-engine` is a mathematical formula. This formula represents the best model found to describe the relationship between your features and the target.

For example, after running on financial data, `Brinias-engine` might discover a formula like this:

```
safe_exp(protected_log(sub(sub(sub(sub(sub(sub(Close, -1.408225548256985), cos(Close)), cos(sub(Close, sin(Open)))), safe_tan(cos(Close))), cos(sub(Close, sin(Open)))), cos(sub(Close, sin(Open))))))
```

This raw output uses protected functions (e.g., `protected_log` to avoid errors) and shows the exact combination of features (`Close`, `Open`) and mathematical operations (`sub`, `cos`, `safe_exp`) that form the predictive model. This equation is then compiled into the final portable Python model.

## 1. Installation

To get started, you need `git` and `python >= 3.7` installed on your system.

### Step 1: Create a Virtual Environment (Recommended)
It is strongly recommended to create a virtual environment to keep your project dependencies isolated.

 ```bash
# Create the virtual environment folder
python3 -m venv .venv

# Activate it on macOS/Linux
source .venv/bin/activate

# Or activate it on Windows
# .\.venv\Scripts\activate
```

### Step 2: Clone and Install
1.  **Clone the Repository:**
    Open your terminal and clone the project.
    ```bash
    git clone https://github.com/brinias/brinias-engine.git
    cd brinias-engine # Navigate into the project's root directory
    ```

2.  **Install the Library:**
    Install the library in "editable" mode (`-e`). This allows you to make changes to the source code and have them immediately apply without reinstalling.
    ```bash
    pip install -e .
    ```
    This command reads the `setup.py` file and installs `brinias` along with all its dependencies.

You are now ready to use the library!

## 2. How to Use Brinias-engine

Using `brinias-engine` is a simple, two-step process:
1.  **Train a Model** on your dataset.
2.  **Make Predictions** using the trained model.

The `examples/` directory contains `training.py`, `predict.py`, and `benchmark.py` to guide you.

### Step 1: Training a Model

The `train_model` function is the heart of the library. It takes your CSV data, finds the best formula, and saves all the resulting model files.

#### Example Training Script (`examples/training.py`)
This code trains a model using the `dataeth.csv` dataset.

```python
from brinias import train_model

print("--- STARTING MODEL TRAINING ---")

# The path to the data is relative to where you run the script
# e.g., run from the project root: python examples/training.py
train_model(
    csv_path="examples/dataeth.csv",
    target_column="next_close",
    output_dir="next_close_model", # Give the model a descriptive name
    generations=120,
    pop_size=100,
    show_plot=True
)

print("--- TRAINING COMPLETE ---")
```

#### What Happens After Training?
A new folder named **`next_close_model`** will be created. It contains everything needed to use your model:

*   `generated_model.py`: A standalone Python script containing your model's formula. **This is your portable model.**
*   `equation.txt`: A simple text file with the raw mathematical expression.
*   `vectorizers.pkl`, `original_cols.pkl`, etc.: Helper files that store the data preprocessing steps.
*   `evolution_history.csv`: A log of the model's performance during training.

### Step 2: Making Predictions

Once the model is trained, use the `make_prediction` function to predict outcomes for new, unseen data.

#### Example Prediction Script (`examples/predict.py`)

```python
from brinias import make_prediction

print("--- MAKING A NEW PREDICTION ---")

# The dictionary keys MUST match the column names from your training CSV
new_data_point = {
   "timestamp": "2025-05-14",
   "Open": 2679.71,
   "High": 2725.99,
   "Low": 2547.26,
   "Close": 2609.74,
   "Volume": 830047.1122,
}

# Point to the folder created during training
prediction = make_prediction(
    input_data=new_data_point,
    model_dir="next_close_model"
)

print("\n--- Prediction Result ---")
print(prediction)
```
The function will return a dictionary containing the prediction, for example: `{'prediction_type': 'regression', 'predicted_value': 2650.75}`.


## 3. Troubleshooting

*   **`ModuleNotFoundError: No module named 'brinias'`**: Make sure you ran `pip install -e .` from the project's root directory and that your virtual environment is active.
*   **`FileNotFoundError: [Errno 2] No such file or directory: 'my_data.csv'`**: Check that the `csv_path` in `train_model` is correct. The path is relative to where you run the `python` command from.
*   **`ValueError: Input data is missing expected column: 'Some_Column'`**: The dictionary passed to `make_prediction` must contain a key for *every single feature column* from your original training CSV (except the target).

## 📊 Benchmark Results

To demonstrate the effectiveness of `Brinias-engine`, a fair benchmark was conducted against several standard regression models. The goal is to predict the `next_close` price of Ethereum.

### Performance Metrics

The table below shows that **Brinias achieved the lowest Mean Squared Error (MSE) and the highest R² Score**, indicating the most accurate and reliable predictions on the test set.

| Model               | Time (s)   | MSE         | R² Score |
|---------------------|------------|-------------|----------|
| **Brinias**         | `244.17`   | `5972.45`   | `0.4801` |
| Linear Regression   | `0.00`     | `6161.01`   | `0.4637` |
| XGBoost             | `0.17`     | `7319.93`   | `0.3628` |
| Random Forest       | `0.15`     | `7394.59`   | `0.3563` |

### Visual Comparison

The plot below visually confirms the results. The yellow line (`Brinias Predictions`) frequently tracks the black line (`Actual Values`) more closely than the other models.

![Benchmark Plot](./Figure_0.png)

### Conclusion

Even on a challenging dataset, **Brinias successfully discovered a symbolic formula that outperformed standard machine learning models.** Its ability to find complex, non-linear relationships makes it a powerful tool for financial time-series analysis and other regression tasks where interpretability and accuracy are paramount.

---
*To reproduce these results, run the `benchmark.py` script located in the `examples/` directory. You will need to install `xgboost` via `pip install xgboost`.*
```