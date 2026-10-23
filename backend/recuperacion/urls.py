from django.urls import path

from .views import (
    solicitar_codigo,
    verificar_codigo,
    restablecer_password,
)


urlpatterns = [

    path(
        "solicitar/",
        solicitar_codigo,
        name="solicitar-recuperacion"
    ),

    path(
        "verificar/",
        verificar_codigo,
        name="verificar-recuperacion"
    ),

    path(
        "restablecer/",
        restablecer_password,
        name="restablecer-password"
    ),

]