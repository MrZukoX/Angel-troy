# 🚀 Sistema de Registro de Usuarios en Tiempo Real

Este proyecto es una aplicación web moderna basada en microservicios contenerizados. Permite capturar datos de identificación personal, procesarlos a través de una API REST y almacenarlos de forma persistente en una base de datos relacional. 

Toda la infraestructura está automatizada mediante **Docker**, orquestada con **Docker Compose**, gestionada visualmente con **Portainer** y expuesta de manera segura.

---

## 👥 Datos del Proyecto

* **Autores:** * Latorre Ronald 🧑‍💻 Vera Angelo 🧑‍💻
* **Tutor del Proyecto:** Byron Moreno 👨‍🏫
* **Entorno:** Servidor VPS con Docker & Portainer

---

## 🛠️ Arquitectura del Sistema

El ecosistema se divide en 4 servicios independientes que se comunican de forma segura dentro de una red virtual aislada en Docker:

1. **Frontend (`app_frontend`):** Servidor web ligero con Nginx que sirve la interfaz web responsiva (HTML5, CSS3, JS).
2. **Backend (`app_backend`):** API REST en Node.js y Express que gestiona las peticiones de datos y la conexión a la base de datos.
3. **Base de Datos (`app_postgres`):** Servidor de PostgreSQL para el almacenamiento persistente y seguro de los datos.
4. **Administración de Base de Datos (`app_pgadmin`):** Interfaz gráfica web (pgAdmin) para auditar y consultar las tablas de datos de manera visual.

---

## 📂 Estructura del Proyecto

```text
/root/mi-proyecto/
├── backend/
│   ├── server.js
│   ├── package.json
│   └── Dockerfile
├── frontend/
│   ├── index.html
│   └── Dockerfile
└── docker-compose.yml
💾 Estructura de la Base de Datos

El sistema crea y valida automáticamente la tabla usuarios en PostgreSQL en cada arranque del backend con la siguiente estructura:CampoTipo de DatoRestriccionesDescripciónidSERIALPRIMARY KEYIncremento único para cada registro.cedulaVARCHAR(20)UNIQUE, NOT NULLDocumento único de identificación.primer_nombreVARCHAR(50)NOT NULLPrimer nombre (Obligatorio).segundo_nombreVARCHAR(50)OpcionalSegundo nombre del usuario.primer_apellidoVARCHAR(50)NOT NULLPrimer apellido (Obligatorio).segundo_apellidoVARCHAR(50)OpcionalSegundo apellido del usuario.telefonoVARCHAR(20)OpcionalTeléfono celular de contacto.direccionVARCHAR(150)OpcionalUbicación o dirección física de domicilio.fecha_registroTIMESTAMPDEFAULT NOW()Fecha y hora de creación automática.🔌 API Endpoints (Backend)GET /api/datosDescripción: Obtiene la lista de todos los usuarios de la base de datos ordenados por fecha de registro (el más reciente primero).Respuesta Exitosa (200 OK): Arreglo en formato JSON.POST /api/datosDescripción: Recibe el formulario del usuario, valida que los campos requeridos no estén vacíos, e inserta el nuevo registro.Respuesta Exitosa (211 Created): Retorna el objeto del usuario creado.Manejo de Errores (400 Bad Request): Captura el código de error 23505 (Cédula duplicada) y devuelve una alerta amigable.🐳 Archivo de Orquestación (docker-compose.yml)El archivo principal para levantar toda la infraestructura de la aplicación con un solo comando es el siguiente:YAMLversion: '3.8'

services:
  postgres-db:
    image: postgres:15-alpine
    container_name: app_postgres
    restart: always
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: password123
      POSTGRES_DB: app_db
    volumes:
      - pg_data:/var/lib/postgresql/data
    networks:
      - app-network

  pgadmin:
    image: dpage/pgadmin4
    container_name: app_pgadmin
    restart: always
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@byronrm.com
      PGADMIN_DEFAULT_PASSWORD: password123
    networks:
      - app-network

  backend:
    build: ./backend
    container_name: app_backend
    restart: always
    environment:
      DB_USER: admin
      DB_HOST: postgres-db
      DB_NAME: app_db
      DB_PASSWORD: password123
      DB_PORT: 5432
    depends_on:
      - postgres-db
    networks:
      - app-network

  frontend:
    build: ./frontend
    container_name: app_frontend
    restart: always
    ports:
      - "80:80"
    depends_on:
      - backend
    networks:
      - app-network

volumes:
  pg_data:

networks:
  app-network:
    driver: bridge
🎨 Características de la Interfaz Web (Frontend)Formulario Ordenado: Estructura limpia y responsiva organizada por:Nombre y Apellido (Campos prioritarios de identidad).Cédula y Teléfono.Dirección física de vivienda (Campo completo).Consumo de API en Tiempo Real: El listado inferior se actualiza de manera asíncrona (AJAX mediante Fetch API) inmediatamente después de enviar el formulario, sin necesidad de recargar la página.Aspecto Moderno: Estilo visual oscuro (Dark Mode) para mayor comodidad visual del usuario y una mejor experiencia móvil.🔧 Gestión Continua con PortainerPara facilitar la monitorización en caliente:Módulo de Contenedores: Permite realizar un Restart rápido a los contenedores app_backend y app_frontend cuando se realizan cambios directos de código en los archivos del VPS.Control de Logs: Inspección en tiempo real de consultas SQL y peticiones entrantes para auditorías rápidas.
---

### 💡 ¿Cómo subirlo a GitHub rápido?
1. Entra a tu repositorio en la página web de GitHub.
2. Haz clic en **Add file** -> **Create new file**.
3. En el nombre del archivo escribe exactamente: `README.md`.
4. Pega el código de arriba en la caja de texto.
5. Ve abajo del todo, haz clic en el botón verde **Commit changes** ¡y listo! Se verá increíblement
