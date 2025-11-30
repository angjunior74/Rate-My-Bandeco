from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import CadastroForm, LoginForm
from .models import Restaurante, Cardapio, Avaliacao, DenunciaComentario, User
from django.db.models import Avg, Count
from datetime import date, timedelta
import uuid
from django.core.mail import send_mail
from django.conf import settings

def landing_view(request):
    if request.user.is_authenticated:
        if request.user.is_admin:
            return redirect('painel_admin')
        else:
            return redirect('home_usuario')
    return render(request, 'core/landing.html')

def cadastro_view(request):
    if request.method == 'POST':
        form = CadastroForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Desativa até confirmar email
            user.token_confirmacao = str(uuid.uuid4())
            user.save()
            
            # Enviar email de confirmação
            link_confirmacao = f"http://{request.get_host()}/confirmar-email/{user.token_confirmacao}/"
            assunto = "Confirme seu email - Rate My Bandeco"
            mensagem = f"""
            Olá {user.username},

            Obrigado por se cadastrar no Rate My Bandeco!

            Para confirmar seu email, clique no link abaixo:
            {link_confirmacao}

            Se não foi você quem fez este cadastro, ignore este email.

            Atenciosamente,
            Equipe Rate My Bandeco
            """
            
            send_mail(
                assunto,
                mensagem,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            
            return render(request, 'core/cadastro_confirmacao.html', {
                'email': user.email,
                'mensagem': 'Um email de confirmação foi enviado para seu email. Verifique sua caixa de entrada!'
            })
    else:
        form = CadastroForm()
    return render(request, 'core/cadastro.html', {'form': form})


def confirmar_email_view(request, token):
    try:
        user = User.objects.get(token_confirmacao=token)
        user.email_confirmado = True
        user.is_active = True
        user.token_confirmacao = ""
        user.save()
        return render(request, 'core/email_confirmado.html', {'sucesso': True})
    except User.DoesNotExist:
        return render(request, 'core/email_confirmado.html', {'sucesso': False})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Admins/staff não precisam confirmar email
            if not user.is_staff and not user.email_confirmado:
                return render(request, 'core/login.html', {
                    'form': LoginForm(),
                    'erro': 'Por favor, confirme seu email antes de fazer login.'
                })
            
            login(request, user)
            if user.is_admin:
                return redirect('painel_admin')
            else:
                return redirect('home_usuario')
        else:
            # Tenta encontrar o usuário para verificar se é email não confirmado
            try:
                user_nao_confirmado = User.objects.get(username=username)
                if not user_nao_confirmado.email_confirmado and user_nao_confirmado.check_password(password):
                    return render(request, 'core/login.html', {
                        'form': LoginForm(),
                        'erro': 'Por favor, confirme seu email antes de fazer login.'
                    })
            except User.DoesNotExist:
                pass
            
            # Credenciais inválidas
            return render(request, 'core/login.html', {
                'form': LoginForm(),
                'erro': 'Usuário ou senha inválidos.'
            })
    else:
        form = LoginForm()
    
    return render(request, 'core/login.html', {'form': form})



def logout_view(request):
    logout(request)
    return redirect('login')

def home_usuario(request):
    if not request.user.is_authenticated or request.user.is_admin:
        return redirect('login')
    
    return render(request, 'core/home_usuario.html')

def cardapio_view(request, restaurante_id):
    restaurante = Restaurante.objects.get(id=restaurante_id)
    cardapio = Cardapio.objects.filter(restaurante=restaurante).order_by('-data').first()
    avaliacoes = Avaliacao.objects.filter(restaurante=restaurante, cardapio=cardapio)
    
    # Calcula a média de avaliações deste cardápio
    media = avaliacoes.aggregate(Avg('estrelas'))['estrelas__avg']
    media_estrelas = round(media, 1) if media else 0
    
    return render(request, 'core/cardapio.html', {
        'restaurante': restaurante,
        'cardapio': cardapio,
        'avaliacoes': avaliacoes,
        'media_estrelas': media_estrelas,
    })

def avaliar_bandejao_view(request, restaurante_id, cardapio_id):
    restaurante = get_object_or_404(Restaurante, id=restaurante_id)
    cardapio = get_object_or_404(Cardapio, id=cardapio_id)
    if request.method == 'POST':
        estrelas = int(request.POST.get('estrelas'))
        comentario = request.POST.get('comentario')
        curso = request.user.curso
        Avaliacao.objects.create(
            restaurante=restaurante,
            cardapio=cardapio,
            usuario=request.user,
            estrelas=estrelas,
            comentario=comentario,
            curso=curso
        )
        return redirect('cardapio', restaurante_id=restaurante.id)
    return render(request, 'core/avaliar_bandejao.html', {
        'restaurante': restaurante,
        'cardapio': cardapio,
    })

def denunciar_comentario_view(request, avaliacao_id):
    avaliacao = get_object_or_404(Avaliacao, id=avaliacao_id)
    motivos = [
        ('INDEVIDO', 'Conteúdo indevido'),
        ('OFENSIVO', 'Conteúdo ofensivo'),
        ('SPAM', 'Spam'),
        ('ASSEDIO', 'Assédio'),
        ('OUTROS', 'Outros'),
    ]
    if request.method == 'POST':
        motivo = request.POST.get('motivo')
        DenunciaComentario.objects.create(
            avaliacao=avaliacao,
            usuario=request.user,
            motivo=motivo,
        )
        return redirect('cardapio', restaurante_id=avaliacao.restaurante.id)
    return render(request, 'core/denunciar_comentario.html', {
        'avaliacao': avaliacao,
        'motivos': motivos,
    })

def painel_admin_view(request):
    if not request.user.is_authenticated or not request.user.is_admin:
        return redirect('login')
    restaurantes = Restaurante.objects.all()
    return render(request, 'core/painel_admin.html', {'restaurantes': restaurantes})

def moderar_comentarios_view(request):
    if not request.user.is_authenticated or not request.user.is_admin:
        return redirect('login')

    if request.method == 'POST':
        denuncia_id = int(request.POST.get('denuncia_id'))
        acao = request.POST.get('acao')
        denuncia = DenunciaComentario.objects.get(id=denuncia_id)
        if acao == 'excluir':
            denuncia.avaliacao.delete()
            denuncia.delete()
            return redirect('moderar_comentarios')
        else:
            denuncia.status = 'Improcedente'
            denuncia.save()
            return redirect('moderar_comentarios')

    denuncias = DenunciaComentario.objects.filter(status='Em análise')
    return render(request, 'core/moderar_comentarios.html', {'denuncias': denuncias})


def dashboard_restaurante_view(request, restaurante_id):
    if not request.user.is_authenticated or not request.user.is_admin:
        return redirect('login')
    restaurante = Restaurante.objects.get(id=restaurante_id)
    cardapio = Cardapio.objects.filter(restaurante=restaurante).order_by('-data').first()

    hoje = date.today()
    semana_inicio = hoje - timedelta(days=hoje.weekday())
    semana_fim = semana_inicio + timedelta(days=6)

    avaliacao_hoje = Avaliacao.objects.filter(restaurante=restaurante, cardapio=cardapio, data__date=hoje)
    avaliacao_semana = Avaliacao.objects.filter(
        restaurante=restaurante, 
        cardapio=cardapio, 
        data__date__range=[semana_inicio, semana_fim]
    )

    media_hoje = round(avaliacao_hoje.aggregate(Avg('estrelas'))['estrelas__avg'] or 0, 1)
    media_semana = round(avaliacao_semana.aggregate(Avg('estrelas'))['estrelas__avg'] or 0, 1)
    total_hoje = avaliacao_hoje.count()
    total_semana = avaliacao_semana.count()

    return render(request, 'core/dashboard_restaurante.html', {
        'restaurante': restaurante,
        'cardapio': cardapio,
        'media_hoje': media_hoje,
        'media_semana': media_semana,
        'total_hoje': total_hoje,
        'total_semana': total_semana,
    })

def novo_cardapio_view(request, restaurante_id):
    if not request.user.is_authenticated or not request.user.is_admin:
        return redirect('login')
    restaurante = Restaurante.objects.get(id=restaurante_id)
    if request.method == 'POST':
        Cardapio.objects.create(
            restaurante=restaurante,
            data=request.POST.get('data'),
            tipo_refeicao=request.POST.get('tipo_refeicao'),
            prato_principal=request.POST.get('prato_principal'),
            opcao_vegetariana=request.POST.get('opcao_vegetariana'),
            guarnicao=request.POST.get('guarnicao'),
            saladas=request.POST.get('saladas'),
            sobremesa=request.POST.get('sobremesa')
        )
        return redirect('dashboard_restaurante', restaurante_id=restaurante.id)
    return render(request, 'core/novo_cardapio.html', {'restaurante': restaurante})

@login_required
def moderar_denuncias_view(request):
    if not request.user.is_admin:
        return redirect('login')
    denuncias = DenunciaComentario.objects.filter(status='Em análise')
    if request.method == "POST":
        denuncia_id = int(request.POST.get('denuncia_id'))
        acao = request.POST.get('acao')
        denuncia = DenunciaComentario.objects.get(id=denuncia_id)
        if acao == "excluir":
            denuncia.status = "Procedente"
            denuncia.avaliacao.delete()  # Apaga o comentário denunciado
        else:
            denuncia.status = "Improcedente"
        denuncia.save()
    return render(request, 'core/moderar_comentarios.html', {'denuncias': denuncias})


from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import RestauranteSerializer

@api_view(['GET'])
def api_restaurantes(request):
    """API que retorna lista de restaurantes com suas médias de avaliações"""
    restaurantes = Restaurante.objects.all()
    serializer = RestauranteSerializer(restaurantes, many=True)
    return Response(serializer.data)



@login_required(login_url='login')
def perfil_usuario(request):
    """Exibe e edita o perfil do usuário"""
    if request.user.is_admin:
        return redirect('painel_admin')
    
    if request.method == 'POST':
        # Atualizar dados do perfil
        novo_curso = request.POST.get('curso')
        
        if novo_curso:
            request.user.curso = novo_curso
            request.user.save()
            
            # Mensagem de sucesso (usando messages do Django)
            from django.contrib import messages
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('perfil_usuario')
    
    return render(request, 'core/perfil_usuario.html', {
        'usuario': request.user
    })
