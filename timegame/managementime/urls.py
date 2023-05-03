from django.urls import path, include
from django.contrib.auth import views as auth_views
from .views import *

urlpatterns = [
    path('', index.as_view(), name='inicio'),
    path('registrar/',TiempoJuegoCreateView.as_view(), name='registrar'),
    path('lista/', TiempoJuegoListView.as_view(), name='lista'),
    path('eliminar-tiempo/<int:pk>/', TiempoJuegoDeleteView, name='eliminar_tiempo'),
    path('actualizar/<int:pk>/', TiempoJuegoUpdateView.as_view(), name='actualizar'),
    path('agregar-consola/', ConsolaCreateView.as_view(), name='consola'),
    path('ver-consola/', VerConsolaListView.as_view(), name='ver_consolas'),
    path('eliminar-consola/<int:pk>/', ConsolaDeleteView, name='eliminar_consolas'),
    path('actualizar-consola/<int:pk>/', ConsolaUpdateView.as_view(), name='actualizar_consolas'),
    path('reporte/', RegistrosPorRangoFechasView.as_view(), name='reporte'),
    path('terminos/', TerminosView.as_view(), name='terminos'),
    path('ayuda/', AyudaView.as_view(), name='ayuda'),
    
    path('backup/', BackupView.as_view(), name='backup'),
    path('restore/', RestoreView.as_view(), name='restore'),
    
    #authenticate
    #Registro de usuario
    path('signup/', SignUpView.as_view(), name='signup'),
    
    #Login
    path('login/', CustomLoginView.as_view(form_class=LoginForm), name='login'),
    
    #cierre de sision
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    #cambio de contraseña
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='managementime/password_change.html', form_class = CustomPasswordChangeForm, success_url='/password_change/done/'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='managementime/password_change_done.html'), name='password_change_done'),
    
    # Restablecimiento de contraseña
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='managementime/password_reset.html', form_class=PasswordResetForm), name='password_reset'), 
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='managementime/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='managementime/password_reset_confirm.html', form_class=CustomSetPasswordForm), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='managementime/password_reset_complete.html'), name='password_reset_complete'),
]