from django.contrib import admin
from .models import Restaurante, Cardapio, Avaliacao, DenunciaComentario, User

admin.site.register(Restaurante)
admin.site.register(Cardapio)
admin.site.register(Avaliacao)
admin.site.register(DenunciaComentario)
admin.site.register(User)
