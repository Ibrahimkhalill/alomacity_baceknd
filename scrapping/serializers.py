from rest_framework import serializers
from .models import News, Reaction
from authentications.serializers import CustomUserSerializer


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = '__all__'

class ReactionSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)  # Nested serializer for user details
    news = serializers.PrimaryKeyRelatedField(queryset=News.objects.all())

    class Meta:
        model = Reaction
        fields = ['id', 'user', 'news', 'love', 'comment', 'created_at']

    def create(self, validated_data):
        # Ensure user is set from the request context
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)