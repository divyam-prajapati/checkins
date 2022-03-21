from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from .views import ChartData

urlpatterns = [
    #basic
    path("", views.homepage, name="homepage"),
    path("form/", views.form, name="form"),
    path("register/", views.register_request, name="register"),
    path("login/", views.login_request, name="login"),
    path("logout/", views.logout_request, name= "logout"),
    
    #password reset
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='checkins/password/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="checkins/password/password_reset_confirm.html"), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='checkins/password/password_reset_complete.html'), name='password_reset_complete'),      
    path("password_reset", views.password_reset_request, name="password_reset"),
    
    #nav
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/edit/<int:object_id>/", views.edit_event, name="edit-event"),
    path("dashboard/delete/<int:object_id>/", views.event_delete, name="delete-event"),

    #FR
    path('dashboard/facereco/live/video_feed', views.video_feed, name='video_feed'),
    path("dashboard/facereco/live", views.live, name="live"),
    path("dashboard/facereco", views.facereco, name="facereco"),
    
    #lists
    path("dashboard/lists", views.lists, name="lists"),
    path("dashboard/lists/<int:object_id>/", views.delete_invite, name="delete-invite"),

    #profile
    path("dashboard/profile", views.profile, name="profile"),
    path("dashboard/profile/event_report", views.exportEvent, name="profile-event-report"),
    path("dashboard/profile/invites_report", views.exportInvites, name="profile-invites-report"),
    path("dashboard/profile/checkins_report", views.exportCheckins, name="profile-checkins-report"),
    
    #stats
    path("dashboard/statistics", views.statistics, name="statistics"),

    #QR
    path("dashboard/qr", views.qr, name="qr"),
    path("dashboard/qr/scan", views.qrscan, name="qr-scan"),
    
    #Chart Data
    path('api/chart/data/', ChartData.as_view(), name="api-chart-data"),
]
