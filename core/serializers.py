from rest_framework import serializers
from .models import Restaurante, Avaliacao
from django.db.models import Avg

class RestauranteSerializer(serializers.ModelSerializer):
    media_estrelas = serializers.SerializerMethodField()
    
    class Meta:
        model = Restaurante
        fields = ['id', 'nome', 'unidade', 'capacidade_refeicoes', 'media_estrelas']
    
    def get_media_estrelas(self, obj):
        """Calcula a média de estrelas do restaurante"""
        media = Avaliacao.objects.filter(restaurante=obj).aggregate(
            Avg('estrelas')
        )['estrelas__avg']
        return round(media, 1) if media else 0
