/* =========================================================
   INFORMES DE ACTIVIDAD - DATOS DE MUESTRA

   Maqueta compartida por la pantalla de Actividades y por
   el contador del Panel del Director, para que ambos digan
   siempre lo mismo.

   Cuando se conecte el backend, esto se sustituye por una
   llamada a /api/usuarios/informes-jefatura/ y este archivo
   desaparece.
========================================================= */

export const INFORMES_MUESTRA = [

  {
    id: 1,
    jefatura: 'MANTENIMIENTO',
    jefaturaNombre: 'Jefatura de Mantenimiento',
    codigo: 'INF-MNT-2026-0004',
    titulo: 'Informe de actividades - Mantenimiento correctivo',
    periodo: 'Agosto 2026',
    fecha: '02/09/26',
    jefe: 'Jefe Mantenimiento',
    origen: 'MTO-2026-0008',
    atendidos: '6 requerimientos',
    resumen:
      'Reemplazo de fuente de poder y revisión eléctrica del '
      + 'laboratorio de cómputo.',
    leido: false,
    contenido:
      'Durante el periodo se atendieron seis requerimientos de '
      + 'mantenimiento correctivo, cinco de ellos cerrados dentro '
      + 'del plazo comprometido.\n\n'
      + 'El requerimiento MTO-2026-0008 derivó en la compra '
      + 'CMP-2026-0007 (pilas de aire), actualmente en trámite.\n\n'
      + 'Se recomienda programar una revisión preventiva del '
      + 'tablero eléctrico del bloque de laboratorios.',
  },

  {
    id: 2,
    jefatura: 'MANTENIMIENTO',
    jefaturaNombre: 'Jefatura de Mantenimiento',
    codigo: 'INF-MNT-2026-0003',
    titulo: 'Informe de actividades - Infraestructura',
    periodo: 'Julio 2026',
    fecha: '05/08/26',
    jefe: 'Jefe Mantenimiento',
    origen: 'MTO-2026-0005',
    atendidos: '4 requerimientos',
    resumen:
      'Refacción de puertas y cambio de luminarias en aulas del '
      + 'segundo piso.',
    leido: true,
    contenido:
      'Se ejecutaron cuatro requerimientos de infraestructura, '
      + 'todos cerrados con acta de conformidad firmada por la '
      + 'unidad solicitante.\n\n'
      + 'No se registraron observaciones ni trabajos pendientes.',
  },

  {
    id: 3,
    jefatura: 'UTIC',
    jefaturaNombre: 'Jefatura de UTIC',
    codigo: 'INF-UTIC-2026-0007',
    titulo: 'Informe de actividades - Soporte Técnico',
    periodo: 'Agosto 2026',
    fecha: '01/09/26',
    jefe: 'Jefe UTIC',
    origen: 'SOP-2026-0012',
    atendidos: '11 tickets',
    resumen:
      'Atención de incidencias de red y reposición de equipos en '
      + 'el área administrativa.',
    leido: false,
    contenido:
      'Se atendieron once tickets de soporte técnico, de los '
      + 'cuales nueve se resolvieron sin necesidad de compra de '
      + 'componentes.\n\n'
      + 'Dos tickets derivaron en solicitudes de compra por '
      + 'reposición de componentes dañados.\n\n'
      + 'El tiempo medio de atención se mantuvo dentro del SLA '
      + 'comprometido para prioridad media.',
  },

  {
    id: 4,
    jefatura: 'UTIC',
    jefaturaNombre: 'Jefatura de UTIC',
    codigo: 'INF-UTIC-2026-0006',
    titulo: 'Informe de actividades - Mantenimiento preventivo',
    periodo: 'Julio 2026',
    fecha: '04/08/26',
    jefe: 'Jefe UTIC',
    origen: 'SOP-2026-0009',
    atendidos: '8 tickets',
    resumen:
      'Mantenimiento preventivo de equipos de cómputo del '
      + 'laboratorio de sistemas.',
    leido: true,
    contenido:
      'Se completó el mantenimiento preventivo programado sobre '
      + 'ocho equipos del laboratorio de sistemas.\n\n'
      + 'Se identificaron dos equipos con disco en estado crítico; '
      + 'se recomienda su reposición durante la próxima gestión.',
  },
]
