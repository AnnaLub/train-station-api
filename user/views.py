from rest_framework import generics, viewsets

from user.serializers import UserSerializer

class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer