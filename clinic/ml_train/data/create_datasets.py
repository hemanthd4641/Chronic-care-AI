import pandas as pd
import numpy as np

# Set random seed for reproducibility
np.random.seed(42)

# Create Heart Disease dataset (UCI Heart Disease)
print("Creating Heart Disease dataset...")
n_samples = 1000

heart_data = {
    'age': np.random.randint(29, 80, n_samples),
    'sex': np.random.choice([0, 1], n_samples),
    'cp': np.random.choice([0, 1, 2, 3], n_samples),
    'trestbps': np.random.randint(94, 200, n_samples),
    'chol': np.random.randint(126, 564, n_samples),
    'fbs': np.random.choice([0, 1], n_samples),
    'restecg': np.random.choice([0, 1, 2], n_samples),
    'thalach': np.random.randint(71, 202, n_samples),
    'exang': np.random.choice([0, 1], n_samples),
    'oldpeak': np.random.uniform(0, 6.2, n_samples),
    'slope': np.random.choice([0, 1, 2], n_samples),
    'ca': np.random.choice([0, 1, 2, 3, 4], n_samples),
    'thal': np.random.choice([1, 2, 3], n_samples),
    'target': np.random.choice([0, 1], n_samples, p=[0.6, 0.4])
}

df_heart = pd.DataFrame(heart_data)
df_heart.to_csv('heart.csv', index=False)
print("✅ Heart dataset created")

# Create Hypertension dataset
print("Creating Hypertension dataset...")
hypertension_data = {
    'age': np.random.randint(18, 80, n_samples),
    'gender': np.random.choice([0, 1], n_samples),
    'bmi': np.random.uniform(18.5, 40, n_samples),
    'systolic_bp': np.random.randint(90, 200, n_samples),
    'diastolic_bp': np.random.randint(60, 120, n_samples),
    'smoker': np.random.choice([0, 1], n_samples),
    'alcohol': np.random.choice([0, 1], n_samples),
    'physical_activity': np.random.choice([0, 1, 2], n_samples),
    'target': np.random.choice([0, 1], n_samples, p=[0.7, 0.3])
}

df_hypertension = pd.DataFrame(hypertension_data)
df_hypertension.to_csv('hypertension.csv', index=False)
print("✅ Hypertension dataset created")

# Create Kidney Disease dataset (CKD)
print("Creating Kidney Disease dataset...")
kidney_data = {
    'age': np.random.uniform(2, 90, n_samples),
    'bp': np.random.uniform(50, 180, n_samples),
    'bgr': np.random.uniform(22, 490, n_samples),
    'bu': np.random.uniform(1.5, 391, n_samples),
    'sc': np.random.uniform(0.4, 76, n_samples),
    'sod': np.random.uniform(4.5, 163, n_samples),
    'pot': np.random.uniform(2.5, 47, n_samples),
    'hemo': np.random.uniform(3.1, 17.8, n_samples),
    'wc': np.random.uniform(2200, 26400, n_samples),
    'rc': np.random.uniform(2.1, 8, n_samples),
    'htn': np.random.choice([0, 1], n_samples),
    'dm': np.random.choice([0, 1], n_samples),
    'cad': np.random.choice([0, 1], n_samples),
    'appet': np.random.choice([0, 1], n_samples),
    'ane': np.random.choice([0, 1], n_samples),
    'target': np.random.choice([0, 1], n_samples, p=[0.6, 0.4])
}

df_kidney = pd.DataFrame(kidney_data)
df_kidney.to_csv('kidney.csv', index=False)
print("✅ Kidney dataset created")

print("\nAll datasets created successfully!")
