from rest_framework import generics
from ..models import Personal
from ..serializers import PersonalSerializer

class PersonalCreateAPIView(generics.CreateAPIView):
    queryset = Personal.objects.all()
    serializer_class = PersonalSerializer

class PersonalUpdateAPIView(generics.UpdateAPIView):
    queryset = Personal.objects.all()
    serializer_class = PersonalSerializer

class PersonalDestroyAPIView(generics.DestroyAPIView):
    queryset = Personal.objects.all()
    serializer_class = PersonalSerializer
