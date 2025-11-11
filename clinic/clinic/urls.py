from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from admission import views as admission_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('admission.urls')),
    path('chatrooms/', include('chatroom.urls')),
    path('profile/', include('userprofile.urls')),
    path('chatbot/', include('chatbot.urls')),
    path("store/", include("medical_store.urls")),
    path('appointments/', include("appointments.urls")),
    path("predict/", include("predictor.urls", namespace="predictor")),
    path("messages/", include("messaging.urls", namespace="messaging")),
    path("health-tracker/", include("health_tracker.urls")),
    path("summary/", admission_views.project_summary, name="project_summary"),



]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
