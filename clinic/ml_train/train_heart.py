import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
import joblib
from pathlib import Path

# Load Heart Disease dataset
CSV = "data/heart.csv"
df = pd.read_csv(CSV)

# Target column
target = "target"

# Feature columns (excluding target)
feature_cols = [col for col in df.columns if col != target]
X = df[feature_cols].copy()
y = df[target]

# Pipeline (scaling + classifier)
pipe = Pipeline([
    ("scaler", StandardScaler()),
    ("clf", RandomForestClassifier(
        n_estimators=300, 
        random_state=42, 
        class_weight="balanced"
    )),
])

# Train/test split
Xtr, Xte, ytr, yte = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Train model
pipe.fit(Xtr, ytr)

# Save trained model
Path("ml_models").mkdir(exist_ok=True)
joblib.dump(pipe, "ml_models/heart_rf.joblib")
print("✅ Saved ml_models/heart_rf.joblib")

# Print accuracy
accuracy = pipe.score(Xte, yte)
print(f"✅ Heart Disease Model Accuracy: {accuracy:.3f}")