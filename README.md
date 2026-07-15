Guía y Documentación del Proyecto: Sistema de Registro de Usuarios en Tiempo Real
Autores: Latorre Ronald, Vera Angelo

Tutor del Proyecto: Byron Moreno

Fecha: Julio 2026

Índice
Introducción al Proyecto

Arquitectura del Sistema

Estructura del Repositorio de Archivos

Base de Datos (PostgreSQL)

Servidor Backend (Node.js & Express)

Interfaz de Usuario (HTML5, CSS3 & JS)

Orquestación y Docker Compose

Administración del Sistema con Portainer

Resolución de Problemas Comunes

1. Introducción al Proyecto
Este proyecto consiste en el desarrollo y despliegue de una aplicación web de registro de usuarios en tiempo real utilizando una arquitectura moderna basada en microservicios contenerizados.

El sistema permite capturar datos de identificación (Cédula, Nombres, Apellidos, Teléfono y Dirección), procesarlos a través de una API REST y almacenarlos de forma persistente en una base de datos relacional robusta. Todo el ecosistema está completamente automatizado y orquestado mediante contenedores Docker, gestionado visualmente con Portainer y expuesto de forma segura a través de subdominios SSL con Traefik como proxy inverso.

2. Arquitectura del Sistema
El ecosistema se divide en 4 servicios independientes que se comunican entre sí a través de una red virtual aislada en Docker:

Frontend (app_frontend): Servidor web ligero (Nginx) que sirve la interfaz gráfica de cara al cliente de forma asíncrona.

Backend (app_backend): API REST construida sobre Node.js y Express encargada de validar los datos y actuar como puente con la base de datos.

Base de Datos (app_postgres): Motor PostgreSQL para el almacenamiento persistente de registros.

Gestor Gráfico de Base de Datos (app_pgadmin): Interfaz web (pgAdmin) para realizar auditorías, consultas directas y mantenimiento de las tablas de datos.

3. Estructura del Repositorio de Archivos
Para garantizar la portabilidad del proyecto, los archivos se organizan en el servidor VPS de la siguiente manera:

Plaintext
/root/mi-proyecto/
├── backend/
│   ├── server.js
│   ├── package.json
│   └── Dockerfile
├── frontend/
│   ├── index.html
│   └── Dockerfile
└── docker-compose.yml
4. Base de Datos (PostgreSQL)
El motor de base de datos utiliza una tabla relacional denominada usuarios.

Estructura de la Tabla usuarios
El sistema ejecuta automáticamente una migración y validación en su arranque para asegurar que la tabla cuente con los siguientes campos y tipos de datos:

Campo	Tipo de Dato	Restricción	Descripción
id	SERIAL	PRIMARY KEY	Incremento único para cada registro.
cedula	VARCHAR(20)	UNIQUE, NOT NULL	Documento único de identificación del usuario.
telefono	VARCHAR(20)	Opcional	Teléfono celular de contacto.
primer_nombre	VARCHAR(50)	NOT NULL	Primer nombre obligatorio.
segundo_nombre	VARCHAR(50)	Opcional	Segundo nombre del usuario.
primer_apellido	VARCHAR(50)	NOT NULL	Primer apellido obligatorio.
segundo_apellido	VARCHAR(50)	Opcional	Segundo apellido del usuario.
direccion	VARCHAR(150)	Opcional	Lugar de residencia / dirección física.
fecha_registro	TIMESTAMP	DEFAULT NOW()	Fecha y hora de creación automática.
5. Servidor Backend (Node.js & Express)
El archivo server.js gestiona la lógica del lado del servidor. Se conecta a la base de datos utilizando el módulo pg (PostgreSQL Client) mediante variables de entorno configurables en Docker.

Endpoints de la API REST
GET /api/datos

Descripción: Recupera la lista de todos los usuarios registrados en orden descendente según su fecha de registro.

Respuesta Exitosa (200 OK): JSON con un arreglo de objetos de usuarios.

POST /api/datos

Descripción: Recibe el payload del formulario, valida los campos obligatorios, e inserta el nuevo registro en la base de datos.

Respuesta Exitosa (211 Created): Retorna el objeto del usuario recién insertado.

Error de Duplicidad (400 Bad Request): Controla el código de error 23505 de Postgres (violación de restricción única de cédula) para alertar al cliente.

6. Interfaz de Usuario (HTML5, CSS3 & JS)
La interfaz se ubica en /frontend/index.html y fue desarrollada bajo estándares modernos de diseño web responsivo (Grid Layout de CSS) con un aspecto nocturno (Dark Mode).

Características Principales del Frontend:
Orden de Llenado Optimizado: Organizado de forma lógica priorizando la identidad (Nombres, Apellidos) seguido de los identificadores (Cédula, Teléfono) y finalmente la ubicación (Dirección).

Consumo de API Asíncrono (AJAX - Fetch API): Los registros nuevos se guardan y se listan inmediatamente en el panel inferior en tiempo real sin necesidad de recargar el navegador.

Pie de Página Académico: Bloque inferior que detalla las firmas de responsabilidad del proyecto académico (Ronald Latorre y Angelo Vera) y la tutoría del docente.

7. Orquestación y Docker Compose
La declaración de todo nuestro entorno se realiza en el archivo principal docker-compose.yml. Los volúmenes aseguran que el ciclo de vida de los contenedores no destruya los registros físicos del disco.

YAML
version: '3.8'

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
8. Administración del Sistema con Portainer
Para las tareas de monitorización y despliegue continuo (CI/CD) se utiliza Portainer, una consola visual intuitiva accesible de manera remota.

Tareas Operativas Claves en Portainer:
Reinicio de Servicios (Hot Reload): Desde el módulo Containers, seleccionando app_backend o app_frontend y ejecutando la opción Restart para aplicar modificaciones de código hechas en caliente en los archivos del VPS.

Verificación de Consola: Capacidad de abrir terminales interactivas (/bin/sh) en caliente directamente desde el navegador en cualquier contenedor de la infraestructura.

Auditoría de Logs: Acceso rápido a las salidas estándar de Node.js y PostgreSQL para rastrear consultas de red y posibles fallos.

9. Resolución de Problemas Comunes
Error Permission Denied al guardar código en SSH:

Causa: El usuario actual carece de privilegios sobre el directorio /root.

Solución: Acceder al servidor directamente bajo la cuenta del superusuario root, o anteponer la utilidad sudo en caso de contar con permisos en la lista de sudoers.

Error Password authentication failed for user "admin" en pgAdmin:

Causa: El volumen físico de la base de datos ya existía con una contraseña previa, ignorando el valor actual declarado en el archivo YAML de Docker Compose.

Solución: Probar contraseñas anteriores configuradas al inicio del entorno, o remover el volumen pg_data mediante Portainer y volver a desplegar si se requiere una base limpia desde cero.

Contenedor no refleja cambios:

Solución: Forzar la reconstrucción de las imágenes con docker compose down y docker compose up --build -d o forzar el reinicio manual del servicio desde el panel web de Portainer.
