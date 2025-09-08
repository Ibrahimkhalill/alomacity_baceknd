from django.shortcuts import render
from django.db.models import Q
from django.core.cache import cache

# Create your views here.
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import News, Reaction
from .serializers import NewsSerializer, ReactionSerializer
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from rest_framework.pagination import PageNumberPagination

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_news(request):
    serializer = NewsSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
CACHE_TIMEOUT = 60 * 60  # 10 minutes

@api_view(['GET'])
def list_news(request):
    cache_key = "last_4_days_news"

    # Check cache first
    news_data = cache.get(cache_key)
    if not news_data:
        news_queryset = News.objects.all().order_by('-published_datetime')
        serializer = NewsSerializer(news_queryset, many=True)
        news_data = serializer.data

        # Store in cache
        cache.set(cache_key, news_data, timeout=CACHE_TIMEOUT)
        print("Cache populated")
    else:
        print("Cache hit")

    # Pagination on cached data
    paginator = PageNumberPagination()
    paginator.page_size = 50
    result_page = paginator.paginate_queryset(news_data, request)

    return paginator.get_paginated_response(result_page)




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

@api_view(['POST', 'PUT'])
@permission_classes([IsAuthenticated])
def create_or_update_reaction(request, news_id):
    user = request.user
    news = get_object_or_404(News, id=news_id)
    
    # Check if reaction exists
    reaction, created = Reaction.objects.get_or_create(user=user, news=news)
    
    # Update reaction
    # Only update love if it's explicitly provided in the request
    if 'love' in request.data:
        reaction.love = request.data.get('love', False)
    
    # Update comment if provided
    if 'comment' in request.data:
        reaction.comment = request.data.get('comment', None)
    
    reaction.save()
    
    serializer = ReactionSerializer(reaction)
    return Response(serializer.data, status=status.HTTP_200_OK if not created else status.HTTP_201_CREATED)

@api_view(['GET'])
def get_reactions_for_news(request, news_id):
    news = get_object_or_404(News, id=news_id)
    reactions = Reaction.objects.filter(news=news)
    serializer = ReactionSerializer(reactions, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def news_search(request):
    search_query = request.query_params.get('q', None)
    queryset = News.objects.all()
    
    if search_query:
        queryset = queryset.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__icontains=search_query)
        )
    
    serializer = NewsSerializer(queryset, many=True)
    return Response(serializer.data)