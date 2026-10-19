from django.contrib import admin

from .models import CategoriaTicket, EstadoTicket, Ticket


@admin.register(CategoriaTicket)
class CategoriaTicketAdmin(admin.ModelAdmin):
    list_display = (
        "codigo",
        "nombre",
        "activo",
    )

    search_fields = (
        "codigo",
        "nombre",
    )


@admin.register(EstadoTicket)
class EstadoTicketAdmin(admin.ModelAdmin):
    list_display = (
        "codigo",
        "nombre",
        "es_inicial",
        "es_terminal",
        "activo",
    )

    search_fields = (
        "codigo",
        "nombre",
    )


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        "codigo",
        "titulo",
        "solicitante",
        "tecnico_asignado",
        "estado",
        "prioridad",
        "creado_en",
    )

    list_filter = (
        "estado",
        "prioridad",
        "categoria",
        "area",
    )

    search_fields = (
        "codigo",
        "titulo",
        "descripcion",
    )