from flask import Flask, request
from datetime import datetime
import calendar

app = Flask(__name__)

# Versión 1.4.1 - Limpieza de sangrías invisibles y f-strings
VERSION = "1.4.1"

@app.route("/")
def inicio():
    # 1. Obtener la fecha para el calendario
    hoy = datetime.now()

    # 2. Capturar el año y mes que el usuario quiere ver desde la URL
    ano_vista = request.args.get('year', default=hoy.year, type=int)
    mes_vista = request.args.get('month', default=hoy.month, type=int)

    if mes_vista < 1 or mes_vista > 12:
        mes_vista = hoy.month

    # 3. Lógica de navegación de meses
    if mes_vista == 1:
        prev_mes = 12
        prev_ano = ano_vista - 1
    else:
        prev_mes = mes_vista - 1
        prev_ano = ano_vista

    if mes_vista == 12:
        next_mes = 1
        next_ano = ano_vista + 1
    else:
        next_mes = mes_vista + 1
        next_ano = ano_vista

    prev_ano_solo = ano_vista - 1
    next_ano_solo = ano_vista + 1

    # 4. Generar la tabla HTML del calendario
    cal = calendar.HTMLCalendar(firstweekday=0)
    calendario_html = cal.formatmonth(ano_vista, mes_vista)
    
    # Inyectar clases de Bootstrap a la tabla
    calendario_html = calendario_html.replace(
        'class="month"', 
        'class="table table-borderless text-center m-0 align-middle"'
    )

    # 5. Paleta de colores Premium
    estilos_css = """
    body {
        background-color: #f1f5f9;
        font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    }
    .gradient-header {
        background: linear-gradient(135deg, #312e81 0%, #1e1b4b 100%);
        color: white;
    }
    .card {
        border: none;
        border-radius: 16px;
        background-color: #ffffff;
    }
    .btn-nav {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        color: #475569;
        transition: all 0.2s;
    }
    .btn-nav:hover {
        background-color: #6366f1;
        color: white;
        border-color: #6366f1;
    }
    .btn-hoy {
        background-color: #ecfdf5;
        color: #059669;
        border: 1px solid #a7f3d0;
    }
    .btn-hoy:hover {
        background-color: #059669;
        color: white;
    }
    th.month {
        font-size: 1.4rem;
        font-weight: 700;
        color: #312e81;
        padding-bottom: 20px;
        text-transform: capitalize;
    }
    .table th {
        color: #94a3b8;
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .table td {
        font-weight: 600;
        color: #334155;
        width: 45px;
        height: 45px;
    }
    .noday {
        color: #cbd5e1 !important;
    }
    .credito-badge {
        background: linear-gradient(135deg, #0f172a 0%, #334155 100%);
        color: #38bdf8;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    """

    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Control Panel - Angelo Vera</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
        <style>
            {estilos_css}
        </style>
    </head>
    <body>

        <div class="gradient-header py-4 mb-5 shadow-sm">
            <div class="container d-flex flex-column flex-sm-row justify-content-between align-items-center gap-3">
                <div>
                    <h1 class="h3 mb-0 fw-bold"><i class="bi bi-terminal-box me-2 text-info"></i>DevOps Dashboard</h1>
                    <small class="opacity-75">Estado de la infraestructura: <span class="badge bg-success">Online</span></small>
                </div>
                <div class="d-flex align-items-center gap-2">
                    <span class="badge credito-badge px-3 py-2 rounded-pill shadow-sm fs-7 border border-secondary">
                        <i class="bi bi-code-slash me-2 text-info"></i>Desarrollado por Angelo Vera - 5to A
                    </span>
                    <span class="badge bg-white text-dark px-3 py-2 rounded-pill fw-semibold shadow-sm">v{VERSION}</span>
                </div>
            </div>
        </div>

        <div class="container">
            <div class="row g-4">
                
                <div class="col-12 col-lg-5">
                    <div class="card shadow-sm h-100 p-4 d-flex flex-column justify-content-between">
                        <div>
                            <div class="d-flex align-items-center mb-3">
                                <div class="bg-indigo-subtle text-indigo rounded-3 p-2 me-3" style="background-color: #e0e7ff; color: #4f46e5;">
                                    <i class="bi bi-clock-history fs-3"></i>
                                </div>
                                <h5 class="card-title mb-0 fw-bold text-secondary">Tiempo del Navegador</h5>
                            </div>
                            <hr class="opacity-25">
                            <p class="text-muted small mb-1 text-uppercase fw-bold">Fecha de tu Ordenador</p>
                            <h4 class="fw-semibold text-dark mb-4" id="fecha-pc">Cargando fecha...</h4>
                        </div>
                        
                        <div class="rounded-3 p-4 text-center my-3" style="background-color: #f8fafc; border: 1px solid #f1f5f9;">
                            <p class="text-muted small mb-1 text-uppercase fw-bold">Hora en Vivo</p>
                            <h1 class="display-3 fw-bold mb-0" id="reloj-pc" style="color: #4f46e5; letter-spacing: -2px;">00:00:00</h1>
                        </div>
                        
                        <div class="text-muted small d-flex align-items-center mt-2">
                            <i class="bi bi-cpu me-2 text-success"></i> Sincronizado dinámicamente con tu sistema operativo.
                        </div>
                    </div>
                </div>

                <div class="col-12 col-lg-7">
                    <div class="card shadow-sm h-100 p-4" 
                         id="calendar-card"
                         data-today-day="{hoy.day}"
                         data-today-month="{hoy.month}"
                         data-today-year="{hoy.year}"
                         data-view-month="{mes_vista}"
                         data-view-year="{ano_vista}">
                        
                        <div class="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-4">
                            <div class="d-flex gap-1">
                                <a href="/?year={prev_ano_solo}&month={mes_vista}" class="btn btn-nav btn-sm shadow-sm" title="Año Anterior"><i class="bi bi-chevron-double-left"></i> Año</a>
                                <a href="/?year={prev_ano}&month={prev_mes}" class="btn btn-nav btn-sm shadow-sm" title="Mes Anterior"><i class="bi bi-chevron-left"></i> Mes</a>
                            </div>
                            
                            <a href="/" class="btn btn-hoy btn-sm fw-bold px-3 shadow-sm"><i class="bi bi-calendar2-check me-1"></i> Ir a Hoy</a>
                            
                            <div class="d-flex gap-1">
                                <a href="/?year={next_ano}&month={next_mes}" class="btn btn-nav btn-sm shadow-sm" title="Mes Siguiente">Mes <i class="bi bi-chevron-right"></i></a>
                                <a href="/?year={next_ano_solo}&month={mes_vista}" class="btn btn-nav btn-sm shadow-sm" title="Año Siguiente">Año <i class="bi bi-chevron-double-right"></i></a>
                            </div>
                        </div>

                        <hr class="opacity-10 m-0 mb-3">
                        
                        <div class="table-responsive">
                            {calendario_html}
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
            // 1. FUNCIÓN PARA EL RELOJ Y FECHA EN TIEMPO REAL (DE TU ORDENADOR)
            function actualizarReloj() {{
                const ahora = new Date();
                
                // Formatear la hora local de la PC (HH:MM:SS)
                const opcionesHora = {{ hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }};
                document.getElementById('reloj-pc').innerText = ahora.toLocaleTimeString('es-ES', opcionesHora);
                
                // Formatear la fecha larga de la PC
                const opcionesFecha = {{ weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }};
                let fechaFormateada = ahora.toLocaleDateString('es-ES', opcionesFecha);
                // Primera letra en mayúscula
                fechaFormateada = fechaFormateada.charAt(0).toUpperCase() + fechaFormateada.slice(1);
                document.getElementById('fecha-pc').innerText = fechaFormateada;
            }}

            // Ejecutar el reloj inmediatamente y configurarlo para actualizarse cada 1 segundo (1000ms)
            actualizarReloj();
            setInterval(actualizarReloj, 1000);

            // 2. LOGICA PARA RESALTAR EL DÍA ACTUAL EN EL CALENDARIO
            document.addEventListener("DOMContentLoaded", function() {{
                const card = document.getElementById("calendar-card");
                const tDay = card.getAttribute("data-today-day");
                const tMonth = card.getAttribute("data-today-month");
                const tYear = card.getAttribute("data-today-year");
                const vMonth = card.getAttribute("data-view-month");
                const vYear = card.getAttribute("data-view-year");
                
                if (tMonth === vMonth && tYear === vYear) {{
                    const celdas = document.querySelectorAll(".table td:not(.noday)");
                    celdas.forEach(celda => {{
                        if (celda.innerText.trim() === tDay) {{
                            celda.innerHTML = '<span class="text-white d-flex align-items-center justify-content-center mx-auto rounded-circle fw-bold shadow-sm" style="width: 38px; height: 38px; background: linear-gradient(135deg, #4f46e5 0%, #312e81 100%);">' + tDay + '</span>';
                        }}
                    }});
                }}
            }});
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)