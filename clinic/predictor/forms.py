from django import forms

# -------- HEART ATTACK (UCI heart.csv) ----------
class HeartAttackForm(forms.Form):
    age = forms.IntegerField(min_value=1, max_value=120, label="Age")
    sex = forms.TypedChoiceField(choices=[(1, "Male"), (0, "Female")], coerce=int, label="Sex")
    cp = forms.TypedChoiceField(choices=[(0, "Typical angina"), (1, "Atypical angina"), (2, "Non-anginal pain"), (3, "Asymptomatic")], coerce=int, label="Chest Pain Type")
    trestbps = forms.IntegerField(label="Resting BP (mm Hg)", min_value=90, max_value=200)
    chol = forms.IntegerField(label="Cholesterol (mg/dl)", min_value=100, max_value=600)
    fbs = forms.TypedChoiceField(label="Fasting BS > 120 mg/dl", choices=[(1, "Yes"), (0, "No")], coerce=int)
    restecg = forms.TypedChoiceField(choices=[(0, "Normal"), (1, "ST-T abnormality"), (2, "LV hypertrophy")], coerce=int, label="Resting ECG")
    thalach = forms.IntegerField(label="Max Heart Rate", min_value=70, max_value=210)
    exang = forms.TypedChoiceField(label="Exercise-induced angina", choices=[(1, "Yes"), (0, "No")], coerce=int)
    oldpeak = forms.FloatField(label="ST depression", min_value=0, max_value=7)
    slope = forms.TypedChoiceField(choices=[(0, "Upsloping"), (1, "Flat"), (2, "Downsloping")], coerce=int, label="Slope")
    ca = forms.IntegerField(min_value=0, max_value=4, label="Num major vessels (0–4)")
    thal = forms.TypedChoiceField(choices=[(1, "Normal"), (2, "Fixed defect"), (3, "Reversible defect")], coerce=int, label="Thal")

# -------- HYPERTENSION ----------
class HypertensionForm(forms.Form):
    age = forms.IntegerField(min_value=18, max_value=80, label="Age")
    gender = forms.TypedChoiceField(choices=[(1, "Male"), (0, "Female")], coerce=int, label="Gender")
    bmi = forms.FloatField(min_value=15, max_value=50, label="BMI")
    systolic_bp = forms.IntegerField(min_value=90, max_value=200, label="Systolic BP")
    diastolic_bp = forms.IntegerField(min_value=60, max_value=120, label="Diastolic BP")
    smoker = forms.TypedChoiceField(choices=[(1, "Yes"), (0, "No")], coerce=int, label="Smoker")
    alcohol = forms.TypedChoiceField(choices=[(1, "Yes"), (0, "No")], coerce=int, label="Alcohol Consumer")
    physical_activity = forms.TypedChoiceField(choices=[(0, "Low"), (1, "Moderate"), (2, "High")], coerce=int, label="Physical Activity")

# -------- DIABETES ----------
class DiabetesForm(forms.Form):
    age = forms.IntegerField(min_value=1, max_value=120, label="Age")
    bmi = forms.FloatField(min_value=15, max_value=50, label="BMI")
    systolic_bp = forms.IntegerField(min_value=90, max_value=200, label="Systolic BP")
    diastolic_bp = forms.IntegerField(min_value=60, max_value=120, label="Diastolic BP")
    fasting_blood_sugar = forms.FloatField(min_value=50, max_value=300, label="Fasting Blood Sugar")
    hba1c = forms.FloatField(min_value=3, max_value=15, label="HbA1c")
    serum_creatinine = forms.FloatField(min_value=0.5, max_value=10, label="Serum Creatinine")
    bun_levels = forms.FloatField(min_value=5, max_value=50, label="BUN Levels")
    gfr = forms.FloatField(min_value=10, max_value=150, label="GFR")
    protein_in_urine = forms.FloatField(min_value=0, max_value=10, label="Protein in Urine")
    acr = forms.FloatField(min_value=0, max_value=500, label="ACR")
    serum_electrolytes_sodium = forms.FloatField(min_value=120, max_value=160, label="Serum Sodium")
    serum_electrolytes_potassium = forms.FloatField(min_value=2, max_value=8, label="Serum Potassium")
    hemoglobin_levels = forms.FloatField(min_value=5, max_value=20, label="Hemoglobin Levels")
    cholesterol_total = forms.FloatField(min_value=100, max_value=400, label="Total Cholesterol")
    cholesterol_ldl = forms.FloatField(min_value=50, max_value=300, label="LDL Cholesterol")
    cholesterol_hdl = forms.FloatField(min_value=20, max_value=100, label="HDL Cholesterol")
    cholesterol_triglycerides = forms.FloatField(min_value=50, max_value=500, label="Triglycerides")

# -------- CHRONIC KIDNEY DISEASE ----------
class KidneyForm(forms.Form):
    age = forms.FloatField(min_value=2, max_value=90, label="Age")
    bp = forms.FloatField(min_value=50, max_value=180, label="Blood Pressure")
    bgr = forms.FloatField(min_value=22, max_value=490, label="Blood Glucose Random")
    bu = forms.FloatField(min_value=1.5, max_value=391, label="Blood Urea")
    sc = forms.FloatField(min_value=0.4, max_value=76, label="Serum Creatinine")
    sod = forms.FloatField(min_value=4.5, max_value=163, label="Sodium")
    pot = forms.FloatField(min_value=2.5, max_value=47, label="Potassium")
    hemo = forms.FloatField(min_value=3.1, max_value=17.8, label="Hemoglobin")
    wc = forms.FloatField(min_value=2200, max_value=26400, label="WBC count")
    rc = forms.FloatField(min_value=2.1, max_value=8, label="RBC count")
    htn = forms.TypedChoiceField(label="Hypertension", choices=[(1, "Yes"), (0, "No")], coerce=int)
    dm = forms.TypedChoiceField(label="Diabetes Mellitus", choices=[(1, "Yes"), (0, "No")], coerce=int)
    cad = forms.TypedChoiceField(label="Coronary Artery Disease", choices=[(1, "Yes"), (0, "No")], coerce=int)
    appet = forms.TypedChoiceField(label="Appetite", choices=[(1, "Good"), (0, "Poor")], coerce=int)
    ane = forms.TypedChoiceField(label="Anemia", choices=[(1, "Yes"), (0, "No")], coerce=int)
