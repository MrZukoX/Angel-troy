from flask import Flask, request, render_template_string, jsonify
from datetime import datetime
import calendar
import random
import re

app = Flask(__name__)

VERSION = "1.8.0"

MESES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

TAREAS_DEVOPS = {
    5: ["Mantenimiento programado de Base de Datos", "Backup semanal"],
    12: ["Despliegue a Producción v2.1.0"],
    18: ["Auditoría de Seguridad - Parche de contenedores Docker"],
    25: ["Revisión de logs y optimización de índices en AWS"]
}

ESTILOS_CSS = """
body {
    background-color: var(--bs-body-bg);
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    transition: background-color 0.3s, color 0.3s;
}
.gradient-header {
    background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
    color: white;
}
.card {
    border: none;
    border-radius: 16px;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03);
    transition: all 0.3s;
}
.btn-nav {
    background-color: var(--bs-tertiary-bg);
    border: 1px solid var(--bs-border-color);
    color: var(--bs-body-color);
    transition: all 0.2s;
}
.btn-nav:hover { background-color: #6366f1; color: white; border-color: #6366f1; }

.btn-hoy {
    background-color: #ecfdf5; color: #059669; border: 1px solid #a7f3d0;
}
[data-bs-theme="dark"] .btn-hoy {
    background-color: #064e3b; color: #34d399; border: 1px solid #047857;
}
.btn-hoy:hover { background-color: #059669; color: white; }

.titulo-mes { font-size: 1.5rem; font-weight: 700; color: #4f46e5; text-transform: capitalize; }
[data-bs-theme="dark"] .titulo-mes { color: #818cf8; }

.table th { color: #94a3b8; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; }
.table td { font-weight: 600; color: var(--bs-body-color); width: 45px; height: 50px; cursor: pointer; border-radius: 8px; position: relative; }
.table td:not(.noday):hover { background-color: var(--bs-secondary-bg-subtle); }
.noday { color: #cbd5e1 !important; cursor: default !important; }
[data-bs-theme="dark"] .noday { color: #475569 !important; }

.tiene-tarea::after {
    content: ''; position: absolute; bottom: 4px; left: 50%; transform: translateX(-50%);
    width: 6px; height: 6px; background-color: #f59e0b; border-radius: 50%;
}

.terminal-logs {
    background-color: #0f172a; font-family: 'Courier New', Courier, monospace; font-size: 0.85rem;
    border-radius: 8px; padding: 15px; max-height: 200px; overflow-y: auto;
}
.log-info { color: #38bdf8; }
.log-success { color: #34d399; }
.log-error { color: #f87171; animation: blinker 1.5s linear infinite; }

@keyframes blinker { 50% { opacity: 0.5; } }

.btn-theme-toggle {
    background: rgba(255, 255, 255, 0.15); border: none; color: white;
    padding: 8px 12px; border-radius: 50rem; font-weight: 500; transition: all 0.2s;
}
.btn-theme-toggle:hover { background: rgba(255, 255, 255, 0.3); }

.reloj-contenedor { background-color: var(--bs-light-bg-subtle); border: 1px solid var(--bs-border-color-translucent); }
"""

PLANTILLA_HTML = """
<!DOCTYPE html>
<html lang="es" data-bs-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DevOps Pro Panel - Angelo Vera</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
    <style>{{ estilos_css | safe }}</style>
</head>
<body>

    <!-- Encabezado -->
    <div class="gradient-header py-4 mb-4 shadow-sm">
        <div class="container d-flex flex-column flex-sm-row justify-content-between align-items-center gap-3">
            <div>
                <h1 class="h3 mb-0 fw-bold"><i class="bi bi-shield-lock me-2 text-info"></i>DevOps Control Center</h1>
                <small class="opacity-75">Estado General: <span id="status-global-badge" class="badge bg-success">ONLINE</span></small>
            </div>
            <div class="d-flex align-items-center flex-wrap justify-content-center gap-3">
                <button class="btn-theme-toggle shadow-sm" id="themeToggler" onclick="cambiarModo()">
                    <i class="bi bi-moon-stars-fill me-2" id="themeIcon"></i><span id="themeText">Modo Oscuro</span>
                </button>
                <span class="badge bg-dark text-info px-3 py-2 rounded-pill border border-secondary shadow-sm fs-7">
                    <i class="bi bi-code-slash me-2"></i>Angelo Vera - 5to A
                </span>
                <span class="badge bg-white text-dark px-3 py-2 rounded-pill fw-semibold shadow-sm">v{{ version }}</span>
            </div>
        </div>
    </div>

    <div class="container">
        <div class="row g-4">
            
            <!-- COLUMNA IZQUIERDA: Estado e Infraestructura -->
            <div class="col-12 col-lg-4 d-flex flex-column gap-4">
                
                <!-- Tarjeta de Tiempo -->
                <div class="card p-4 shadow-sm">
                    <div class="d-flex align-items-center mb-3">
                        <div class="rounded-3 p-2 me-3" style="background-color: #e0e7ff; color: #4f46e5;"><i class="bi bi-clock-history fs-4"></i></div>
                        <h5 class="mb-0 fw-bold text-secondary">Monitor de Tiempo</h5>
                    </div>
                    <div class="rounded-3 p-3 text-center my-2 reloj-contenedor">
                        <h2 class="fw-bold mb-0" id="reloj-pc" style="color: #6366f1; letter-spacing: -1px;">00:00:00</h2>
                        <small class="text-muted fw-semibold" id="fecha-pc">Cargando...</small>
                    </div>
                </div>

                <!-- Tarjeta de Recursos + Switch de Pánico -->
                <div class="card p-4 shadow-sm">
                    <div class="d-flex align-items-center justify-content-between mb-3">
                        <div class="d-flex align-items-center">
                            <div id="recursos-icon-bg" class="rounded-3 p-2 me-3" style="background-color: #e0f2fe; color: #0284c7;"><i class="bi bi-cpu fs-4"></i></div>
                            <h5 class="mb-0 fw-bold text-secondary">Telemetría</h5>
                        </div>
                        <!-- NUEVO: Switch de simulación de incidentes -->
                        <div class="form-check form-switch" title="Simular colapso del sistema">
                            <input class="form-check-input" type="checkbox" id="panicSwitch" onchange="alternarPanico()">
                            <label class="form-check-label text-danger small fw-bold" for="panicSwitch"><i class="bi bi-exclamation-triangle"></i></label>
                        </div>
                    </div>
                    <div class="mb-3">
                        <div class="d-flex justify-content-between small fw-bold mb-1"><span>Carga CPU</span><span id="cpu-txt">18%</span></div>
                        <div class="progress" style="height: 8px;"><div id="cpu-bar" class="progress-bar bg-info" style="width: 18%"></div></div>
                    </div>
                    <div class="mb-3">
                        <div class="d-flex justify-content-between small fw-bold mb-1"><span>Uso Memoria RAM</span><span id="ram-txt">42%</span></div>
                        <div class="progress" style="height: 8px;"><div id="ram-bar" class="progress-bar bg-primary" style="width: 42%"></div></div>
                    </div>
                    <!-- NUEVO: Contador de Uptime -->
                    <hr class="opacity-25">
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="small text-muted fw-semibold">Tiempo Continuo sin Fallos:</span>
                        <span id="uptime-contador" class="badge bg-success-subtle text-success fw-bold p-2 fs-7">142 Días</span>
                    </div>
                </div>

                <!-- NUEVO: Herramienta de Diagnóstico de Red (Ping) -->
                <div class="card p-4 shadow-sm">
                    <div class="d-flex align-items-center mb-3">
                        <div class="rounded-3 p-2 me-3" style="background-color: #fef3c7; color: #d97706;"><i class="bi bi-hdd-network fs-4"></i></div>
                        <h5 class="mb-0 fw-bold text-secondary">Herramientas de Red</h5>
                    </div>
                    <p class="text-muted small">Verifica el estado de comunicación con un host de la red local o externa:</p>
                    <div class="input-group input-group-sm mb-2">
                        <span class="input-group-text bg-body-tertiary"><i class="bi bi-globe"></i></span>
                        <input type="text" id="pingHost" class="form-control" value="192.168.1.1" placeholder="Ej: google.com">
                        <button class="btn btn-primary" type="button" id="btnPing" onclick="ejecutarPing()">Ping</button>
                    </div>
                    <div id="pingResult" class="small fw-semibold mt-1 text-muted" style="display: none;">
                        <i class="bi bi-arrow-return-right me-1"></i> Respuesta: <span id="pingValue" class="text-success">--</span>
                    </div>
                </div>

            </div>

            <!-- COLUMNA DERECHA: Calendario e Interacciones -->
            <div class="col-12 col-lg-8">
                <div class="card p-4 shadow-sm h-100" id="calendar-card"
                     data-today-day="{{ hoy.day }}" data-today-month="{{ hoy.month }}" data-today-year="{{ hoy.year }}"
                     data-view-month="{{ mes_vista }}" data-view-year="{{ ano_vista }}">
                    
                    <div class="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-3">
                        <div class="d-flex gap-1">
                            <a href="/?year={{ prev_ano_solo }}&month={{ mes_vista }}" class="btn btn-nav btn-sm shadow-sm">« Año</a>
                            <a href="/?year={{ prev_ano }}&month={{ prev_mes }}" class="btn btn-nav btn-sm shadow-sm">‹ Mes</a>
                        </div>
                        <span class="titulo-mes">{{ nombre_mes_vista }} {{ ano_vista }}</span>
                        <div class="d-flex gap-1">
                            <a href="/?year={{ next_ano }}&month={{ next_mes }}" class="btn btn-nav btn-sm shadow-sm">Mes ›</a>
                            <a href="/?year={{ next_ano_solo }}&month={{ mes_vista }}" class="btn btn-nav btn-sm shadow-sm">Año »</a>
                        </div>
                    </div>

                    <div class="text-center mb-3">
                        <a href="/" class="btn btn-hoy btn-sm fw-bold px-4 shadow-sm"><i class="bi bi-calendar2-check me-1"></i> Ir al Mes Actual</a>
                    </div>

                    <div class="table-responsive">
                        {{ calendario_html | safe }}
                    </div>

                    <div class="mt-3 p-3 bg-body-tertiary rounded-3 border">
                        <h6 class="fw-bold mb-2 text-primary"><i class="bi bi-info-circle me-2"></i>Tareas del Día Seleccionado:</h6>
                        <ul id="lista-tareas" class="mb-0 small text-muted">
                            <li>Haz clic en cualquier día del calendario (los días con marcas naranjas indican mantenimientos programados).</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>

        <!-- Consola de Logs Inferior -->
        <div class="row mt-4">
            <div class="col-12">
                <div class="card p-4 shadow-sm">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <h5 class="fw-bold text-secondary mb-0"><i class="bi bi-terminal me-2"></i>Consola de Logs en Vivo</h5>
                        <button class="btn btn-outline-secondary btn-sm" onclick="document.getElementById('terminal').innerHTML=''"><i class="bi bi-trash3"></i> Limpiar</button>
                    </div>
                    <div class="terminal-logs" id="terminal">
                        <span class="log-info">[SYSTEM] Inicializando entorno DevOps... OK</span><br>
                        <span class="log-success">[SUCCESS] Kernel mapeado y enlazado a Flask core correctamente.</span><br>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <footer class="container text-center text-muted small my-5 py-3 border-top opacity-50">
        Infraestructura DevOps de Prácticas &bull; Angelo Vera &bull; 2026
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        let modoPanico = false;

        // 1. CONTROL DE TEMA
        const htmlElement = document.documentElement;
        const themeIcon = document.getElementById('themeIcon');
        const themeText = document.getElementById('themeText');
        const temaGuardado = localStorage.getItem('theme') || 'light';
        aplicarTema(temaGuardado);

        function cambiarModo() {
            const nuevoTema = htmlElement.getAttribute('data-bs-theme') === 'light' ? 'dark' : 'light';
            aplicarTema(nuevoTema);
            localStorage.setItem('theme', nuevoTema);
        }

        function aplicarTema(tema) {
            htmlElement.setAttribute('data-bs-theme', tema);
            if (tema === 'dark') {
                themeIcon.className = 'bi bi-sun-fill me-2'; themeText.innerText = 'Modo Claro';
            } else {
                themeIcon.className = 'bi bi-moon-stars-fill me-2'; themeText.innerText = 'Modo Oscuro';
            }
        }

        // 2. RELOJ EN VIVO
        function actualizarReloj() {
            const ahora = new Date();
            document.getElementById('reloj-pc').innerText = ahora.toLocaleTimeString('es-ES', { hour12: false });
            let fecha = ahora.toLocaleDateString('es-ES', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
            document.getElementById('fecha-pc').innerText = fecha.charAt(0).toUpperCase() + fecha.slice(1);
        }
        setInterval(actualizarReloj, 1000); actualizarReloj();

        // 3. SIMULACIÓN DE MÉTRICAS & MODO PÁNICO
        setInterval(() => {
            let cpu, ram;
            const term = document.getElementById('terminal');
            
            if (!modoPanico) {
                cpu = Math.floor(Math.random() * (45 - 12) + 12);
                ram = Math.floor(Math.random() * (60 - 35) + 35);
                
                if (Math.random() > 0.75) {
                    const mensajes = ["Sincronización NTP Exitosa", "Estructura de Red saludable", "Conexiones entrantes balanceadas", "Verificación de storage: OK"];
                    term.innerHTML += `<span class="log-info">[${new Date().toLocaleTimeString()}] [INFO] ${mensajes[Math.floor(Math.random()*mensajes.length)]}.</span><br>`;
                }
            } else {
                // Si el switch está activo, las métricas revientan
                cpu = Math.floor(Math.random() * (100 - 94) + 94);
                ram = Math.floor(Math.random() * (99 - 91) + 91);
                
                const errores = ["CRITICAL: DB Connection Timeout!", "WARNING: Memoria swap superando el 90%", "ERROR: Puerto 443 saturado - Posible ataque de denegación DDOS", "ALERT: Pérdida de paquetes en la interfaz eth0"];
                term.innerHTML += `<span class="log-error">[${new Date().toLocaleTimeString()}] [CRITICAL] ${errores[Math.floor(Math.random()*errores.length)]}.</span><br>`;
            }

            document.getElementById('cpu-txt').innerText = cpu + '%';
            document.getElementById('cpu-bar').style.width = cpu + '%';
            document.getElementById('ram-txt').innerText = ram + '%';
            document.getElementById('ram-bar').style.width = ram + '%';
            
            // Cambiar colores de barras si pasa umbrales críticos
            if(cpu > 85) { document.getElementById('cpu-bar').className = "progress-bar bg-danger"; }
            else { document.getElementById('cpu-bar').className = "progress-bar bg-info"; }
            
            if(ram > 85) { document.getElementById('ram-bar').className = "progress-bar bg-danger"; }
            else { document.getElementById('ram-bar').className = "progress-bar bg-primary"; }

            term.scrollTop = term.scrollHeight;
        }, 2500);

        function alternarPanico() {
            modoPanico = document.getElementById('panicSwitch').checked;
            const badge = document.getElementById('status-global-badge');
            const uptime = document.getElementById('uptime-contador');
            const iconBg = document.getElementById('recursos-icon-bg');
            const term = document.getElementById('terminal');

            if (modoPanico) {
                badge.className = "badge bg-danger animate-pulse";
                badge.innerText = "CRITICAL FAILURE";
                uptime.className = "badge bg-danger-subtle text-danger fw-bold p-2 fs-7";
                uptime.innerText = "0 Días (SISTEMA CAÍDO)";
                iconBg.style.backgroundColor = "#fee2e2"; iconBg.style.color = "#ef4444";
                term.innerHTML += `<span class="log-error">[${new Date().toLocaleTimeString()}] [ALERT] SWITCH DE INCIDENTE MANUAL INICIADO POR EL ADMINISTRADOR.</span><br>`;
            } else {
                badge.className = "badge bg-success";
                badge.innerText = "ONLINE";
                uptime.className = "badge bg-success-subtle text-success fw-bold p-2 fs-7";
                uptime.innerText = "142 Días";
                iconBg.style.backgroundColor = "#e0f2fe"; iconBg.style.color = "#0284c7";
                term.innerHTML += `<span class="log-success">[${new Date().toLocaleTimeString()}] [SYSTEM] Contingencia resuelta. Estabilizando servicios...</span><br>`;
            }
            term.scrollTop = term.scrollHeight;
        }

        // 4. SIMULACIÓN DE PING EN RED
        function ejecutarPing() {
            const host = document.getElementById('pingHost').value.trim();
            const btn = document.getElementById('btnPing');
            const resBox = document.getElementById('pingResult');
            const resVal = document.getElementById('pingValue');
            const term = document.getElementById('terminal');

            if(!host) return;

            btn.disabled = true;
            btn.innerHTML = `<span class="spinner-border spinner-border-sm"></span>`;
            resBox.style.display = "block";
            resVal.className = "text-warning";
            resVal.innerText = "Haciendo traza...";

            // Simular petición asíncrona de red
            setTimeout(() => {
                btn.disabled = false;
                btn.innerText = "Ping";
                
                if (modoPanico && Math.random() > 0.3) {
                    // Si el sistema está caído, el ping suele fallar
                    resVal.className = "text-danger";
                    resVal.innerText = "Tiempo de espera agotado (Request Timeout)";
                    term.innerHTML += `<span class="log-error">[${new Date().toLocaleTimeString()}] [NET] Ping fallido hacia ${host}.</span><br>`;
                } else {
                    const ms = Math.floor(Math.random() * (62 - 8) + 8);
                    resVal.className = "text-success";
                    resVal.innerText = `Exitoso en ${ms}ms (TTL=54)`;
                    term.innerHTML += `<span class="log-success">[${new Date().toLocaleTimeString()}] [NET] Respuesta de ping desde ${host}: bytes=32 tiempo=${ms}ms</span><br>`;
                }
                term.scrollTop = term.scrollHeight;
            }, 1200);
        }

        // 5. INTERACCIÓN CALENDARIO
        document.addEventListener("DOMContentLoaded", function() {
            const card = document.getElementById("calendar-card");
            const tDay = card.getAttribute("data-today-day");
            const tMonth = card.getAttribute("data-today-month");
            const tYear = card.getAttribute("data-today-year");
            const vMonth = card.getAttribute("data-view-month");
            const vYear = card.getAttribute("data-view-year");
            
            const celdas = document.querySelectorAll(".table td:not(.noday)");
            
            celdas.forEach(celda => {
                const diaNum = celda.innerText.trim();
                
                if (tMonth === vMonth && tYear === vYear && diaNum === tDay) {
                    celda.innerHTML = `<span class="text-white d-flex align-items-center justify-content-center mx-auto rounded-circle fw-bold shadow-sm" style="width: 36px; height: 36px; background: linear-gradient(135deg, #6366f1 0%, #312e81 100%);">${diaNum}</span>`;
                }

                celda.addEventListener('click', () => {
                    fetch(`/api/tareas?day=${diaNum}`)
                        .then(response => response.json())
                        .then(data => {
                            const lista = document.getElementById('lista-tareas');
                            lista.innerHTML = "";
                            if (data.tareas.length === 0) {
                                lista.innerHTML = `<li>No hay eventos registrados para el día ${diaNum}.</li>`;
                            } else {
                                data.tareas.forEach(t => {
                                    lista.innerHTML += `<li><strong class="text-warning">●</strong> ${t}</li>`;
                                });
                            }
                        });
                });
            });
        });
    </script>
</body>
</html>
"""

@app.route("/api/tareas")
def api_tareas():
    dia = request.args.get('day', type=int)
    tareas = TAREAS_DEVOPS.get(dia, [])
    return jsonify({"tareas": tareas})

@app.route("/")
def inicio():
    hoy = datetime.now()
    ano_vista = request.args.get('year', default=hoy.year, type=int)
    mes_vista = request.args.get('month', default=hoy.month, type=int)

    if mes_vista < 1 or mes_vista > 12: mes_vista = hoy.month
    if ano_vista < 1: ano_vista = hoy.year

    prev_mes = 12 if mes_vista == 1 else mes_vista - 1
    prev_ano = ano_vista - 1 if mes_vista == 1 else ano_vista
    next_mes = 1 if mes_vista == 12 else mes_vista + 1
    next_ano = ano_vista + 1 if mes_vista == 12 else ano_vista

    cal = calendar.HTMLCalendar(firstweekday=0)
    calendario_html = cal.formatmonth(ano_vista, mes_vista)
    
    calendario_html = calendario_html.replace(
        'class="month"', 
        'class="table table-borderless text-center m-0 align-middle"'
    )
    calendario_html = re.sub(r'<tr><th colspan="7".*?</th></tr>', '', calendario_html)

    for dia_con_tarea in TAREAS_DEVOPS.keys():
        calendario_html = re.sub(
            f'>({dia_con_tarea})</td>', 
            f' class="tiene-tarea">{dia_con_tarea}</td>', 
            calendario_html
        )

    return render_template_string(
        PLANTILLA_HTML, estilos_css=ESTILOS_CSS, version=VERSION, hoy=hoy,
        mes_vista=mes_vista, ano_vista=ano_vista, nombre_mes_vista=MESES_ES[mes_vista],
        prev_mes=prev_mes, prev_ano=prev_ano, next_mes=next_mes, next_ano=next_ano,
        prev_ano_solo=ano_vista-1, next_ano_solo=ano_vista+1, calendario_html=calendario_html
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)