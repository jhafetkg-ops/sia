from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from usuarios.models import Area, Usuario, UsuarioRol

from soporte.models import CategoriaTicket, EstadoTicket, Ticket


class Command(BaseCommand):

    help = (
        "Caso de uso 'Generar ticket preventivo automático' "
        "(actor Sistema): crea un ticket de mantenimiento "
        "preventivo por cada área activa que todavía no tenga "
        "uno este mes. Pensado para ejecutarse por cron/tarea "
        "programada del sistema operativo (no hay Celery en "
        "el proyecto)."
    )

    @transaction.atomic
    def handle(self, *args, **options):

        try:
            categoria = CategoriaTicket.objects.get(codigo="PREVENTIVO", activo=True)
        except CategoriaTicket.DoesNotExist:
            self.stderr.write(
                self.style.ERROR(
                    "No existe la categoría PREVENTIVO. "
                    "Ejecute las migraciones de soporte antes de correr este comando."
                )
            )
            return

        try:
            estado_nuevo = EstadoTicket.objects.get(codigo="NUEVO", activo=True)
        except EstadoTicket.DoesNotExist:
            self.stderr.write(
                self.style.ERROR(
                    "No existe el estado NUEVO. "
                    "Ejecute las migraciones de soporte antes de correr este comando."
                )
            )
            return

        autor = (
            Usuario.objects.filter(is_superuser=True, is_active=True).first()
            or Usuario.objects.filter(
                roles_asignados__rol__codigo="ADMIN",
                roles_asignados__activo=True,
                is_active=True,
            ).first()
        )

        if not autor:
            self.stderr.write(
                self.style.ERROR(
                    "No hay ningún usuario ADMIN activo para "
                    "registrar como autor de los tickets preventivos."
                )
            )
            return

        ahora = timezone.now()
        creados = 0

        for area in Area.objects.filter(activo=True):

            ya_existe = Ticket.objects.filter(
                area=area,
                categoria=categoria,
                creado_en__year=ahora.year,
                creado_en__month=ahora.month,
            ).exists()

            if ya_existe:
                continue

            anio = ahora.year
            prefijo = f"SOP-{anio}-"
            ultimo = (
                Ticket.objects.filter(codigo__startswith=prefijo)
                .order_by("-codigo")
                .first()
            )
            numero = 1
            if ultimo:
                try:
                    numero = int(ultimo.codigo.split("-")[-1]) + 1
                except (ValueError, IndexError):
                    numero = Ticket.objects.filter(codigo__startswith=prefijo).count() + 1
            codigo = f"{prefijo}{numero:04d}"

            Ticket.objects.create(
                codigo=codigo,
                titulo=f"Mantenimiento preventivo automático - {area.nombre} ({ahora.month:02d}/{ahora.year})",
                descripcion=(
                    "Ticket generado automáticamente por el sistema para "
                    f"el mantenimiento preventivo mensual del área {area.nombre}."
                ),
                solicitante=autor,
                area=area,
                ubicacion=area.nombre,
                equipo_afectado="Equipamiento general del área",
                categoria=categoria,
                estado=estado_nuevo,
            )

            creados += 1
            self.stdout.write(self.style.SUCCESS(f"Ticket preventivo creado para {area.nombre}: {codigo}"))

        self.stdout.write(f"Tickets preventivos generados: {creados}")
