import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
import joblib
from pathlib import Path

# Load Diabetes dataset (using the existing diabetes.csv)
CSV = "data/diabetes.csv"
df = pd.read_csv(CSV)

# Target column
target = "Diagnosis"

# Select relevant features for diabetes prediction
feature_cols = [
    "Age", "BMI", "SystolicBP", "DiastolicBP", 
    "FastingBloodSugar", "HbA1c", "SerumCreatinine", 
    "BUNLevels", "GFR", "ProteinInUrine", "ACR",
    "SerumElectrolytesSodium", "SerumElectrolytesPotassium",
    "HemoglobinLevels", "CholesterolTotal", "CholesterolLDL",
    "CholesterolHDL", "CholesterolTriglycerides"
]

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
joblib.dump(pipe, "ml_models/diabetes_rf.joblib")
print("✅ Saved ml_models/diabetes_rf.joblib")

# Print accuracy
accuracy = pipe.score(Xte, yte)
print(f"✅ Diabetes Model Accuracy: {accuracy:.3f}")