# brinias/file_utils.py

import pandas as pd
import numpy as np
import pickle
import re
import os
from datetime import datetime
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer

def safe_name(s):
    return re.sub(r"\W|^(?=\d)", "_", s)

def preprocess_input(value):
    if isinstance(value, str):
        try: return datetime.strptime(value, "%Y-%m-%d").timestamp()
        except ValueError:
            try: return float(value)
            except ValueError: return hash(value) % 1000
    elif isinstance(value, (int, float)): return value
    elif isinstance(value, bool): return int(value)
    else: return 0.0

def fit_and_transform_data(file_path: str, target_column: str, output_dir: str):
    """
    Loads data, FITS all transformers, saves them to output_dir,
    and returns the transformed training data.
    """
    # --- THE FIX ---
    os.makedirs(output_dir, exist_ok=True)
    # ---------------

    try:
        df = pd.read_csv(file_path, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding="latin1")

    if target_column not in df.columns:
        raise ValueError(f"Target column '{target_column}' not found.")

    y_raw = df[target_column]
    X_raw = df.drop(columns=[target_column])

    feature_names = []
    final_X_parts = []
    vectorizers = {}
    original_cols = list(X_raw.columns)

    for col in original_cols:
        if X_raw[col].dtype == 'object' and X_raw[col].fillna('').str.len().mean() > 15:
            vectorizer = TfidfVectorizer(max_features=100, stop_words="english", ngram_range=(1, 2), lowercase=True)
            text_features = vectorizer.fit_transform(X_raw[col].astype(str))
            tfidf_names = [f"{col}_tfidf_{safe_name(w)}" for w in vectorizer.get_feature_names_out()]
            final_X_parts.append(text_features.toarray())
            feature_names.extend(tfidf_names)
            vectorizers[col] = vectorizer
        else:
            encoded = X_raw[col].apply(preprocess_input).values.reshape(-1, 1)
            final_X_parts.append(encoded)
            feature_names.append(col)

    X = np.hstack(final_X_parts)

    if not np.issubdtype(y_raw.dtype, np.number) or len(np.unique(y_raw)) < 20:
        task_type = "classification"
        label_encoder = LabelEncoder()
        y = label_encoder.fit_transform(y_raw.astype(str))
        with open(os.path.join(output_dir, "label_encoder.pkl"), "wb") as f:
            pickle.dump(label_encoder, f)
    else:
        task_type = "regression"
        y = y_raw.values.astype(float)

    with open(os.path.join(output_dir, "vectorizers.pkl"), "wb") as f: pickle.dump(vectorizers, f)
    with open(os.path.join(output_dir, "task_type.pkl"), "wb") as f: pickle.dump(task_type, f)
    with open(os.path.join(output_dir, "original_cols.pkl"), "wb") as f: pickle.dump(original_cols, f)

    return X, y, feature_names, task_type

def transform_new_data(df: pd.DataFrame, model_dir: str):
    """
    Transforms a new DataFrame using PRE-FITTED transformers loaded from model_dir.
    """
    with open(os.path.join(model_dir, "vectorizers.pkl"), "rb") as f: vectorizers = pickle.load(f)
    with open(os.path.join(model_dir, "original_cols.pkl"), "rb") as f: original_cols = pickle.load(f)

    for col in original_cols:
        if col not in df.columns:
            raise ValueError(f"Input data is missing expected column: '{col}'")

    X_raw = df[original_cols]

    final_X_parts = []
    for col in original_cols:
        if col in vectorizers:
            vec = vectorizers[col]
            tfidf = vec.transform(X_raw[col].astype(str)).toarray()
            final_X_parts.append(tfidf)
        else:
            encoded = X_raw[col].apply(preprocess_input).values.reshape(-1, 1)
            final_X_parts.append(encoded)

    X_transformed = np.hstack(final_X_parts)
    return X_transformed