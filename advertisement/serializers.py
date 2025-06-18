from rest_framework import serializers
from .models import Advertisement, AdvertisementImage

class AdvertisementImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdvertisementImage
        fields = ['id', 'image']

class AdvertisementSerializer(serializers.ModelSerializer):
    images = AdvertisementImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(max_length=1000000, allow_empty_file=False),
        write_only=True
    )
    user = serializers.ReadOnlyField(source='user.email')  # Read-only user field

    class Meta:
        model = Advertisement
        fields = ['id', 'user', 'serial_number', 'title', 'description', 'category', 'views', 'url', 'images', 'uploaded_images', 'status', 'created_at']

    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images')
        # Ensure user is available from context
        user = self.context['request'].user
        if not user.is_authenticated:
            raise serializers.ValidationError("Authentication required to create an advertisement.")
        advertisement = Advertisement.objects.create(user=user, **validated_data)
        for image in uploaded_images:
            AdvertisementImage.objects.create(advertisement=advertisement, image=image)
        return advertisement

    def update(self, instance, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.category = validated_data.get('category', instance.category)
        instance.url = validated_data.get('url', instance.url)
        instance.save()
        if uploaded_images:
            AdvertisementImage.objects.filter(advertisement=instance).delete()
            for image in uploaded_images:
                AdvertisementImage.objects.create(advertisement=instance, image=image)
        return instance