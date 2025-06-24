from django.urls import path
from .views import advertisement_rejected, advertisement_create, advertisement_update, advertisement_get, advertisement_list, advertisement_delete, advertisement_approve, advertisement_get_by_user

urlpatterns = [
    path('advertisements/create/', advertisement_create, name='advertisement_create'),
    path('advertisements/<int:pk>/update/', advertisement_update, name='advertisement_update'),
    path('advertisements/<int:pk>/', advertisement_get, name='advertisement_get'),
    path('advertisements/get_all/', advertisement_list, name='advertisement_list'),
    path('advertisements/<int:pk>/delete/', advertisement_delete, name='advertisement_delete'),
    path('advertisements/<int:pk>/approve/', advertisement_approve, name='advertisement_approve'),
    path('advertisements/<int:pk>/rejected/', advertisement_rejected, name='advertisement_rejected'),
    path('advertisements/user/get_all/', advertisement_get_by_user, name='advertisement_get_by_user'),
]