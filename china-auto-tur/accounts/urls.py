from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('cabinet/', views.cabinet_client_view, name='cabinet_client'),
    path('manager/', views.cabinet_manager_view, name='cabinet_manager'),
    path('admin-panel/', views.admin_panel_view, name='admin_panel'),
    path('admin-panel/users/<int:pk>/role/', views.user_role_update_view, name='user_role_update'),
]