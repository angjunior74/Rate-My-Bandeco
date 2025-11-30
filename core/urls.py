from django.urls import path
from . import views


urlpatterns = [
    # Autenticação
    path('', views.landing_view, name='landing'),
    path('cadastro/', views.cadastro_view, name='cadastro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('confirmar-email/<str:token>/', views.confirmar_email_view, name='confirmar_email'),
    
    # Usuário comum
    path('home/', views.home_usuario, name='home_usuario'),
    path('cardapio/<int:restaurante_id>/', views.cardapio_view, name='cardapio'),
    path('avaliar/<int:restaurante_id>/<int:cardapio_id>/', views.avaliar_bandejao_view, name='avaliar_bandejao'),
    path('denunciar/<int:avaliacao_id>/', views.denunciar_comentario_view, name='denunciar_comentario'),
    
    # Admin
    path('painel/', views.painel_admin_view, name='painel_admin'),
    path('painel/moderar/', views.moderar_comentarios_view, name='moderar_comentarios'),
    path('painel/restaurante/<int:restaurante_id>/', views.dashboard_restaurante_view, name='dashboard_restaurante'),
    path('painel/restaurante/<int:restaurante_id>/novo_cardapio/', views.novo_cardapio_view, name='novo_cardapio'),
    path('api/restaurantes/', views.api_restaurantes, name='api_restaurantes'),
    path('perfil/', views.perfil_usuario, name='perfil_usuario'),


]
