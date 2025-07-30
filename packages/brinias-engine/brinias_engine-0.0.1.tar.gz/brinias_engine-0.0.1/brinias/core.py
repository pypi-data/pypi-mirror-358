# brinias/core.py

import textwrap
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from scipy.sparse import hstack
import numpy as np
import math
import random
from functools import partial
from datetime import datetime
from typing import List
import pandas as pd
import operator
import warnings
from deap import gp, base, creator, tools, algorithms
from sklearn.model_selection import KFold
from sklearn.metrics import mean_squared_error, accuracy_score

# (All protected math functions: protected_div, protected_log, etc. go here unchanged)
def protected_div(a, b):
    try:
        if b == 0 or np.isnan(b) or np.isinf(a) or np.isinf(b): return 1.0
        return a / b
    except: return 1.0
def protected_log(x):
    try: return math.log(abs(x)) if x != 0 else 0.0
    except: return 0.0
def protected_sqrt(x):
    try: return math.sqrt(abs(x))
    except: return 0.0
def safe_exp(x):
    try: return math.exp(min(x, 50))
    except: return 1.0
def safe_tan(x):
    try: return math.tan(x)
    except: return 0.0
def if_then_else(condition, out1, out2):
    return out1 if condition else out2
def preprocess_input(value):
    if isinstance(value, str):
        try: return datetime.strptime(value, "%Y-%m-%d").timestamp()
        except ValueError:
            try: return float(value)
            except ValueError: return hash(value) % 1000
    elif isinstance(value, (int, float)): return value
    elif isinstance(value, bool): return int(value)
    else: return 0.0

###############################################
#  Brinias Core Class                         #
###############################################

class Brinias: # <-- RENAMED CLASS
    def __init__(
        self,
        n_features: int,
        feature_names: List[str] = None,
        task: str = "regression",
        pop_size: int = 300,
        generations: int = 100,
        cv_folds: int = 5,
        seed: int = 42,
    ):
        # (The rest of the class is identical to DigitalEinstein, no other changes needed inside)
        self.n_features = n_features
        self.feature_names = feature_names or [f"x{i}" for i in range(n_features)]
        self.task = task
        self.pop_size = pop_size
        self.generations = generations
        self.cv_folds = cv_folds
        self.random_state = seed
        self.history = []
        self.best_expr = None
        self.best_func = None

        random.seed(seed)
        np.random.seed(seed)

        self.pset = self._build_primitive_set()
        self.toolbox = self._build_toolbox()
        self.hall_of_fame = tools.HallOfFame(1)

    def _build_primitive_set(self):
        pset = gp.PrimitiveSet("MAIN", self.n_features)
        for i, name in enumerate(self.feature_names):
            pset.renameArguments(**{f"ARG{i}": name})
        pset.addPrimitive(operator.add, 2)
        pset.addPrimitive(operator.sub, 2)
        pset.addPrimitive(operator.mul, 2)
        pset.addPrimitive(protected_div, 2)
        pset.addPrimitive(operator.neg, 1)
        pset.addPrimitive(math.sin, 1)
        pset.addPrimitive(math.cos, 1)
        pset.addPrimitive(safe_tan, 1)
        pset.addPrimitive(safe_exp, 1)
        pset.addPrimitive(protected_log, 1)
        pset.addPrimitive(protected_sqrt, 1)
        pset.addPrimitive(abs, 1)
        pset.addPrimitive(if_then_else, 3)
        pset.addEphemeralConstant("rand", partial(random.uniform, -2.0, 2.0))
        return pset

    def _build_toolbox(self):
        if not hasattr(creator, "FitnessMin"):
            creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        if not hasattr(creator, "Individual"):
            creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMin)
        toolbox = base.Toolbox()
        toolbox.register("expr", gp.genHalfAndHalf, pset=self.pset, min_=1, max_=3)
        toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)
        toolbox.register("compile", gp.compile, pset=self.pset)
        toolbox.register("select", tools.selTournament, tournsize=5)
        toolbox.register("mate", gp.cxOnePoint)
        toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr, pset=self.pset)
        toolbox.decorate("mate", gp.staticLimit(key=len, max_value=30))
        toolbox.decorate("mutate", gp.staticLimit(key=len, max_value=30))
        return toolbox

    def fit(self, X: np.ndarray, y: np.ndarray):
        assert X.shape[1] == self.n_features, "Feature mismatch"
        def evaluate(ind):
            func = self.toolbox.compile(expr=ind)
            kf = KFold(n_splits=self.cv_folds, shuffle=True, random_state=self.random_state)
            scores = []
            for train_idx, test_idx in kf.split(X):
                X_train, y_train = X[train_idx], y[train_idx]
                try:
                    y_pred = np.array([func(*row) for row in X_train])
                except:
                    return (float("inf"),)
                if np.any(np.isnan(y_pred)) or np.any(np.isinf(y_pred)):
                    return (float("inf"),)
                if self.task == "regression":
                    score = mean_squared_error(y_train, y_pred)
                else:
                    y_pred_labels = (y_pred > 0.5).astype(int)
                    score = 1 - accuracy_score(y_train, y_pred_labels)
                scores.append(score)
            return (float(np.mean(scores)),)
        self.toolbox.register("evaluate", evaluate)
        pop = self.toolbox.population(n=self.pop_size)
        stats = tools.Statistics(lambda ind: ind.fitness.values[0])
        stats.register("avg", np.mean)
        stats.register("min", np.min)
        stats.register("max", np.max)
        pop, logbook = algorithms.eaSimple(
            pop, self.toolbox, cxpb=0.5, mutpb=0.3, ngen=self.generations,
            stats=stats, halloffame=self.hall_of_fame, verbose=True,
        )
        for record in logbook:
            self.history.append(dict(record))
        self.best_expr = self.hall_of_fame[0]
        self.best_func = self.toolbox.compile(expr=self.best_expr)
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        assert self.best_func is not None, "Model not fitted."
        preds = np.array([self.best_func(*row) for row in X])
        preds = np.clip(preds, -1e6, 1e6)
        if self.task == "classification":
            return (preds > 0.5).astype(int)
        return preds

    # (export_to_python, expression_str, etc. are all unchanged)
    def expression_str(self) -> str:
        return str(self.best_expr)
    def save_history(self, path: str):
        pd.DataFrame(self.history).to_csv(path, index=False)
    def export_to_python(self, filename: str):
        helpers = textwrap.dedent("""
            import math
            from datetime import datetime

            def protected_div(a, b):
                if b == 0 or abs(b) < 1e-12 or math.isnan(b) or math.isinf(b):
                    return 1.0
                return a / b

            def protected_log(x):
                return math.log(abs(x)) if x != 0 else 0.0

            def protected_sqrt(x):
                return math.sqrt(abs(x))

            def safe_exp(x):
                try:
                    return math.exp(min(x, 50))
                except:
                    return 1.0

            def safe_tan(x):
                try:
                    return math.tan(x)
                except:
                    return 0.0

            def if_then_else(cond, t, f): return t if cond else f
            def abs_fn(x): return abs(x)
            def add(a, b): return a + b
            def sub(a, b): return a - b
            def mul(a, b): return a * b
            def neg(a): return -a
            def cos(x): return math.cos(x)
            def sin(x): return math.sin(x)

            def preprocess_input(val):
                if isinstance(val, str):
                    try:
                        return datetime.strptime(val, "%Y-%m-%d").timestamp()
                    except:
                        try: return float(val)
                        except: return hash(val) % 1000
                if isinstance(val, bool): return int(val)
                return float(val) if isinstance(val, (int, float)) else 0.0
        """)

        inputs = ", ".join(self.feature_names)
        expr = self.expression_str().replace("abs", "abs_fn")

        model_code = textwrap.dedent(f"""
            def model(*args):
                x = [preprocess_input(v) for v in args]
                {inputs} = x
                return {expr}
        """)

        with open(filename, "w") as f:
            f.write(helpers)
            f.write("\n\n")
            f.write(model_code)

        print(f"✅ Model exported to: {filename}")

        
    def expression_math(self) -> str:
        """
        Return a clean mathematical representation of the symbolic expression.
        """
        import re

        expr = str(self.best_expr)

        # Mapping DEAP primitive names to math symbols/functions
        replacements = {
            "add": "+",
            "sub": "-",
            "mul": "*",
            "neg": "-",
            "abs_fn": "abs",
            "protected_div": "/",
            "protected_log": "log",
            "protected_sqrt": "sqrt",
            "safe_exp": "exp",
            "safe_tan": "tan",
            "cos": "cos",
            "sin": "sin",
            "if_then_else": "if_then_else",
        }

        # Αντικατάσταση ονομάτων συναρτήσεων
        for func, symbol in replacements.items():
            expr = re.sub(rf"\b{func}\b", symbol, expr)

        # Προσθήκη spacing και clean εμφάνιση
        expr = expr.replace(",", " , ")
        expr = expr.replace("(", "( ").replace(")", " )")
        expr = re.sub(r"\s+", " ", expr)

        return expr.strip()




