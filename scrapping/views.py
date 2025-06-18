from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import News, Reaction
from .serializers import NewsSerializer, ReactionSerializer
from django.shortcuts import get_object_or_404

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_news(request):
    serializer = NewsSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def list_news(request):
    news = News.objects.all().order_by('-published_datetime')  # sort by most recent
    serializer = NewsSerializer(news, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)




@api_view(['GET'])
def get_news_detail(request, news_id):
    news = get_object_or_404(News, id=news_id)
    serializer = NewsSerializer(news)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_news(request, news_id):
    news = get_object_or_404(News, id=news_id)
    serializer = NewsSerializer(news, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_news(request, news_id):
    news = get_object_or_404(News, id=news_id)
    news.delete()
    return Response({"message": "News deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

@api_view(['POST','PUT'])
@permission_classes([IsAuthenticated])
def create_or_update_reaction(request, news_id):
    user = request.user
    news = get_object_or_404(News, id=news_id)
    
    # Check if reaction exists
    reaction, created = Reaction.objects.get_or_create(user=user, news=news)
    
    # Update reaction
    love = request.data.get('love', False)
    comment = request.data.get('comment', None)
    
    reaction.love = love
    if comment is not None:
        reaction.comment = comment
    reaction.save()
    
    serializer = ReactionSerializer(reaction)
    return Response(serializer.data, status=status.HTTP_200_OK if not created else status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_reactions_for_news(request, news_id):
    news = get_object_or_404(News, id=news_id)
    reactions = Reaction.objects.filter(news=news)
    serializer = ReactionSerializer(reactions, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)