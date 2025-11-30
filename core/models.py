from django.db import models
from django.contrib.auth.models import AbstractUser

# Usuário customizado
class User(AbstractUser):
    curso = models.CharField(max_length=100)
    is_admin = models.BooleanField(default=False)
    email_confirmado = models.BooleanField(default=False)
    token_confirmacao = models.CharField(max_length=100, blank=True, null=True)

class Restaurante(models.Model):
    nome = models.CharField(max_length=100)
    unidade = models.CharField(max_length=100)
    capacidade_refeicoes = models.IntegerField()
    descricao = models.TextField(blank=True)

    def __str__(self):
        return self.nome

class Cardapio(models.Model):
    restaurante = models.ForeignKey(Restaurante, on_delete=models.CASCADE)
    data = models.DateField()
    tipo_refeicao = models.CharField(max_length=50)
    guarnicao = models.CharField(max_length=100)
    prato_principal = models.CharField(max_length=100)
    prato_secundario = models.CharField(max_length=100)
    opcao_vegetariana = models.CharField(max_length=100, blank=True)
    saladas = models.CharField(max_length=200)
    sobremesa = models.CharField(max_length=100, blank=True)
    acompanhamentos = models.CharField(max_length=100, blank=True, default="")

class Avaliacao(models.Model):
    restaurante = models.ForeignKey(Restaurante, on_delete=models.CASCADE)
    cardapio = models.ForeignKey(Cardapio, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    estrelas = models.PositiveIntegerField()  # Total: de 1 a 5
    comentario = models.TextField(blank=True)
    curso = models.CharField(max_length=100)
    data = models.DateTimeField(auto_now_add=True)

class DenunciaComentario(models.Model):
    MOTIVOS = [
        ('INDEVIDO', 'Conteúdo indevido'),
        ('OFENSIVO', 'Conteúdo ofensivo'),
        ('SPAM', 'Spam'),
        ('ASSEDIO', 'Assédio'),
        ('OUTROS', 'Outros'),
    ]
    avaliacao = models.ForeignKey(Avaliacao, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    motivo = models.CharField(max_length=20, choices=MOTIVOS)
    status = models.CharField(max_length=20, default='Em análise')
    data = models.DateTimeField(auto_now_add=True)
