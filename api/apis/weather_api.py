import requests
from datetime import datetime
from django.core.cache import cache
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

# Mapeo basado en el estándar WMO 4677 simplificado
WMO_CODES = {
    0: "Despejado",
    1: "Principalmente despejado",
    2: "Parcialmente nublado",
    3: "Nublado",
    45: "Niebla",
    48: "Niebla de rima depositada",
    51: "Llovizna ligera",
    53: "Llovizna moderada",
    55: "Llovizna densa",
    56: "Llovizna helada ligera",
    57: "Llovizna helada densa",
    61: "Lluvia ligera",
    63: "Lluvia moderada",
    65: "Lluvia fuerte",
    66: "Lluvia helada ligera",
    67: "Lluvia helada fuerte",
    71: "Nieve ligera",
    73: "Nieve moderada",
    75: "Nieve fuerte",
    77: "Granos de nieve",
    80: "Chubascos de lluvia ligeros",
    81: "Chubascos de lluvia moderados",
    82: "Chubascos de lluvia violentos",
    85: "Chubascos de nieve ligeros",
    86: "Chubascos de nieve fuertes",
    95: "Tormenta",
    96: "Tormenta con granizo ligero",
    99: "Tormenta con granizo fuerte",
}

DIAS_SEMANA = {
    0: "Lunes",
    1: "Martes",
    2: "Miércoles",
    3: "Jueves",
    4: "Viernes",
    5: "Sábado",
    6: "Domingo"
}

def get_weather_description(code):
    return WMO_CODES.get(code, "Desconocido")

def get_dia_nombre(fecha_str):
    try:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d')
        return DIAS_SEMANA.get(fecha.weekday(), "")
    except:
        return ""

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_weather_forecast(request):
    lat = request.query_params.get('lat')
    lon = request.query_params.get('lon')

    if not lat or not lon:
        return Response({"error": "Se requieren los parámetros lat y lon."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        lat = float(lat)
        lon = float(lon)
    except ValueError:
        return Response({"error": "lat y lon deben ser números válidos."}, status=status.HTTP_400_BAD_REQUEST)

    # Cache key rounded to 2 decimal places
    cache_key = f"weather_{round(lat, 2)}_{round(lon, 2)}"
    cached_data = cache.get(cache_key)

    if cached_data:
        return Response(cached_data)

    # API Call
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code&daily=weather_code,temperature_2m_max,temperature_2m_min&timezone=auto"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        return Response({"error": f"Error al conectar con Open-Meteo: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Current data
    current = data.get('current', {})
    weather_code = current.get('weather_code', 0)
    wind_speed = current.get('wind_speed_10m', 0)
    
    actual = {
        "temperatura": current.get('temperature_2m'),
        "humedad": current.get('relative_humidity_2m'),
        "viento": wind_speed,
        "descripcion": get_weather_description(weather_code),
        "alerta_pulverizacion": wind_speed > 15
    }

    # Forecast data (next 5 days)
    daily = data.get('daily', {})
    times = daily.get('time', [])
    max_temps = daily.get('temperature_2m_max', [])
    min_temps = daily.get('temperature_2m_min', [])
    weather_codes = daily.get('weather_code', [])

    pronostico = []
    for i in range(min(5, len(times))):
        fecha_str = times[i]
        pronostico.append({
            "dia": fecha_str,
            "dia_nombre": get_dia_nombre(fecha_str),
            "max": max_temps[i],
            "min": min_temps[i],
            "clima": get_weather_description(weather_codes[i])
        })

    result = {
        "actual": actual,
        "pronostico": pronostico
    }

    # Store in cache for 15 minutes (900 seconds)
    cache.set(cache_key, result, 900)

    return Response(result)
