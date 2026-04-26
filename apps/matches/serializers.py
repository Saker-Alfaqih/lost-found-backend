"""
Matches App Serializers
"""

from rest_framework import serializers
from .models import SmartMatch, MatchType


class MatchSimilaritySerializer(serializers.Serializer):
    """Serializer for match similarity scores"""
    text = serializers.DecimalField(max_digits=5, decimal_places=2)
    location = serializers.DecimalField(max_digits=5, decimal_places=2)
    category = serializers.DecimalField(max_digits=5, decimal_places=2)
    date = serializers.DecimalField(max_digits=5, decimal_places=2)
    overall = serializers.DecimalField(max_digits=5, decimal_places=2)


class SmartMatchSerializer(serializers.ModelSerializer):
    """Serializer for smart matches"""
    similarity = serializers.SerializerMethodField()
    similarity_score = serializers.SerializerMethodField()
    
    class Meta:
        model = SmartMatch
        fields = [
            'id', 'lost_item_id', 'found_item_id', 'similarity',
            'similarity_score', 'match_type', 'is_reviewed', 'is_dismissed',
            'created_at'
        ]
    
    def get_similarity(self, obj):
        return {
            'text': obj.similarity_text,
            'location': obj.similarity_location,
            'category': obj.similarity_category,
            'date': obj.similarity_date,
            'overall': obj.similarity_overall
        }
    
    def get_similarity_score(self, obj):
        return int(obj.similarity_overall)


class SmartMatchAdminSerializer(serializers.ModelSerializer):
    """Full match serializer for admin"""
    class Meta:
        model = SmartMatch
        fields = '__all__'


class SmartMatchUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating match status"""
    class Meta:
        model = SmartMatch
        fields = ['is_reviewed', 'is_dismissed']