<template>

  <div class="layout">

    <AdminMenu />

    <main>

      <header>

        <div>

          <h1>
            Portal Solicitante
          </h1>

          <p>
            Vista de autoservicio y seguimiento de
            Soporte Técnico, Mantenimiento y Compras.
          </p>

        </div>

        <button
          @click="
            router.push(
              '/usuario/dashboard'
            )
          "
        >
          Abrir portal
        </button>

      
        <UsuarioHeader @actualizar="cargarTodo" />
      </header>


      <section class="cards">

        <article>

          <strong>
            {{ soporte.length }}
          </strong>

          <span>
            Solicitudes de Soporte
          </span>

        </article>


        <article>

          <strong>
            {{ mantenimiento.length }}
          </strong>

          <span>
            Requerimientos de Mantenimiento
          </span>

        </article>


        <article>

          <strong>
            {{ compras.length }}
          </strong>

          <span>
            Solicitudes de Compra
          </span>

        </article>


        <article>

          <strong>
            {{ total }}
          </strong>

          <span>
            Total de registros
          </span>

        </article>

      </section>


      <section class="table-card">

        <div class="table-header">

          <div>
            <span class="section-label">
              SEGUIMIENTO GENERAL
            </span>

            <h2>
              Requerimientos y solicitudes registradas
            </h2>
          </div>

          <span class="count">
            {{ total }} registro(s)
          </span>

        </div>


        <div
          v-if="cargando"
          class="empty"
        >
          Cargando registros...
        </div>


        <div
          v-else-if="requerimientos.length === 0"
          class="empty"
        >
          No existen registros para mostrar.
        </div>


        <div
          v-else
          class="table"
        >

          <div class="row head">

            <span>Código</span>
            <span>Título</span>
            <span>Proceso</span>
            <span>Estado</span>

          </div>


          <div
            v-for="item in requerimientos"
            :key="`${item.modulo}-${item.id}`"
            class="row"
          >

            <strong>
              {{ item.codigo }}
            </strong>

            <span>
              {{ item.titulo }}
            </span>

            <span>
              {{ item.modulo }}
            </span>

            <span>
              {{ item.estado }}
            </span>

          </div>

        </div>

      </section>

    </main>

  </div>

</template>


<script setup>
import UsuarioHeader from '../components/UsuarioHeader.vue'

import {
  computed,
  onMounted,
  ref
} from 'vue'

import {
  useRouter
} from 'vue-router'

import AdminMenu
  from '../components/AdminMenu.vue'


const router =
  useRouter()


const soporte =
  ref([])

const mantenimiento =
  ref([])

const compras =
  ref([])

const cargando =
  ref(true)


const token =
  localStorage.getItem(
    'sigta_token'
  )


onMounted(
  async () => {

    if (!token) {

      router.push(
        '/login'
      )

      return
    }


    await cargarTodo()
  }
)


function normalizarLista(
  datos
) {

  if (
    Array.isArray(datos)
  ) {

    return datos
  }


  if (
    Array.isArray(
      datos?.results
    )
  ) {

    return datos.results
  }


  return []
}


async function cargarEndpoint(
  url
) {

  const respuesta =
    await fetch(
      url,
      {
        headers: {

          Authorization:
            `Token ${token}`,

          Accept:
            'application/json',
        }
      }
    )


  if (
    respuesta.status === 401
    ||
    respuesta.status === 403
  ) {

    localStorage.removeItem(
      'sigta_token'
    )

    localStorage.removeItem(
      'sigta_usuario'
    )

    router.push(
      '/login'
    )

    throw new Error(
      'Sesión no autorizada.'
    )
  }


  if (!respuesta.ok) {

    throw new Error(
      `Error ${respuesta.status}`
    )
  }


  return normalizarLista(
    await respuesta.json()
  )
}


async function cargarTodo() {

  cargando.value =
    true


  try {

    const resultados =
      await Promise.allSettled([

        cargarEndpoint(
          '/api/soporte/tickets/'
        ),

        cargarEndpoint(
          '/api/mantenimiento/requerimientos/'
        ),

        cargarEndpoint(
          '/api/compras/solicitudes/'
        ),
      ])

    soporte.value = resultados[0].status === 'fulfilled' ? resultados[0].value : []
    mantenimiento.value = resultados[1].status === 'fulfilled' ? resultados[1].value : []
    compras.value = resultados[2].status === 'fulfilled' ? resultados[2].value : []

    const fallos = resultados.filter(resultado => resultado.status === 'rejected')
    if (fallos.length) {
      console.error('Portal solicitante: carga parcial', fallos.map(resultado => resultado.reason))
    }


  } catch (error) {

    console.error(
      'Portal solicitante:',
      error
    )


  } finally {

    cargando.value =
      false
  }
}


const total =
  computed(() => {

    return (
      soporte.value.length
      +
      mantenimiento.value.length
      +
      compras.value.length
    )
  })


const requerimientos =
  computed(() => {

    const st =
      soporte.value.map(
        item => ({

          id:
            item.id,

          codigo:
            item.codigo,

          titulo:
            item.titulo,

          modulo:
            'Soporte Técnico',

          estado:
            item.estado_nombre
            || item.estado_codigo
            || item.estado
            || 'Registrado',

          fecha:
            item.creado_en
            || item.created_at
            || null,
        })
      )


    const mt =
      mantenimiento.value.map(
        item => ({

          id:
            item.id,

          codigo:
            item.codigo,

          titulo:
            item.titulo
            || item.descripcion
            || 'Requerimiento de mantenimiento',

          modulo:
            'Mantenimiento',

          estado:
            item.estado_nombre
            || item.estado_codigo
            || item.estado
            || 'Registrado',

          fecha:
            item.creado_en
            || item.created_at
            || null,
        })
      )


    const cmp =
      compras.value.map(
        item => ({

          id:
            item.id,

          codigo:
            item.codigo,

          titulo:
            item.titulo
            || item.descripcion
            || 'Solicitud de compra',

          modulo:
            'Compras',

          estado:
            item.estado_nombre
            || item.estado
            || 'Registrado',

          fecha:
            item.creado_en
            || item.created_at
            || null,
        })
      )


    return [
      ...st,
      ...mt,
      ...cmp
    ]
      .sort(
        (a, b) => {

          const fechaA =
            new Date(
              a.fecha
              || 0
            ).getTime()

          const fechaB =
            new Date(
              b.fecha
              || 0
            ).getTime()


          if (
            fechaA
            &&
            fechaB
          ) {

            return fechaB - fechaA
          }


          return (
            Number(b.id || 0)
            -
            Number(a.id || 0)
          )
        }
      )
  })

</script>


<style scoped>

* {
  box-sizing: border-box;
}


.layout {

  min-height: 100vh;

  display: flex;

  background: var(--sigta-azul-tenue);

  font-family: var(--sigta-fuente);
}


main {

  flex: 1;

  min-width: 0;

  padding: 28px;
}


header {

  display: flex;

  align-items: center;

  justify-content:
    space-between;

  gap: 15px;
}


.breadcrumb {

  display: block;

  margin-bottom: 6px;

  color: var(--sigta-texto-suave);

  font-size: 9px;
}


header h1 {

  margin: 0;

  color: var(--sigta-texto);

  font-size: 28px;
}


header p {

  margin: 6px 0 0;

  color: var(--sigta-texto-suave);

  font-size: 11px;
}


header button {

  min-height: 42px;

  padding:
    0 17px;

  border: none;

  border-radius: 7px;

  background: var(--sigta-mostaza);

  color: var(--sigta-texto);

  font-weight: 800;

  cursor: pointer;
}


.cards {

  display: grid;

  grid-template-columns:
    repeat(4,1fr);

  gap: 14px;

  margin:
    23px 0;
}


.cards article {

  padding: 20px;

  border-top:
    3px solid var(--sigta-azul);

  border-radius: 9px;

  background: white;

  box-shadow:
    0
    3px
    12px
    rgba(0,0,0,.04);
}


.cards strong,
.cards span {

  display: block;
}


.cards strong {

  color: var(--sigta-azul);

  font-size: 27px;
}


.cards span {

  margin-top: 7px;

  color: var(--sigta-texto-suave);

  font-size: 10px;
}


.table-card {

  padding: 20px;

  border-radius: 9px;

  background: white;

  box-shadow:
    0
    3px
    12px
    rgba(0,0,0,.04);
}


.table-header {

  display: flex;

  align-items: center;

  justify-content:
    space-between;

  gap: 15px;

  margin-bottom: 12px;
}


.section-label {

  display: block;

  margin-bottom: 4px;

  color: var(--sigta-azul);

  font-size: 7px;

  font-weight: 900;

  letter-spacing: .8px;
}


.table-card h2 {

  margin: 0;

  color: var(--sigta-texto);

  font-size: 17px;
}


.count {

  padding:
    5px 8px;

  border-radius: 14px;

  background: var(--sigta-azul-tenue);

  color: var(--sigta-azul);

  font-size: 8px;

  font-weight: 800;
}


.row {

  min-height: 48px;

  display: grid;

  grid-template-columns:
    150px
    1fr
    160px
    150px;

  align-items: center;

  gap: 10px;

  padding:
    0 12px;

  border-bottom:
    1px solid var(--sigta-azul-tenue);

  color: var(--sigta-texto-suave);

  font-size: 10px;
}


.row.head {

  background: var(--sigta-azul-tenue);

  color: var(--sigta-texto-suave);

  font-weight: 800;
}


.row strong {

  color: var(--sigta-azul);
}


.empty {

  padding: 30px;

  color: var(--sigta-texto-suave);

  text-align: center;

  font-size: 10px;
}


@media (
  max-width: 1000px
) {

  .cards {

    grid-template-columns:
      repeat(2,1fr);
  }

}


@media (
  max-width: 760px
) {

  .layout {

    display: block;
  }


  main {

    padding: 16px;
  }


  header {

    align-items:
      flex-start;

    flex-direction:
      column;
  }


  .cards {

    grid-template-columns:
      1fr;
  }


  .table {

    overflow-x: auto;
  }


  .row {

    min-width: 700px;
  }

}

</style>

