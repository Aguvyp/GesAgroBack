from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from ..serializers import RegisterSerializer, LoginSerializer, UsuarioSerializer, UpdatePasswordSerializer
from ..models import Usuario, Personal
from ..services.auth_token_service import create_auth_token, invalidate_token

class RegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "id": user.id,
                "nombre": user.nombre,
                "email": user.email,
                "role": user.rol,
                "message": "Usuario registrado exitosamente"
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            try:
                # 1. Buscar el usuario por email en la tabla Usuarios
                user = Usuario.objects.get(email=email)
                
                # 2. Hashear la password recibida con el mismo proceso que cuando se registra
                #    y comparar con la password obtenida del registro en la base de datos
                #    check_password() usa el mismo algoritmo (PBKDF2) que set_password()
                #    usado durante el registro, hashea la contraseña en texto plano y
                #    la compara con el hash almacenado en la BD
                if user.check_password(password) and user.is_active:
                    # 3. Si coinciden las password, crear token personalizado
                    auth_token = create_auth_token(user.id)
                    
                    # Buscar Personal por nombre ya que no hay relación directa en la BD
                    try:
                        personal = Personal.objects.get(nombre=user.nombre)
                        personal_id = personal.id
                    except Personal.DoesNotExist:
                        personal_id = None
                    
                    return Response({
                        "access_token": auth_token.access_token,
                        "token_type": "bearer",
                        "role": user.rol,
                        "user_id": user.id,
                        "personal_id": personal_id,
                        "usuario_id": user.id
                    })
                else:
                    return Response({"detail": "Credenciales inválidas"}, status=status.HTTP_401_UNAUTHORIZED)
            except Usuario.DoesNotExist:
                return Response({"detail": "Credenciales inválidas"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdatePasswordView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = UpdatePasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            try:
                # Buscar el usuario por email en la tabla Usuarios
                user = Usuario.objects.get(email=email)
                
                # Hashear la nueva contraseña con el mismo proceso que cuando se registra
                # set_password() usa el mismo algoritmo (PBKDF2) que se usa durante el registro
                user.set_password(password)
                user.save()
                
                return Response({
                    "message": "Contraseña actualizada exitosamente",
                    "email": user.email
                }, status=status.HTTP_200_OK)
            except Usuario.DoesNotExist:
                return Response({"detail": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TestView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        return Response({"status": "ok", "message": "Conexión exitosa"})

class HealthCheckView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        from django.utils import timezone
        return Response({
            "status": "healthy",
            "timestamp": timezone.now().isoformat()
        })

class LogoutView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        access_token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not access_token:
            access_token = request.data.get('access_token')
        
        if invalidate_token(access_token):
            return Response({"message": "Sesión cerrada exitosamente"})
        return Response({"detail": "Token inválido"}, status=status.HTTP_400_BAD_REQUEST)
