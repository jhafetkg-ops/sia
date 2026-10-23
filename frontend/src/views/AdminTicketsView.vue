<template>

  <div class="layout">

    <AdminMenu />


    <main class="page">

      <header>

        <div>

          <h1>
            Consulta de requerimientos
          </h1>

          <p>
            Consulta global de Soporte Técnico,
            Mantenimiento y Compras.
          </p>

        </div>

        <button
          @click="
            router.push(
              '/admin/dashboard'
            )
          "
        >
          Volver al Dashboard
        </button>

      
        <UsuarioHeader @actualizar="cargarTodo" />
      </header>


      <section class="stats">

        <article>

          <span>
            Soporte Técnico
          </span>

          <strong>
            {{ soporte.length }}
          </strong>

        </article>


        <article>

          <span>
            Mantenimiento
          </span>

          <strong>
            {{ mantenimiento.length }}
          </strong>

        </article>


        <article>

          <span>
            Compras
          </span>

          <strong>
            {{ compras.length }}
          </strong>

        </article>


        <article>

          <span>
            Total
          </span>

          <strong>
            {{ registros.length }}
          </strong>

        </article>

      </section>


      <section class="filters">

        <input
          v-model="busqueda"
          placeholder="Buscar código, título o solicitante..."
        />


        <select
          v-model="tipo"
        >

          <option value="">
            Todos
          </option>

          <option value="SOPORTE">
            Soporte Técnico
          </option>

          <option value="MANTENIMIENTO">
            Mantenimiento
          </option>

          <option value="COMPRAS">
            Compras
          </option>

        </select>

      </section>


      <section class="table">

        <div
          v-if="cargando"
          class="empty"
        >
          Cargando registros...
        </div>


        <div
          v-else-if="filtrados.length === 0"
          class="empty"
        >
          No existen registros que coincidan con la búsqueda.
        </div>


        <div
          v-for="item in filtrados"
          v-else
          :key="`${item.tipo}-${item.id}`"
          class="row"
        >

          <div class="code">
            {{ item.codigo }}
          </div>


          <div class="info">

            <strong>
              {{ item.titulo }}
            </strong>

            <span>
              {{
                item.solicitante_nombre
                || 'Sin solicitante'
              }}
            </span>

          </div>


          <span
            class="tag"
          >
            {{ item.tipoTexto }}
          </span>


          <span
            class="status"
          >
            {{ item.estadoTexto }}
          </span>

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

const busqueda =
  ref('')

const tipo =
  ref('')


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

    const [
      soporteData,
      mantenimientoData,
      comprasData
    ] =
      await Promise.all([

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


    soporte.value =
      soporteData


    mantenimiento.value =
      mantenimientoData


    compras.value =
      comprasData


  } catch (error) {

    console.error(
      'Consulta global:',
      error
    )


  } finally {

    cargando.value =
      false
  }
}


const registros =
  computed(() => [

    ...soporte.value.map(
      item => ({

        ...item,

        tipo:
          'SOPORTE',

        tipoTexto:
          'Soporte Técnico',

        titulo:
          item.titulo
          || item.descripcion
          || 'Solicitud de soporte',

        estadoTexto:
          item.estado_nombre
          || item.estado_codigo
          || item.estado
          || 'Registrado',
      })
    ),


    ...mantenimiento.value.map(
      item => ({

        ...item,

        tipo:
          'MANTENIMIENTO',

        tipoTexto:
          'Mantenimiento',

        titulo:
          item.titulo
          || item.descripcion
          || 'Requerimiento de mantenimiento',

        estadoTexto:
          item.estado_nombre
          || item.estado_codigo
          || item.estado
          || 'Registrado',
      })
    ),


    ...compras.value.map(
      item => ({

        ...item,

        tipo:
          'COMPRAS',

        tipoTexto:
          'Compras',

        titulo:
          item.titulo
          || item.descripcion
          || 'Solicitud de compra',

        estadoTexto:
          item.estado_nombre
          || item.estado
          || 'Registrado',
      })
    ),

  ])


const filtrados =
  computed(() => {

    const q =
      busqueda.value
        .toLowerCase()
        .trim()


    return registros.value.filter(
      item => {

        const tipoOk =
          !tipo.value
          ||
          item.tipo === tipo.value


        const texto =
          [
            item.codigo,
            item.titulo,
            item.solicitante_nombre,
            item.tipoTexto,
          ]
            .filter(Boolean)
            .join(' ')
            .toLowerCase()


        const textoOk =
          !q
          ||
          texto.includes(q)


        return (
          tipoOk
          &&
          textoOk
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


.page {

  flex: 1;

  min-width: 0;

  min-height: 100vh;

  padding: 28px;
}


header {

  display: flex;

  justify-content:
    space-between;

  align-items: center;

  gap: 18px;
}


.breadcrumb {

  display: block;

  margin-bottom: 6px;

  color: var(--sigta-texto-suave);

  font-size: 9px;
}


h1 {

  margin: 0;

  color: var(--sigta-texto);

  font-size: 27px;
}


header p {

  margin: 6px 0 0;

  color: var(--sigta-texto-suave);

  font-size: 11px;
}


header button {

  min-height: 42px;

  padding:
    0 16px;

  border: none;

  border-radius: 7px;

  background: var(--sigta-azul);

  color: white;

  font-size: 9px;

  font-weight: 800;

  cursor: pointer;
}


.stats {

  display: grid;

  grid-template-columns:
    repeat(4,1fr);

  gap: 14px;

  margin:
    20px 0;
}


.stats article {

  padding: 18px;

  border-top:
    3px solid var(--sigta-mostaza);

  border-radius: 9px;

  background: white;

  box-shadow:
    0
    3px
    12px
    rgba(0,0,0,.04);
}


.stats span {

  color: var(--sigta-texto-suave);

  font-size: 9px;
}


.stats strong {

  display: block;

  margin-top: 5px;

  color: var(--sigta-azul);

  font-size: 25px;
}


.filters {

  display: grid;

  grid-template-columns:
    1fr
    220px;

  gap: 10px;

  margin-bottom: 15px;
}


.filters input,
.filters select {

  height: 42px;

  padding:
    0
    12px;

  border:
    1px solid var(--sigta-borde);

  border-radius: 7px;

  background: white;
}


.table {

  overflow: hidden;

  border-radius: 10px;

  background: white;

  box-shadow:
    0
    3px
    12px
    rgba(0,0,0,.04);
}


.row {

  display: grid;

  grid-template-columns:
    150px
    1fr
    150px
    150px;

  align-items: center;

  gap: 12px;

  padding: 16px;

  border-bottom:
    1px solid var(--sigta-azul-tenue);
}


.code {

  color: var(--sigta-azul);

  font-weight: 800;
}


.info strong,
.info span {

  display: block;
}


.info span {

  margin-top: 4px;

  color: var(--sigta-texto-suave);

  font-size: 11px;
}


.tag {

  color: var(--sigta-azul);

  font-size: 9px;

  font-weight: 800;
}


.status {

  padding:
    5px
    8px;

  border-radius: 20px;

  background: var(--sigta-azul-tenue);

  text-align: center;

  font-size: 10px;
}


.empty {

  padding: 35px;

  color: var(--sigta-texto-suave);

  text-align: center;

  font-size: 10px;
}


@media (
  max-width: 1000px
) {

  .stats {

    grid-template-columns:
      repeat(2,1fr);
  }

}


@media (
  max-width: 700px
) {

  .layout {

    display: block;
  }


  .page {

    padding: 15px;
  }


  header {

    align-items:
      flex-start;

    flex-direction:
      column;

    gap: 12px;
  }


  .stats,
  .filters {

    grid-template-columns:
      1fr;
  }


  .row {

    grid-template-columns:
      1fr;
  }

}

</style>
