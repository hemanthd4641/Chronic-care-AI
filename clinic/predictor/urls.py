from django.urls import path
from . import views

app_name = "predictor"

urlpatterns = [
    path("", views.index, name="index"),
    path("history/", views.prediction_history, name="history"),
    path("download/<str:format_type>/", views.download_report, name="download_report"),
    path("chart-data/", views.chart_data, name="chart_data"),
    path("compare/", views.compare_predictions, name="compare"),
    path("<str:key>/", views.predict_disease, name="predict"),
]
