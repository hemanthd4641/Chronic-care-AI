# Chronic Care AI

A comprehensive Django-based healthcare system focused on chronic disease support and AI-assisted clinical workflows. The project combines standard web features (appointments, messaging, admission management) with machine learning disease prediction models and an AI chatbot assistant.

## Key features

- Disease Prediction Room: Heart disease, Diabetes, Hypertension, Kidney disease prediction with model training scripts and saved joblib pipelines.
- Prediction History: Users can view and export past predictions and confidence scores.
- Appointment Booking: Patients book appointments with assigned doctors; doctors can manage appointments.
- Private Messaging: Secure doctor-patient messaging with read/unread states.
- Community Chat Room: Real-time group chat for users.
- Medical Store: Browse and add medicines to cart, with simple inventory management.
- User Profile Management: Update personal info, profile picture, and preferences.
- AI Agent Assistant (chatbot): AI-powered assistant for doctors and patients to access patient info, messages, appointments, and prediction history.

## Project layout (important folders)

- `clinic/` - Django project core (settings, URLs, WSGI/ASGI).
- `admission/`, `appointments/`, `chatbot/`, `chatroom/`, `health_tracker/`, `medical_store/`, `messaging/`, `predictor/`, `userprofile/` - Django apps providing the main features.
- `ml_train/` - Training scripts and `ml_models/` output directory for saved joblib models.
- `templates/`, `static/` - Frontend templates and static assets.

## Tech stack

- Python 3.x
- Django 5.x (web framework)
- SQLite (default development DB)
- Machine learning: scikit-learn, joblib, pandas, numpy
- Optional / advanced AI: PyTorch, HuggingFace Transformers, sentence-transformers, FAISS, LangChain (chatbot/embeddings)
- Frontend: Django templates (server-rendered)

Dependencies (not exhaustive) are declared in `requirements.txt`. Major packages include:

- Django
- scikit-learn
- pandas
- numpy
- joblib
- torch, transformers, sentence-transformers, faiss-cpu, langchain

## ML models and training

- Training scripts live in `clinic/ml_train/`:
  - `train_diabetes.py` -> produces `ml_models/diabetes_rf.joblib`
  - `train_heart.py` -> produces `ml_models/heart_rf.joblib`
  - `train_hypertension.py` -> produces `ml_models/hypertension_rf.joblib`
  - `train_kidney.py` -> produces `ml_models/kidney_rf.joblib`
- Trained models are saved as joblib pipelines in `ml_models/`. The project settings define the ML models directory (see `clinic/clinic/settings.py`): `ML_MODELS_DIR = BASE_DIR / 'ml_train' / 'ml_models'`.
- At runtime models are loaded with `predictor.utils.load_model(model_name)` which caches models for performance.

## Installation (development, Windows PowerShell)

1. Create and activate a virtual environment (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Apply migrations and create a superuser:

```powershell
python clinic/manage.py migrate
python clinic/manage.py createsuperuser
```

4. Run the development server:

```powershell
python clinic/manage.py runserver
```

Visit http://127.0.0.1:8000/ and log in to access the features.

## Training models

Train models locally (ensure `data/` CSVs exist and are formatted as the training scripts expect):

```powershell
python clinic/ml_train/train_diabetes.py
python clinic/ml_train/train_heart.py
python clinic/ml_train/train_hypertension.py
python clinic/ml_train/train_kidney.py
```

Each script will save a joblib file into `clinic/ml_train/ml_models/` (or `ml_models/` depending on current working directory). Confirm `clinic/clinic/settings.py` `ML_MODELS_DIR` if models are not found at runtime.

## Running predictions (high-level)

- The web UI exposes a Prediction Room where logged-in users can select the disease type, enter health parameters, and get a risk assessment.
- Prediction history for users is stored and viewable via the Prediction History page.

## Chatbot / AI Assistant

- The `chatbot/` app contains an AI agent capable of answering queries about patients, appointments, messages, and predictions. It also includes project info JSON used by the assistant.
- Advanced features (embedding search, LLMs) rely on optional packages (transformers, sentence-transformers, FAISS, LangChain) and may require additional configuration (API keys, model downloads).

## Configuration notes

- Settings default to development mode (`DEBUG = True`). Replace the secret key and set `DEBUG = False` for production.
- Database: default SQLite (`db.sqlite3`), change `DATABASES` in `clinic/clinic/settings.py` for production.

## Tests

- Some apps include tests (e.g., `chatbot/tests.py`). Run tests with:

```powershell
python clinic/manage.py test
```

## Next steps / suggestions

- Add a LICENSE file and contribution guidelines.
- Add environment configuration (example `.env`) and update `settings.py` to read secrets from environment variables.
- CI: add automated tests and a linting stage.

## Contact / Authors

This README was generated from the project sources. For issues or contributions, open an issue or a pull request in the repository.

---

Generated summary of features and tech stack based on project files and training scripts found in the repository.
