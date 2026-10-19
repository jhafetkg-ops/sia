import {
  createRouter,
  createWebHistory
} from 'vue-router'


/* =========================================================
   AUTENTICACIÓN
========================================================= */

import LoginView
  from '../views/LoginView.vue'

import CambiarPasswordView
  from '../views/CambiarPasswordView.vue'

import RecuperarPasswordView
  from '../views/RecuperarPasswordView.vue'


/* =========================================================
   ADMINISTRADOR - YA EXISTENTES
========================================================= */

import AdminDashboardView
  from '../views/AdminDashboardView.vue'

import AdminUsuariosView
  from '../views/AdminUsuariosView.vue'

import AdminRolesAreasView
  from '../views/AdminRolesAreasView.vue'

import AdminTicketsView
  from '../views/AdminTicketsView.vue'

import AdminBitacoraView
  from '../views/AdminBitacoraView.vue'

import AdminSMTPView
  from '../views/AdminSMTPView.vue'

import AdminPreferenciasView
  from '../views/AdminPreferenciasView.vue'

import AdminActividadesView
  from '../views/AdminActividadesView.vue'


/* =========================================================
   SUPERUSUARIO
========================================================= */

import SuperuserDashboardView
  from '../views/SuperuserDashboardView.vue'


/* =========================================================
   ADMINISTRADOR - NUEVOS MÓDULOS
========================================================= */

import AdminSoporteView
  from '../views/AdminSoporteView.vue'

import AdminComprasView
  from '../views/AdminComprasView.vue'

import AdminMantenimientoView
  from '../views/AdminMantenimientoView.vue'

import AdminPortalSolicitanteView
  from '../views/AdminPortalSolicitanteView.vue'


/* =========================================================
   SOLICITANTE
========================================================= */

import SolicitanteDashboardView
  from '../views/UsuarioDashboardKanbanView.vue'

import SolicitanteSoporteView
  from '../views/SolicitanteSoporteView.vue'

import MisSolicitudesView
  from '../views/MisSolicitudesView.vue'

import SolicitanteComprasView
  from '../views/SolicitanteComprasView.vue'

import SolicitanteMantenimientoView
  from '../views/SolicitanteMantenimientoView.vue'

import NotificacionesView
  from '../views/NotificacionesView.vue'

import PerfilView
  from '../views/PerfilView.vue'

import JefeUticDashboardView
  from '../views/JefeUticDashboardView.vue'

import EspecialistaDashboardView
  from '../views/EspecialistaDashboardView.vue'

import ServiciosGeneralesDashboardView
  from '../views/ServiciosGeneralesDashboardView.vue'

import AuxiliarServiciosGeneralesDashboardView
  from '../views/AuxiliarServiciosGeneralesDashboardView.vue'

import TesoreriaDashboardView
  from '../views/TesoreriaDashboardView.vue'

import AlmacenDashboardView
  from '../views/AlmacenDashboardView.vue'

import DafDashboardView
  from '../views/DafDashboardView.vue'


/* =========================================================
   ROUTER
========================================================= */

const router = createRouter({

  history:
    createWebHistory(
      import.meta.env.BASE_URL
    ),

  routes: [

    /* =====================================================
       GENERAL
    ===================================================== */

    {
      path: '/',
      redirect: '/login',
    },

    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: {
        publica: true,
      },
    },

    {
      path: '/cambiar-contrasena',
      name: 'cambiar-contrasena',
      component: CambiarPasswordView,
      meta: {
        requiereAuth: true,
      },
    },

    {
      path: '/recuperar-contrasena',
      name: 'recuperar-contrasena',
      component: RecuperarPasswordView,
      meta: {
        publica: true,
      },
    },


    /* =====================================================
       ADMINISTRADOR
    ===================================================== */

    {
      path: '/admin/mis-solicitudes', component: MisSolicitudesView,
      meta: { requiereAuth: true, admin: true, portalDirector: true },
    },
    {
      path: '/admin/nueva-solicitud/soporte', component: SolicitanteSoporteView,
      meta: { requiereAuth: true, admin: true, portalDirector: true },
    },
    {
      path: '/admin/nueva-solicitud/mantenimiento', component: SolicitanteMantenimientoView,
      meta: { requiereAuth: true, admin: true, portalDirector: true },
    },

    {
      path: '/admin/dashboard',
      name: 'admin-dashboard',
      component: AdminDashboardView,
      meta: {
        requiereAuth: true,
        admin: true,
      },
    },


    /* -----------------------------------------------------
       NUEVO KANBAN DE SOPORTE
    ----------------------------------------------------- */

    {
      path: '/admin/soporte',
      name: 'admin-soporte',
      component: AdminSoporteView,
      meta: {
        requiereAuth: true,
        admin: true,
      },
    },


    /* -----------------------------------------------------
       MANTENIMIENTO
    ----------------------------------------------------- */

    {
      path: '/admin/mantenimiento',
      name: 'admin-mantenimiento',
      component: AdminMantenimientoView,
      meta: {
        requiereAuth: true,
        admin: true,
      },
    },


    /* -----------------------------------------------------
       COMPRAS
    ----------------------------------------------------- */

    {
      path: '/admin/compras',
      name: 'admin-compras',
      component: AdminComprasView,
      meta: {
        requiereAuth: true,
        admin: true,
        vista: 'PENDIENTES',
      },
    },

    /* Mismo componente que /admin/compras, en modo archivo:
       solo solicitudes ya aprobadas o rechazadas. */
    {
      path: '/admin/historial',
      name: 'admin-historial',
      component: AdminComprasView,
      meta: {
        requiereAuth: true,
        admin: true,
        vista: 'HISTORIAL',
      },
    },


    /* -----------------------------------------------------
       ACTIVIDADES (solo Director)

       Maqueta visual de los informes que remiten las
       jefaturas de UTIC y Mantenimiento. No consume API.
    ----------------------------------------------------- */

    {
      path: '/admin/actividades',
      name: 'admin-actividades',
      component: AdminActividadesView,
      meta: {
        requiereAuth: true,
        admin: true,
      },
    },


    /* -----------------------------------------------------
       PORTAL SOLICITANTE - VISTA ADMIN
    ----------------------------------------------------- */

    {
      path: '/admin/portal-solicitante',
      name: 'admin-portal-solicitante',
      component: AdminPortalSolicitanteView,
      meta: {
        requiereAuth: true,
        admin: true,
      },
    },


    /* -----------------------------------------------------
       MANTENEMOS TU PANTALLA ANTERIOR DE TICKETS
    ----------------------------------------------------- */

    {
      path: '/admin/tickets',
      name: 'admin-tickets',
      component: AdminTicketsView,
      meta: {
        requiereAuth: true,
        admin: true,
      },
    },


    /* -----------------------------------------------------
       BITÁCORA (solo el Superusuario; el Director ya no
       tiene acceso a esta sección)
    ----------------------------------------------------- */

    {
      path: '/superuser/auditoria',
      name: 'superuser-auditoria',
      component: AdminBitacoraView,
      meta: {
        requiereAuth: true,
        roles: ['SUPERUSER'],
      },
    },


    /* =====================================================
       SUPERUSUARIO

       Vista separada del panel del Director (/admin/...):
       administración técnica del sistema (usuarios, roles y
       permisos, correo SMTP, preferencias). Reutiliza el
       mismo rol ADMIN para la autorización.
    ===================================================== */

    {
      path: '/superuser/dashboard',
      name: 'superuser-dashboard',
      component: SuperuserDashboardView,
      meta: {
        requiereAuth: true,
        roles: ['ADMIN', 'SUPERUSER'],
      },
    },

    {
      path: '/superuser/usuarios',
      name: 'superuser-usuarios',
      component: AdminUsuariosView,
      meta: {
        requiereAuth: true,
        roles: ['ADMIN', 'SUPERUSER'],
      },
    },

    {
      path: '/superuser/roles-permisos',
      name: 'superuser-roles-permisos',
      component: AdminRolesAreasView,
      meta: {
        requiereAuth: true,
        roles: ['ADMIN', 'SUPERUSER'],
      },
    },

    {
      path: '/superuser/smtp',
      name: 'superuser-smtp',
      component: AdminSMTPView,
      meta: {
        requiereAuth: true,
        roles: ['ADMIN', 'SUPERUSER'],
      },
    },

    {
      path: '/superuser/preferencias',
      name: 'superuser-preferencias',
      component: AdminPreferenciasView,
      meta: {
        requiereAuth: true,
        roles: ['ADMIN', 'SUPERUSER'],
      },
    },


    /* =====================================================
       SOLICITANTE
    ===================================================== */

    {
      path: '/usuario/dashboard',
      name: 'usuario-dashboard',
      component: SolicitanteDashboardView,
      meta: {
        requiereAuth: true,
      },
    },

    {
      path: '/usuario/soporte',
      name: 'usuario-soporte',
      component: SolicitanteSoporteView,
      meta: {
        requiereAuth: true,
      },
    },

    {
      path: '/usuario/mantenimiento',
      name: 'usuario-mantenimiento',
      component: SolicitanteMantenimientoView,
      meta: {
        requiereAuth: true,
      },
    },

    {
      path: '/usuario/mis-solicitudes',
      name: 'usuario-mis-solicitudes',
      component: MisSolicitudesView,
      meta: {
        requiereAuth: true,
      },
    },

    {
      path: '/usuario/compras',
      name: 'usuario-compras',
      component: SolicitanteComprasView,
      meta: {
        requiereAuth: true,
      },
    },

    {
      path: '/usuario/notificaciones',
      name: 'usuario-notificaciones',
      component: NotificacionesView,
      meta: {
        requiereAuth: true,
        roles: ['SOLICITANTE'],
      },
    },

    {
      path: '/especialista/notificaciones',
      name: 'especialista-notificaciones',
      redirect: { path: '/especialista/dashboard', query: { vista: 'notificaciones' } },
      meta: {
        requiereAuth: true,
        roles: ['ESPECIALISTA', 'AGENTE'],
      },
    },

    {
      path: '/usuario/perfil',
      name: 'usuario-perfil',
      component: PerfilView,
      meta: {
        requiereAuth: true,
      },
    },

    {
      path: '/usuario/configuracion',
      name: 'usuario-configuracion',
      component: CambiarPasswordView,
      meta: {
        requiereAuth: true,
      },
    },

    {
      path: '/jefe-utic/dashboard',
      name: 'jefe-utic-dashboard',
      component: JefeUticDashboardView,
      meta: { requiereAuth: true, roles: ['JEFE_UTIC'] },
    },

    {
      path: '/especialista/dashboard',
      name: 'especialista-dashboard',
      component: EspecialistaDashboardView,
      meta: { requiereAuth: true, roles: ['ESPECIALISTA'] },
    },

    {
      path: '/servicios-generales/dashboard',
      name: 'servicios-generales-dashboard',
      component: ServiciosGeneralesDashboardView,
      meta: { requiereAuth: true, roles: ['SERVICIOS_GENERALES'] },
    },

    {
      path: '/auxiliar-servicios-generales/dashboard',
      name: 'auxiliar-servicios-generales-dashboard',
      component: AuxiliarServiciosGeneralesDashboardView,
      meta: { requiereAuth: true, roles: ['AUXILIAR_SERVICIOS_GENERALES'] },
    },

    {
      path: '/tesoreria/dashboard',
      name: 'tesoreria-dashboard',
      component: TesoreriaDashboardView,
      meta: { requiereAuth: true, roles: ['TESORERIA'] },
    },

    {
      path: '/almacen/dashboard',
      name: 'almacen-dashboard',
      component: AlmacenDashboardView,
      meta: { requiereAuth: true, roles: ['ENCARGADO_COMPRAS_ALMACEN'] },
    },

    {
      path: '/almacen/requerimientos',
      name: 'almacen-requerimientos',
      component: AlmacenDashboardView,
      meta: { requiereAuth: true, roles: ['ENCARGADO_COMPRAS_ALMACEN'] },
    },

    {
      path: '/daf/emitir',
      name: 'daf-emitir',
      component: () => import('../views/DafEmitirView.vue'),
      meta: { requiereAuth: true, roles: ['DAF'] },
    },
    {
      path: '/daf/dashboard',
      name: 'daf-dashboard',
      component: DafDashboardView,
      meta: { requiereAuth: true, roles: ['DAF'] },
    },


    /* =====================================================
       RUTA NO ENCONTRADA
    ===================================================== */

    {
      path: '/:pathMatch(.*)*',
      redirect: '/login',
    },
  ],
})


/* =========================================================
   PROTECCIÓN DE RUTAS
========================================================= */

router.beforeEach(
  (to) => {

    const token =
      localStorage.getItem(
        'sigta_token'
      )


    const usuarioTexto =
      localStorage.getItem(
        'sigta_usuario'
      )


    let usuario = null


    try {

      usuario =
        usuarioTexto
          ? JSON.parse(usuarioTexto)
          : null

    } catch {

      usuario = null
    }


    /* -----------------------------------------------------
       RUTA QUE REQUIERE LOGIN
    ----------------------------------------------------- */

    if (
      to.meta.requiereAuth
      &&
      !token
    ) {

      return '/login'
    }

    /* HU-02: mientras must_change_password siga activo, ninguna
       otra vista debe ser navegable (el backend ya rechaza las
       llamadas a la API con 403; esto evita además que el
       usuario vea una pantalla rota). */
    if (
      to.meta.requiereAuth
      &&
      token
      &&
      usuario?.must_change_password
      &&
      to.path !== '/cambiar-contrasena'
    ) {

      return '/cambiar-contrasena'
    }

    /* El portal del solicitante no debe funcionar como ruta
       de respaldo para actores institucionales. */
    if (to.path.startsWith('/usuario/')) {
      const roles = Array.isArray(usuario?.roles)
        ? usuario.roles.map(rol => String(rol.codigo || '').toUpperCase())
        : []

      if (!roles.includes('SOLICITANTE')) {
        if (roles.includes('ADMIN')) return '/admin/dashboard'
        if (roles.includes('SUPERUSER')) return '/superuser/dashboard'
        if (roles.includes('JEFE_UTIC')) return '/jefe-utic/dashboard'
        if (roles.includes('ESPECIALISTA')) return '/especialista/dashboard'
        if (roles.includes('SERVICIOS_GENERALES')) return '/servicios-generales/dashboard'
        if (roles.includes('AUXILIAR_SERVICIOS_GENERALES')) return '/auxiliar-servicios-generales/dashboard'
        if (roles.includes('TESORERIA')) return '/tesoreria/dashboard'
        if (roles.includes('ENCARGADO_COMPRAS_ALMACEN')) return '/almacen/dashboard'
        if (roles.includes('DAF')) return '/daf/dashboard'
      }
    }


    /* -----------------------------------------------------
       RUTAS ADMIN
    ----------------------------------------------------- */

    if (to.meta.admin) {

      const roles =
        Array.isArray(usuario?.roles)
          ? usuario.roles.map(
              rol =>
                String(
                  rol.codigo || ''
                ).toUpperCase()
            )
          : []


      if (
        !roles.includes('ADMIN')
      ) {

        return '/usuario/dashboard'
      }
    }

    if (Array.isArray(to.meta.roles)) {
      const roles = Array.isArray(usuario?.roles)
        ? usuario.roles.map(rol => String(rol.codigo || '').toUpperCase())
        : []
      if (!to.meta.roles.some(rol => roles.includes(rol))) return '/usuario/dashboard'
    }


    /* -----------------------------------------------------
       USUARIO LOGUEADO EN LOGIN
    ----------------------------------------------------- */

    if (
      to.path === '/login'
      &&
      token
      &&
      usuario
    ) {

      const roles =
        Array.isArray(usuario.roles)
          ? usuario.roles.map(
              rol =>
                String(
                  rol.codigo || ''
                ).toUpperCase()
            )
          : []


      if (
        roles.includes('ADMIN')
      ) {

        return '/admin/dashboard'
      }

      if (roles.includes('SUPERUSER')) return '/superuser/dashboard'
      if (roles.includes('JEFE_UTIC')) return '/jefe-utic/dashboard'
      if (roles.includes('ESPECIALISTA')) return '/especialista/dashboard'
      if (roles.includes('SERVICIOS_GENERALES')) return '/servicios-generales/dashboard'
      if (roles.includes('AUXILIAR_SERVICIOS_GENERALES')) return '/auxiliar-servicios-generales/dashboard'
      if (roles.includes('TESORERIA')) return '/tesoreria/dashboard'
      if (roles.includes('ENCARGADO_COMPRAS_ALMACEN')) return '/almacen/dashboard'
      if (roles.includes('DAF')) return '/daf/dashboard'
    }


    return true
  }
)


export default router
