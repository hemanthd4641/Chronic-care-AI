import joblib
from django.conf import settings
from pathlib import Path

# Cached models
_MODEL_CACHE = {}

def load_model(model_name: str):
    """
    Loads a joblib pipeline from settings.ML_MODELS_DIR / f"{model_name}.joblib"
    Caches in memory for performance.
    """
    if model_name in _MODEL_CACHE:
        return _MODEL_CACHE[model_name]
    model_path = Path(settings.ML_MODELS_DIR) / f"{model_name}.joblib"
    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")
    pipeline = joblib.load(model_path)
    _MODEL_CACHE[model_name] = pipeline
    return pipeline
