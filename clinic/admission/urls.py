from django.urls import path
from . import views
app_name = 'admission'
urlpatterns = [
    path('register/',views.registration,name = 'registration'),
    path('',views.LoginView,name = 'login'),
    path('index/',views.index,name='index'),
    path('logout/',views.LogoutView,name='logout'),
    path('viewStudents/',views.veiewStudents,name = 'viewstudents'),
    path('deletestudent/<int:pk>/',views.deletestudent,name = 'deletestudent'),
    path('updatedetails/<int:pk>/',views.updatedetails,name = 'updatedetails'),
    path('announcement/',views.announcement_view,name='announcement'),
    path('deleteannouncement/<int:pk>/',views.deleteAnnouncements,name='deleteannouncement'),
    path('manage-assignments/',views.manage_patient_assignments,name='manage_assignments'),
    path('sync-students/',views.sync_missing_students,name='sync_students'),
]
