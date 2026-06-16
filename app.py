from flask import Flask, request, render_template_string, jsonify
from datetime import datetime
import calendar
import random
import re

app = Flask(__name__)

VERSION = "2.1.0"

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
.table td:not(.nonday):hover { background-color: var(--bs-secondary-bg-subtle); }
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
.log-alert { color: #fbbf24; font-weight: bold; }
.log-deploy { color: #a855f7; }
.log-training { color: #22d3ee; }

@keyframes blinker { 50% { opacity: 0.5; } }

.btn-theme-toggle {
    background: rgba(255, 255, 255, 0.15); border: none; color: white;
    padding: 8px 12px; border-radius: 50rem; font-weight: 500; transition: all 0.2s;
}
.btn-theme-toggle:hover { background: rgba(255, 255, 255, 0.3); }

.reloj-contenedor { background-color: var(--bs-light-bg-subtle); border: 1px solid var(--bs-border-color-translucent); }

.pulse-danger {
    animation: pulse-bg 1s infinite alternate;
}
@keyframes pulse-bg {
    0% { background-color: rgba(239, 68, 68, 0.1); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
    100% { background-color: rgba(239, 68, 68, 0.25); box-shadow: 0 0 10px 4px rgba(239, 68, 68, 0.2); }
}

.video-responsive {
    position: relative;
    padding-bottom: 56.25%;
    height: 0;
    overflow: hidden;
    border-radius: 12px;
}
.video-responsive iframe {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    border: none;
}
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
            
            <div class="col-12 col-lg-4 d-flex flex-column gap-4">
                
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

                <div class="card p-4 shadow-sm" id="recursos-card">
                    <div class="d-flex align-items-center justify-content-between mb-3">
                        <div class="d-flex align-items-center">
                            <div id="recursos-icon-bg" class="rounded-3 p-2 me-3" style="background-color: #e0f2fe; color: #0284c7;"><i class="bi bi-cpu fs-4"></i></div>
                            <h5 class="mb-0 fw-bold text-secondary">Telemetría</h5>
                        </div>
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
                    <hr class="opacity-25">
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="small text-muted fw-semibold">Tiempo Continuo sin Fallos:</span>
                        <span id="uptime-contador" class="badge bg-success-subtle text-success fw-bold p-2 fs-7">142 Días</span>
                    </div>
                </div>

                <div class="card p-4 shadow-sm" id="alarm-card">
                    <div class="d-flex align-items-center justify-content-between mb-3">
                        <div class="d-flex align-items-center">
                            <div id="alarm-icon-bg" class="rounded-3 p-2 me-3" style="background-color: #fee2e2; color: #dc2626;"><i class="bi bi-bell fs-4"></i></div>
                            <h5 class="mb-0 fw-bold text-secondary">Umbral de Alarma</h5>
                        </div>
                        <span id="alarm-status-badge" class="badge bg-secondary">Inactiva</span>
                    </div>
                    
                    <label for="cpuThreshold" class="form-label small fw-bold text-muted">Disparar alarma si la CPU supera el:</label>
                    <div class="d-flex align-items-center gap-3 mb-3">
                        <input type="range" class="form-range" id="cpuThreshold" min="50" max="95" value="80" oninput="actualizarThresholdTexto(this.value)">
                        <span id="threshold-val" class="fw-bold text-primary fs-5" style="min-width: 45px;">80%</span>
                    </div>

                    <div class="form-check form-check-inline small">
                        <input class="form-check-input" type="checkbox" id="muteSound" checked>
                        <label class="form-check-label text-muted" for="muteSound"><i class="bi bi-volume-mute"></i> Silenciar pitido sonoro</label>
                    </div>
                </div>

            </div>

            <div class="col-12 col-lg-8 d-flex flex-column gap-4">
                
                <div class="card p-4 shadow-sm" id="calendar-card"
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

                <div class="card p-4 shadow-sm">
                    <div class="d-flex flex-column flex-sm-row justify-content-between align-items-start align-items-sm-center gap-2 mb-3">
                        <div class="d-flex align-items-center">
                            <div class="rounded-3 p-2 me-3" style="background-color: #f3e8ff; color: #a855f7;"><i class="bi bi-rocket-takeoff fs-4"></i></div>
                            <div>
                                <h5 class="mb-0 fw-bold text-secondary">Pipeline de Integración Continua (CI/CD)</h5>
                                <small class="text-muted">Rama activa: <code class="text-purple">main</code></small>
                            </div>
                        </div>
                        <button class="btn btn-purple text-white fw-bold px-3 shadow-sm" style="background-color: #a855f7;" id="btnDeploy" onclick="iniciarDespliegue()">
                            <i class="bi bi-play-fill me-1"></i> Deploy Code
                        </button>
                    </div>

                    <div id="deploy-process-box" class="p-3 bg-body-tertiary rounded-3 border" style="display:none;">
                        <div class="d-flex justify-content-between small fw-bold mb-2">
                            <span id="deploy-step-text" class="text-purple">Preparando...</span>
                            <span id="deploy-pct-text">0%</span>
                        </div>
                        <div class="progress" style="height: 10px;">
                            <div id="deploy-progress-bar" class="progress-bar progress-bar-striped progress-bar-animated bg-purple" style="width: 0%; background-color: #a855f7;"></div>
                        </div>
                    </div>
                </div>

                <div class="card p-4 shadow-sm">
                    <div class="d-flex align-items-center mb-3">
                        <div class="rounded-3 p-2 me-3" style="background-color: #ffe4e6; color: #f43f5e;"><i class="bi bi-youtube fs-4"></i></div>
                        <div>
                            <h5 class="mb-0 fw-bold text-secondary">Centro de Capacitación & Cultura</h5>
                            <small class="text-muted">Recursos multimedia y muestras de producción nacional ecuatoriana</small>
                        </div>
                    </div>
                    
                    <div class="d-flex flex-wrap gap-2 mb-3">
                        <button class="btn btn-outline-danger btn-sm active fw-semibold" id="btn-vid1" onclick="cambiarVideo('Aztra - El Mañana', 'Muestra artística del emblemático tema musical \\'El Mañana\\' interpretado por la icónica banda de rock/metal nacional Aztra.', '🎸 Rock/Metal EC', 'https://www.youtube.com/embed/PhkfHrljRiQ', 'btn-vid1')">
                            <i class="bi bi-music-note-beamed me-1"></i> Aztra - El Mañana
                        </button>
                        <button class="btn btn-outline-danger btn-sm fw-semibold" id="btn-vid2" onclick="cambiarVideo('🐳 Tecnologías de Contenedores', '📦 Explicación práctica de Docker y arquitectura aislada.', '🐳 ¿Qué es Docker?', 'https://www.youtube.com/embed/4Dko5W96tRE', 'btn-vid2')">
                            <i class="bi bi-box-seam me-1"></i> Módulo 2: Docker
                        </button>
                        <button class="btn btn-outline-danger btn-sm fw-semibold" id="btn-vid3" onclick="cambiarVideo('♾️ Cultura & Flujo DevOps', '🔄 Comprendiendo la integración continua y despliegue automatizado.', '♾️ Introducción DevOps', 'https://www.youtube.com/embed/V6HwYv736as', 'btn-vid3')">
                            <i class="bi bi-infinity me-1"></i> Módulo 3: DevOps
                        </button>
                    </div>

                    <div class="row g-3">
                        <div class="col-12 col-md-7">
                            <div class="video-responsive border shadow-sm">
                                <iframe id="yt-player" src="https://www.youtube.com/embed/PhkfHrljRiQ" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
                            </div>
                        </div>
                        <div class="col-12 col-md-5 d-flex flex-column justify-content-center p-3 bg-body-tertiary rounded-3 border">
                            <span class="badge bg-danger-subtle text-danger align-self-start mb-2" id="vid-tag">🎸 Rock/Metal EC</span>
                            <h6 class="fw-bold mb-1 text-body" id="vid-title">Aztra - El Mañana</h6>
                            <p class="text-muted small mb-0" id="vid-desc">Muestra artística del emblemático tema musical 'El Mañana' interpretado por la icónica banda de rock/metal nacional Aztra.</p>
                        </div>
                    </div>
                </div>

                <div class="card p-4 shadow-sm">
                    <div class="d-flex align-items-center mb-3">
                        <div class="rounded-3 p-2 me-3" style="background-color: #fef3c7; color: #d97706;"><i class="bi bi-hdd-network fs-4"></i></div>
                        <h5 class="mb-0 fw-bold text-secondary">Herramientas de Red</h5>
                    </div>
                    <div class="row g-2 align-items-center">
                        <div class="col-12 col-sm-8">
                            <div class="input-group input-group-sm">
                                <span class="input-group-text bg-body-tertiary"><i class="bi bi-globe"></i></span>
                                <input type="text" id="pingHost" class="form-control" value="192.168.1.1">
                                <button class="btn btn-primary" type="button" id="btnPing" onclick="ejecutarPing()">Ping</button>
                            </div>
                        </div>
                        <div class="col-12 col-sm-4">
                            <div id="pingResult" class="small fw-semibold text-muted ps-2" style="display: none;">
                                Rsp: <span id="pingValue" class="text-success">--</span>
                            </div>
                        </div>
                    </div>
                </div>

            </div>
        </div>

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
        let alarmThreshold = 80;
        let audioCtx = null;

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

        function actualizarReloj() {
            const ahora = new Date();
            document.getElementById('reloj-pc').innerText = SecurityEscape(ahora.toLocaleTimeString('es-ES', { hour12: false }));
            let fecha = ahora.toLocaleDateString('es-ES', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
            document.getElementById('fecha-pc').innerText = fecha.charAt(0).toUpperCase() + fecha.slice(1);
        }
        function SecurityEscape(str) { return str.replace(/</g, "&lt;").replace(/>/g, "&gt;"); }
        setInterval(actualizarReloj, 1000); actualizarReloj();

        function playBeep() {
            if (document.getElementById('muteSound').checked) return;
            try {
                if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                let osc = audioCtx.createOscillator();
                let gain = audioCtx.createGain();
                osc.type = 'sine';
                osc.frequency.setValueAtTime(880, audioCtx.currentTime);
                gain.gain.setValueAtTime(0.1, audioCtx.currentTime);
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                osc.start();
                osc.stop(audioCtx.currentTime + 0.15);
            } catch(e) {}
        }

        function actualizarThresholdTexto(valor) {
            alarmThreshold = parseInt(valor);
            document.getElementById('threshold-val').innerText = valor + '%';
        }

        function cambiarVideo(titulo, descripcion, tag, url, btnId) {
            document.getElementById('yt-player').src = url;
            document.getElementById('vid-title').innerText = titulo;
            document.getElementById('vid-desc').innerText = descripcion;
            document.getElementById('vid-tag').innerText = tag;
            
            document.getElementById('btn-vid1').classList.remove('active');
            document.getElementById('btn-vid2').classList.remove('active');
            document.getElementById('btn-vid3').classList.remove('active');
            document.getElementById(btnId).classList.add('active');

            const term = document.getElementById('terminal');
            term.innerHTML += `<span class="log-training">[${new Date().toLocaleTimeString()}] [TRAINING] Cargando contenido multimedia: ${SecurityEscape(titulo)}... OK</span><br>`;
            term.scrollTop = term.scrollHeight;
        }

        setInterval(() => {
            let cpu, ram;
            const term = document.getElementById('terminal');
            
            if (!modoPanico) {
                cpu = Math.floor(Math.random() * (45 - 12) + 12);
                ram = Math.floor(Math.random() * (60 - 35) + 35);
                if (Math.random() > 0.82) {
                    const mensajes = ["Sincronización NTP Exitosa", "Estructura de Red saludable", "Conexiones balanceadas"];
                    term.innerHTML += `<span class="log-info">[${new Date().toLocaleTimeString()}] [INFO] ${mensajes[Math.floor(Math.random()*mensajes.length)]}.</span><br>`;
                }
            } else {
                cpu = Math.floor(Math.random() * (100 - 94) + 94);
                ram = Math.floor(Math.random() * (99 - 91) + 91);
                const errores = ["CRITICAL: DB Connection Timeout!", "ERROR: Puerto 443 saturado - DDOS detectado"];
                term.innerHTML += `<span class="log-error">[${new Date().toLocaleTimeString()}] [CRITICAL] ${errores[Math.floor(Math.random()*errores.length)]}.</span><br>`;
            }

            document.getElementById('cpu-txt').innerText = cpu + '%';
            document.getElementById('cpu-bar').style.width = cpu + '%';
            document.getElementById('ram-txt').innerText = ram + '%';
            document.getElementById('ram-bar').style.width = ram + '%';
            
            if(cpu > 85) { document.getElementById('cpu-bar').className = "progress-bar bg-danger"; }
            else { document.getElementById('cpu-bar').className = "progress-bar bg-info"; }

            const alarmCard = document.getElementById('alarm-card');
            const alarmBadge = document.getElementById('alarm-status-badge');
            if (cpu >= alarmThreshold) {
                alarmCard.classList.add('pulse-danger');
                alarmBadge.className = "badge bg-danger animate-pulse";
                alarmBadge.innerText = "¡DISPARADA!";
                playBeep();
            } else {
                alarmCard.classList.remove('pulse-danger');
                alarmBadge.className = "badge bg-secondary";
                alarmBadge.innerText = "Inactiva";
            }
            term.scrollTop = term.scrollHeight;
        }, 2500);

        function alternarPanico() {
            modoPanico = document.getElementById('panicSwitch').checked;
            const badge = document.getElementById('status-global-badge');
            const uptime = document.getElementById('uptime-contador');
            const iconBg = document.getElementById('recursos-icon-bg');

            if (modoPanico) {
                badge.className = "badge bg-danger animate-pulse"; badge.innerText = "CRITICAL FAILURE";
                uptime.className = "badge bg-danger-subtle text-danger fw-bold p-2 fs-7"; uptime.innerText = "0 Días (CAÍDO)";
                iconBg.style.backgroundColor = "#fee2e2"; iconBg.style.color = "#ef4444";
            } else {
                badge.className = "badge bg-success"; badge.innerText = "ONLINE";
                uptime.className = "badge bg-success-subtle text-success fw-bold p-2 fs-7"; uptime.innerText = "142 Días";
                iconBg.style.backgroundColor = "#e0f2fe"; iconBg.style.color = "#0284c7";
            }
        }

        function iniciarDespliegue() {
            const btn = document.getElementById('btnDeploy');
            const box = document.getElementById('deploy-process-box');
            const bar = document.getElementById('deploy-progress-bar');
            const stepTxt = document.getElementById('deploy-step-text');
            const pctTxt = document.getElementById('deploy-pct-text');
            const term = document.getElementById('terminal');

            if (modoPanico) {
                term.innerHTML += `<span class="log-error">[${new Date().toLocaleTimeString()}] [DEPLOY] [ERROR] Despliegue cancelado automáticamente. En el servidor actual se reportan fallas críticas.</span><br>`;
                term.scrollTop = term.scrollHeight;
                alert("¡Error en el Pipeline! No se puede actualizar el sistema mientras el servidor esté caído.");
                return;
            }

            btn.disabled = true;
            box.style.display = "block";
            let progreso = 0;
            
            term.innerHTML += `<span class="log-deploy">[${new Date().toLocaleTimeString()}] [CI/CD] Triggering new production deployment (commit #A7X92)...</span><br>`;

            let intervalo = setInterval(() => {
                progreso += 5;
                bar.style.width = progreso + "%";
                pctTxt.innerText = progreso + "%";

                if (progreso < 35) {
                    stepTxt.innerText = "🔨 Stage 1: Compilando paquetes de código...";
                    if(progreso === 5) term.innerHTML += `<span class="log-info">[${new Date().toLocaleTimeString()}] [CI/CD] Building project dependencies via Webpack...</span><br>`;
                } else if (progreso < 75) {
                    stepTxt.className = "text-warning";
                    bar.className = "progress-bar progress-bar-striped progress-bar-animated bg-warning";
                    stepTxt.innerText = "🧪 Stage 2: Ejecutando pruebas unitarias...";
                    if(progreso === 35) term.innerHTML += `<span class="log-alert">[${new Date().toLocaleTimeString()}] [CI/CD] Launching core unit tests with Jest...</span><br>`;
                } else if (progreso < 100) {
                    stepTxt.className = "text-info";
                    bar.className = "progress-bar progress-bar-striped progress-bar-animated bg-info";
                    stepTxt.innerText = "📦 Stage 3: Distribuyendo contenedores Docker...";
                    if(progreso === 75) term.innerHTML += `<span class="log-info">[${new Date().toLocaleTimeString()}] [CI/CD] Pushing new production images to local registry...</span><br>`;
                } else {
                    clearInterval(intervalo);
                    stepTxt.className = "text-success";
                    bar.className = "progress-bar bg-success";
                    stepTxt.innerHTML = "✅ ¡Despliegue Exitoso! Producción v2.1.0 online.";
                    term.innerHTML += `<span class="log-success">[${new Date().toLocaleTimeString()}] [SUCCESS] Deployment finished successfully! All checks passed.</span><br>`;
                    
                    setTimeout(() => {
                        btn.disabled = false;
                        box.style.display = "none";
                        bar.style.width = "0%";
                    }, 4000);
                }
                term.scrollTop = term.scrollHeight;
            }, 250);
        }

        function ejecutarPing() {
            const host = document.getElementById('pingHost').value.trim();
            const btn = document.getElementById('btnPing');
            const resBox = document.getElementById('pingResult');
            const resVal = document.getElementById('pingValue');
            const term = document.getElementById('terminal');

            if(!host) return;
            btn.disabled = true;
            resBox.style.display = "block";
            resVal.className = "text-warning"; resVal.innerText = "Trazando...";

            setTimeout(() => {
                btn.disabled = false;
                if (modoPanico && Math.random() > 0.3) {
                    resVal.className = "text-danger"; resVal.innerText = "Timeout";
                    term.innerHTML += `<span class="log-error">[${new Date().toLocaleTimeString()}] [NET] Ping timeout para ${SecurityEscape(host)}.</span><br>`;
                } else {
                    const ms = Math.floor(Math.random() * (45 - 5) + 5);
                    resVal.className = "text-success"; resVal.innerText = `${ms}ms`;
                    term.innerHTML += `<span class="log-success">[${new Date().toLocaleTimeString()}] [NET] Respuesta desde ${SecurityEscape(host)}: tiempo=${ms}ms.</span><br>`;
                }
                term.scrollTop = term.scrollHeight;
            }, 1200);
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    hoy = datetime.now()
    ano_actual = hoy.year
    mes_actual = hoy.month
    
    ano_vista = request.args.get('year', default=ano_actual, type=int)
    mes_vista = request.args.get('month', default=mes_actual, type=int)
    
    if mes_vista < 1:
        mes_vista = 12
        ano_vista -= 1
    elif mes_vista > 12:
        mes_vista = 1
        ano_vista += 1
        
    nombre_mes_vista = MESES_ES.get(mes_vista, "Mes")
    
    prev_mes = mes_vista - 1
    prev_ano = ano_vista
    if prev_mes < 1:
        prev_mes = 12
        prev_ano -= 1
        
    next_mes = mes_vista + 1
    next_ano = ano_vista
    if next_mes > 12:
        next_mes = 1
        next_ano += 1

    prev_ano_solo = ano_vista - 1
    next_ano_solo = ano_vista + 1

    # Generación estructurada del Calendario HTML nativo compatible con Bootstrap
    cal = calendar.Calendar(firstweekday=0) # Lunes primer día
    semanas = cal.monthdayscalendar(ano_vista, mes_vista)
    
    tabla_html = '<table class="table table-bordered text-center align-middle mb-0">'
    tabla_html += '<thead><tr><th>Lun</th><th>Mar</th><th>Mié</th><th>Jue</th><th>Vie</th><th>Sáb</th><th>Dom</th></tr></thead>'
    tabla_html += '<tbody>'
    
    for semana in semanas:
        tabla_html += '<tr>'
        for dia in semana:
            if dia == 0:
                tabla_html += '<td class="noday text-muted opacity-25">-</td>'
            else:
                clases = []
                # Validar si el día coincide exactamente con "hoy"
                if dia == hoy.day and mes_vista == hoy.month and ano_vista == hoy.year:
                    clases.append("bg-info-subtle border border-info border-2 text-info-emphasis rounded-3")
                
                # Validar si tiene tareas asignadas
                if dia in TAREAS_DEVOPS:
                    clases.append("tiene-tarea fw-bold")
                
                clase_str = " ".join(clases) if clases else ""
                tabla_html += f'<td class="{clase_str}" onclick="verTareas({dia})">{dia}</td>'
        tabla_html += '</tr>'
    tabla_html += '</tbody></table>'

    # Se usa el prefijo 'r' para indicarle a Python que es un string crudo (Raw String)
    # Evitando así el SyntaxWarning causado por '\${dia}' y '\${t}' de JavaScript.
    script_calendario = r"""
    <script>
    const tareasLocales = %s;
    function verTareas(dia) {
        const lista = document.getElementById('lista-tareas');
        lista.innerHTML = "";
        
        document.querySelectorAll('.table td.bg-primary-subtle').forEach(el => el.classList.remove('bg-primary-subtle'));
        
        const celdas = document.querySelectorAll('.table td');
        for(let celda of celdas) {
            if(!celda.classList.contains('noday') && parseInt(celda.innerText) === dia) {
                celda.classList.add('bg-primary-subtle');
                break;
            }
        }
        
        if (tareasLocales[dia]) {
            let htmlContent = "";
            tareasLocales[dia].forEach(t => {
                htmlContent += `<li class="mb-1 text-start fw-semibold text-body"><i class="bi bi-patch-check-fill text-warning me-2"></i>\${t}</li>`;
            });
            lista.innerHTML = htmlContent;
        } else {
            lista.innerHTML = `<li class="text-muted text-start"><i class="bi bi-calendar-x me-2"></i>No hay tareas críticas programadas para el día \${dia}.</li>`;
        }
    }
    </script>
    """ % str(TAREAS_DEVOPS)

    plantilla_final = PLANTILLA_HTML.replace("</body>", f"{script_calendario}</body>")

    return render_template_string(
        plantilla_final,
        estilos_css=ESTILOS_CSS,
        version=VERSION,
        hoy=hoy,
        calendario_html=tabla_html,
        mes_vista=mes_vista,
        ano_vista=ano_vista,
        nombre_mes_vista=nombre_mes_vista,
        prev_mes=prev_mes,
        prev_ano=prev_ano,
        next_mes=next_mes,
        next_ano=next_ano,
        prev_ano_solo=prev_ano_solo,
        next_ano_solo=next_ano_solo
    )

if __name__ == '__main__':
    # host='0.0.0.0' expone la aplicación hacia la red del contenedor Docker de forma correcta
    app.run(host='0.0.0.0', port=5000, debug=True)