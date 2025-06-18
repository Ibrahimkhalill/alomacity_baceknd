from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Advertisement, AdvertisementImage
from .serializers import AdvertisementSerializer
from django.shortcuts import get_object_or_404

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def advertisement_create(request):
    if request.method == 'POST':
        serializer = AdvertisementSerializer(data=request.data, context={'request': request})  # Pass request context
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def advertisement_update(request, pk):
    if request.method == 'PUT':
        advertisement = get_object_or_404(Advertisement, pk=pk)
        # Check if the user is the owner or admin
        if advertisement.user != request.user and not request.user.is_staff:
            return Response({"detail": "You do not have permission to update this advertisement."}, status=status.HTTP403_FORBIDDEN)
        serializer = AdvertisementSerializer(advertisement, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Optional: Can be removed if public access is desired
def advertisement_get(request, pk):
    if request.method == 'GET':
        advertisement = get_object_or_404(Advertisement, pk=pk)
        serializer = AdvertisementSerializer(advertisement)
        return Response(serializer.data)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Optional: Can be removed if public access is desired
def advertisement_get_by_user(request):
    if request.method == 'GET':
        user = request.user
        advertisement = Advertisement.objects.filter(user=user)
        serializer = AdvertisementSerializer(advertisement, many=True)
        return Response(serializer.data)

@api_view(['GET'])
def advertisement_list(request):  # Public access for listing
    if request.method == 'GET':
        advertisements = Advertisement.objects.all()
        serializer = AdvertisementSerializer(advertisements, many=True)
        return Response(serializer.data)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def advertisement_delete(request, pk):
    if request.method == 'DELETE':
        advertisement = get_object_or_404(Advertisement, pk=pk)
        # Check if the user is the owner or admin
        if advertisement.user != request.user and not request.user.is_staff:
            return Response({"detail": "You do not have permission to delete this advertisement."}, status=status.HTTP403_FORBIDDEN)
        advertisement.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def advertisement_approve(request, pk):
    if request.method == 'POST':
        advertisement = get_object_or_404(Advertisement, pk=pk)
        advertisement.status = 'approved'
        advertisement.save()
        serializer = AdvertisementSerializer(advertisement)
        return Response(serializer.data)