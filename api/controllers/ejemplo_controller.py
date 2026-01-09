# urls_controller_system_roles = []

# ###############################################################
# ##CREATE

# class SystemRolesCreateAPIView(generics.CreateAPIView):
#     """
#     Vista para crear un nuevo rol del sistema.

#     @queryset SystemRoles.objects.all(): Conjunto de consultas de todos los roles.
#     @serializer_class SystemRolesSerializer: Serializador utilizado para crear roles.
#     @memberof SystemRolesCreateAPIView
#     """
#     queryset = SystemRoles.objects.all()
#     serializer_class = SystemRolesSerializer
# urls_controller_system_roles.append(path('system_roles/create', SystemRolesCreateAPIView.as_view(), name='crear-system_roles'))

# ###############################################################
# ##UPDATE

# class SystemRolesUpdateAPIView(generics.UpdateAPIView):
#     """
#     Vista para actualizar un rol del sistema existente.

#     @queryset SystemRoles.objects.all(): Conjunto de consultas de todos los roles.
#     @serializer_class SystemRolesSerializer: Serializador utilizado para actualizar roles.
#     @memberof SystemRolesUpdateAPIView
#     """
#     queryset = SystemRoles.objects.all()
#     serializer_class = SystemRolesSerializer
# urls_controller_system_roles.append(path('system_roles/<int:pk>/update', SystemRolesUpdateAPIView.as_view(), name='actualizar-system_roles'))
    
# ###############################################################
# ##DELETE

# class SystemRolesDestroyAPIView(generics.DestroyAPIView):
#     """
#     Vista para eliminar un rol del sistema existente.

#     @queryset SystemRoles.objects.all(): Conjunto de consultas de todos los roles.
#     @serializer_class SystemRolesSerializer: Serializador utilizado para eliminar roles.
#     @memberof SystemRolesDestroyAPIView
#     """
#     queryset = SystemRoles.objects.all()
#     serializer_class = SystemRolesSerializer
# urls_controller_system_roles.append(path('system_roles/<int:pk>/delete', SystemRolesDestroyAPIView.as_view(), name='eliminar-system_roles'))
