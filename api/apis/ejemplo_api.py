# urls_api_system_roles = []
# """
# Lista que contiene las rutas de la API relacionadas con el modelo `SystemRoles`.
# """

# @swagger_auto_schema(method='get', operation_description="Obtiene una lista de SystemRoles. Si se proporciona el parámetro pk, obtiene el SystemRoles específico.", responses={200: "OK", 400: "BAD REQUEST", 404: "NOT FOUND"})
# @api_view(['GET'])
# def get_system_roles(request, pk=None):
#     """
#     Obtiene una lista de objetos `SystemRoles` o un objeto específico si se proporciona un `pk`.

#     Args:
#         request: La solicitud HTTP.
#         pk (int, optional): El identificador primario del `SystemRoles` a obtener. Si no se proporciona, se obtienen todos los objetos.

#     Returns:
#         Response: Una respuesta con los datos serializados del objeto `SystemRoles` o una lista de objetos.
#     """
#     if pk is not None:
#         system_roles = get_object_or_404(SystemRoles, pk=pk)
#         serializer = SystemRolesSerializer(system_roles)
#         return Response(serializer.data)
#     else:
#         system_roles = SystemRoles.objects.all()
#         serializer = SystemRolesSerializer(system_roles, many=True)
#         return Response(serializer.data)
# urls_api_system_roles.append(path('system_roles/', get_system_roles, name='obtener-system_roles'))
# urls_api_system_roles.append(path('system_roles/<int:pk>', get_system_roles, name='obtener-system_roles-por-id'))
