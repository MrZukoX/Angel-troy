# angeltroy — despliegue 


Todo se hace por clicks en `http://portainerat.byronrm.com/`, en este orden:
**Images (construir) → Volumes (persistencia) → Networks (red interna) → Containers (levantar los 3)**

---

## Paso 1 — Construir la imagen del backend

1. Portainer → menú lateral → **Images**.
2. Botón **+ Build a new image** (arriba a la derecha).
3. **Name**: `angeltroy-backend:latest`
4. **Build method**: `Upload`
5. Sube el archivo `angeltroy-backend-context.tar`.
6. Deja **Dockerfile path** como `Dockerfile` (ya está en la raíz del tar).
7. Botón **Build the image**. Espera a que termine (verás el log del build en vivo).

## Paso 2 — Construir la imagen del frontend

Repite lo mismo:
1. **Images → + Build a new image**.
2. **Name**: `angeltroy-frontend:latest`
3. **Build method**: `Upload` → sube `angeltroy-frontend-context.tar`.
4. **Build the image**.

Al terminar, en **Images** deberías ver `angeltroy-backend:latest` y `angeltroy-frontend:latest` en la lista, junto con `traefik:v2.11` y las demás que ya tenías.

---

## Paso 3 — Crear el volumen para la base de datos (persistencia)

1. Portainer → **Volumes → + Add volume**.
2. **Name**: `angeltroy_db_data`
3. Driver: `local` (por defecto).
4. **Create the volume**.

---

## Paso 4 — Crear la red interna (para que backend y db se hablen)

1. Portainer → **Networks → + Add network**.
2. **Name**: `angeltroy_internal`
3. Driver: `bridge`.
4. Deja el resto por defecto → **Create the network**.

---

## Paso 5 — Levantar el contenedor de la base de datos

1. Portainer → **Containers → + Add container**.
2. **Name**: `angeltroy_db`
3. **Image**: `postgres:16-alpine`
4. Baja a **Network** → selecciona `angeltroy_internal` (la que creaste en el paso 4).
5. Ve a la pestaña **Volumes** (dentro del formulario) → **map additional volume**:
   - **Container**: `/var/lib/postgresql/data`
   - **Volume**: selecciona `angeltroy_db_data` (el que creaste en el paso 3)
6. Ve a la pestaña **Env** → agrega 3 variables:
   | name | value |
   |---|---|
   | `POSTGRES_USER` | `angeltroy` |
   | `POSTGRES_PASSWORD` | 24810 |
   | `POSTGRES_DB` | `angeltroy` |
7. Ve a **Restart policy** → selecciona `Unless stopped`.
8. Botón **Deploy the container**.

---

## Paso 6 — Levantar el contenedor del backend (API)

1. **Containers → + Add container**.
2. **Name**: `angeltroy_backend`
3. **Image**: `angeltroy-backend:latest`
4. **Network**: `angeltroy_internal` (misma red que la base de datos, para que se vean entre sí por nombre).
5. Pestaña **Ports**:
   - **map additional port** → host `4000` → container `4000` → protocolo `TCP`.
6. Pestaña **Env** → agrega:
   | name | value |
   |---|---|
   | `PGHOST` | `angeltroy_db` |
   | `PGPORT` | `5432` |
   | `PGUSER` | `angeltroy` |
   | `PGPASSWORD` | *(la misma contraseña del paso 5)* |
   | `PGDATABASE` | `angeltroy` |
   | `PORT` | `4000` |
7. **Restart policy**: `Unless stopped`.
8. **Deploy the container**.

Verifica que arrancó bien: click en `angeltroy_backend` → **Logs**. Deberías ver `Tabla "tasks" verificada/creada correctamente.` y `API escuchando en el puerto 4000`.

---

## Paso 7 — Levantar el contenedor del frontend (con Traefik)

1. **Containers → + Add container**.
2. **Name**: `angeltroy_frontend`
3. **Image**: `angeltroy-frontend:latest`
4. **Network**: `root_default` (la red donde vive tu Traefik — **esta es la clave** para que te dé HTTPS automático).
5. Pestaña **Env** → agrega:
   | name | value |
   |---|---|
   | `API_URL` | `http://144.91.95.161:4000` |
6. Pestaña **Labels** → agrega estas 6 labels (name / value):
   | name | value |
   |---|---|
   | `traefik.enable` | `true` |
   | `traefik.docker.network` | `root_default` |
   | `traefik.http.routers.angeltroy-front.rule` | `` Host(`angeltroy.byronrm.com`) `` |
   | `traefik.http.routers.angeltroy-front.entrypoints` | `websecure` |
   | `traefik.http.routers.angeltroy-front.tls.certresolver` | `letsencrypt` |
   | `traefik.http.services.angeltroy-front.loadbalancer.server.port` | `80` |
7. **Restart policy**: `Unless stopped`.
8. **Deploy the container**.

---

## Paso 8 — Abrir el puerto del backend

Esto sí requiere una consola, pero **puedes usar la consola web de Portainer**, sin SSH externo:
1. Portainer → **Containers** → busca cualquier contenedor con acceso a shell (o usa **Host → Console** si tu versión de Portainer lo expone), o pide a quien administra el proveedor del VPS que abra el puerto `4000/tcp` en el firewall/panel de control (muchos proveedores como Hetzner, Contabo, etc. tienen esto en su panel web, sin necesidad de SSH).
2. Si tu Portainer tiene acceso al **Host** (menú lateral → *Host* en algunas versiones), ahí a veces hay una opción de consola del propio servidor.

Si de plano no tienes forma de abrir el puerto sin SSH, dime y ajustamos el backend para que use el mismo Traefik (HTTPS, sin necesitar abrir puertos nuevos) — ver la sección "Alternativa" más abajo.

---

## Paso 9 — Verificar

- `http://144.91.95.161:4000/api/health` → `{"status":"ok","db":"conectada"}`
- `https://angeltroy.byronrm.com` → el gestor de tareas, con el punto de estado en verde arriba a la derecha.
- Crea, marca como hecha y borra una tarea. Recarga la página — deben seguir ahí.

---

## Alternativa recomendada: backend también por Traefik (evita abrir puertos y el aviso de "contenido mixto")

Si en el paso 8 no puedes abrir el firewall, esta opción es mejor de todos modos: el backend también pasa por Traefik, con HTTPS, sin publicar ningún puerto nuevo.

Necesitas un registro DNS nuevo (igual que los otros): `apiangeltroy.byronrm.com → 144.91.95.161`. Si puedes crear ese registro, dime y te reescribo el Paso 6 y el Paso 7 para que el backend también viva en la red `root_default` con sus propias labels de Traefik, en vez de publicar el puerto 4000.

---

## Actualizar la app más adelante

Cuando cambies el código: reconstruye la imagen correspondiente (**Images → + Build a new image**, mismo nombre `angeltroy-backend:latest` o `angeltroy-frontend:latest`, sube el tar actualizado — sobrescribe la anterior), luego en **Containers**, entra al contenedor viejo (`angeltroy_backend` o `angeltroy_frontend`) → **Recreate** (Portainer tiene un botón "Recreate" que lo destruye y crea de nuevo con la imagen más reciente del mismo nombre, sin perder la configuración). La base de datos nunca se toca porque vive en el volumen `angeltroy_db_data`, no en el contenedor.
