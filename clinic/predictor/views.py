from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import Http404, HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.db.models import Count, Q
import json
import csv
import io
from datetime import datetime, timedelta
from .forms import HeartAttackForm, HypertensionForm, DiabetesForm, KidneyForm
from .utils import load_model
from .models import PredictionHistory

DISEASES = {
    "heart": {
        "title": "Heart Attack Risk",
        "model": "heart_rf",
        "form": HeartAttackForm,
        "template": "predictor/heart_disease.html",
        "feature_order": ["age","sex","cp","trestbps","chol","fbs","restecg",
                          "thalach","exang","oldpeak","slope","ca","thal"],
    },
    "hypertension": {
        "title": "Hypertension Risk",
        "model": "hypertension_rf",
        "form": HypertensionForm,
        "template": "predictor/hypertension.html",
        "feature_order": ["age","gender","bmi","systolic_bp","diastolic_bp","smoker","alcohol","physical_activity"],
    },
    "diabetes": {
        "title": "Diabetes Risk",
        "model": "diabetes_rf",
        "form": DiabetesForm,
        "template": "predictor/diabetes.html",
        "feature_order": ["age","bmi","systolic_bp","diastolic_bp","fasting_blood_sugar","hba1c",
                          "serum_creatinine","bun_levels","gfr","protein_in_urine","acr",
                          "serum_electrolytes_sodium","serum_electrolytes_potassium",
                          "hemoglobin_levels","cholesterol_total","cholesterol_ldl",
                          "cholesterol_hdl","cholesterol_triglycerides"],
    },
    "kidney": {
        "title": "Chronic Kidney Disease",
        "model": "kidney_rf",
        "form": KidneyForm,
        "template": "predictor/kidney_disease.html",
        "feature_order": ["age","bp","bgr","bu","sc","sod","pot","hemo","wc","rc","htn","dm","cad","appet","ane"],
    },
}

@login_required
def index(request):
    # Shows 4 cards that link to each disease form
    context = {"diseases": DISEASES}
    return render(request, "predictor/index.html", context)

@login_required
def predict_disease(request, key: str):
    cfg = DISEASES.get(key)
    if not cfg:
        raise Http404("Unknown disease")

    FormCls = cfg["form"]
    title = cfg["title"]
    model_name = cfg["model"]
    feature_order = cfg["feature_order"]
    template = cfg["template"]

    context = {"title": title, "key": key}
    if request.method == "POST":
        form = FormCls(request.POST)
        if form.is_valid():
            try:
                # extract features in the exact order used by the training pipeline
                X = [[float(form.cleaned_data[f]) for f in feature_order]]
            except KeyError as e:
                missing_field = str(e).strip("'")
                return render(request, template, {
                    **context,
                    "form": form,
                    "done": False,
                    "error_message": f"Missing required field: {missing_field}. Please fill it and submit again.",
                })
            except ValueError as e:
                return render(request, template, {
                    **context,
                    "form": form,
                    "done": False,
                    "error_message": "One or more inputs have invalid numbers. Please correct highlighted fields.",
                })

            try:
                model = load_model(model_name)
                y_pred = model.predict(X)[0]
                proba = None
                if hasattr(model, "predict_proba"):
                    try:
                        proba = float(model.predict_proba(X)[0][1])
                    except Exception:
                        proba = None

                # Save prediction to history
                PredictionHistory.objects.create(
                    user=request.user,
                    disease_type=key,
                    prediction_result=int(y_pred),
                    confidence=proba,
                    input_data=form.cleaned_data
                )

                context.update({
                    "form": form,
                    "pred": int(y_pred),
                    "proba": f"{proba*100:.1f}%" if proba is not None else None,
                    "done": True,
                })
                return render(request, template, context)
            except FileNotFoundError:
                return render(request, template, {
                    **context,
                    "form": form,
                    "done": False,
                    "error_message": "Model file is missing. Please contact support to restore ML models.",
                })
            except Exception as e:
                return render(request, template, {
                    **context,
                    "form": form,
                    "done": False,
                    "error_message": "We couldn't compute a prediction due to an internal error. Please review inputs and try again.",
                })
        else:
            # Provide a concise, human-readable summary of first few field errors
            field_errors = []
            for field_name, errors in list(form.errors.items())[:5]:
                field_errors.append(f"{field_name.replace('_',' ').title()}: {errors[0]}")
            return render(request, template, {
                **context,
                "form": form,
                "done": False,
                "error_message": "Please fix the following: " + "; ".join(field_errors),
            })
    else:
        form = FormCls()

    context["form"] = form
    return render(request, template, context)

@login_required
def prediction_history(request):
    """Display user's prediction history with charts and comparison"""
    predictions = PredictionHistory.objects.filter(user=request.user).order_by('-created_at')
    
    # Get date range for filtering
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if date_from:
        predictions = predictions.filter(created_at__date__gte=date_from)
    if date_to:
        predictions = predictions.filter(created_at__date__lte=date_to)
    
    # Get statistics for charts
    disease_stats = predictions.values('disease_type').annotate(count=Count('id'))
    risk_stats = predictions.values('prediction_result').annotate(count=Count('id'))
    
    # Get monthly trends
    monthly_data = []
    for i in range(6):  # Last 6 months
        month_start = timezone.now() - timedelta(days=30*i)
        month_end = month_start + timedelta(days=30)
        count = predictions.filter(created_at__range=[month_start, month_end]).count()
        monthly_data.append({
            'month': month_start.strftime('%b %Y'),
            'count': count
        })
    monthly_data.reverse()
    
    context = {
        'predictions': predictions[:50],  # Show last 50 predictions
        'total_predictions': predictions.count(),
        'disease_stats': list(disease_stats),
        'risk_stats': list(risk_stats),
        'monthly_data': monthly_data,
        'date_from': date_from,
        'date_to': date_to,
    }
    return render(request, 'predictor/history.html', context)

@login_required
def download_report(request, format_type='pdf'):
    """Download prediction history as PDF or CSV"""
    predictions = PredictionHistory.objects.filter(user=request.user).order_by('-created_at')
    
    if format_type == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="prediction_history_{request.user.username}_{datetime.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Date', 'Disease Type', 'Prediction Result', 'Confidence', 'Risk Level'])
        
        for pred in predictions:
            risk_level = 'High Risk' if pred.prediction_result == 1 else 'Low Risk'
            confidence = f"{pred.confidence*100:.1f}%" if pred.confidence else 'N/A'
            writer.writerow([
                pred.created_at.strftime('%Y-%m-%d %H:%M'),
                pred.disease_type.title(),
                pred.prediction_result,
                confidence,
                risk_level
            ])
        
        return response
    
    elif format_type == 'json':
        data = []
        for pred in predictions:
            data.append({
                'date': pred.created_at.isoformat(),
                'disease_type': pred.disease_type,
                'prediction_result': pred.prediction_result,
                'confidence': pred.confidence,
                'risk_level': 'High Risk' if pred.prediction_result == 1 else 'Low Risk',
                'input_data': pred.input_data
            })
        
        response = HttpResponse(json.dumps(data, indent=2), content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="prediction_history_{request.user.username}_{datetime.now().strftime("%Y%m%d")}.json"'
        return response
    
    else:  # PDF format
        html_string = render_to_string('predictor/report_template.html', {
            'predictions': predictions,
            'user': request.user,
            'generated_at': datetime.now()
        })
        
        response = HttpResponse(html_string, content_type='text/html')
        response['Content-Disposition'] = f'attachment; filename="prediction_report_{request.user.username}_{datetime.now().strftime("%Y%m%d")}.html"'
        return response

@login_required
def chart_data(request):
    """API endpoint for chart data"""
    predictions = PredictionHistory.objects.filter(user=request.user)
    
    # Disease distribution
    disease_data = {}
    for pred in predictions:
        disease = pred.disease_type
        if disease not in disease_data:
            disease_data[disease] = {'total': 0, 'high_risk': 0}
        disease_data[disease]['total'] += 1
        if pred.prediction_result == 1:
            disease_data[disease]['high_risk'] += 1
    
    # Monthly trends
    monthly_trends = {}
    for pred in predictions:
        month_key = pred.created_at.strftime('%Y-%m')
        if month_key not in monthly_trends:
            monthly_trends[month_key] = {'total': 0, 'high_risk': 0}
        monthly_trends[month_key]['total'] += 1
        if pred.prediction_result == 1:
            monthly_trends[month_key]['high_risk'] += 1
    
    # Risk level distribution
    risk_distribution = {'low_risk': 0, 'high_risk': 0}
    for pred in predictions:
        if pred.prediction_result == 1:
            risk_distribution['high_risk'] += 1
        else:
            risk_distribution['low_risk'] += 1
    
    return JsonResponse({
        'disease_data': disease_data,
        'monthly_trends': monthly_trends,
        'risk_distribution': risk_distribution,
        'total_predictions': predictions.count()
    })

@login_required
def compare_predictions(request):
    """Compare predictions between different time periods or diseases"""
    predictions = PredictionHistory.objects.filter(user=request.user)
    
    # Get comparison parameters
    compare_type = request.GET.get('type', 'disease')  # disease, time_period
    period1 = request.GET.get('period1')
    period2 = request.GET.get('period2')
    
    comparison_data = {}
    
    if compare_type == 'disease':
        # Compare different diseases
        diseases = ['heart', 'diabetes', 'hypertension', 'kidney']
        for disease in diseases:
            disease_preds = predictions.filter(disease_type=disease)
            comparison_data[disease] = {
                'total': disease_preds.count(),
                'high_risk': disease_preds.filter(prediction_result=1).count(),
                'avg_confidence': sum(p.confidence for p in disease_preds if p.confidence) / max(disease_preds.count(), 1)
            }
    
    elif compare_type == 'time_period':
        # Compare different time periods
        if period1 and period2:
            # Implementation for time period comparison
            pass
    
    context = {
        'comparison_data': comparison_data,
        'compare_type': compare_type
    }
    return render(request, 'predictor/compare.html', context)
