from flask import Flask
from datetime import datetime
import calendar

app = Flask(__name__)

# Nueva versión corregida
VERSION = "1.2.1"

@app.route("/")
def inicio():
    ahora = datetime.now()
    fecha_texto = ahora.strftime("%A, %d de %B de %Y")
    hora_texto = ahora.strftime("%H:%M:%S")
    
    # Generar el calendario base del mes actual
    cal = calendar.HTMLCalendar(firstweekday=0)
    calendario_html = cal.formatmonth(ahora.year, ahora.month)
    
    # Inyectamos las clases de Bootstrap a la tabla generada
    calendario_html = calendario_html.replace(
        'class="month"', 
        'class="table table-borderless text-center m-0 align-middle"'
    )

    # Estilos CSS separados para no generar conflictos con las llaves de las f-strings
    estilos_css = """
    body {
        background-color: #f4f6f9;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .gradient-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
    }
    .card {
        border: none;
        border-radius: 15px;
        transition: transform 0.2s;
    }
    .card:hover {
        transform: translateY(-2px);
    }
    th.month {
        font-size: 1.25rem;
        font-weight: 600;
        color: #2a5298;
        padding-bottom: 15px;
        text-transform: capitalize;
    }
    .table th {
        color: #6c757d;
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
    }
    .table td {
        font-weight: 500;
        width: 45px;
        height: 45px;
    }
    .noday {
        color: #dee2e6;
    }
    """

    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dashboard Reloj y Calendario</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
        <style>
            {estilos_css}
        </style>
    </head>
    <body>

        <div class="gradient-header py-4 mb-5 shadow-sm">
            <div class="container d-flex justify-content-between align-items-center">
                <div>
                    <h1 class="h3 mb-0 fw-bold"><i class="bi bi-cpu-fill me-2"></i>DevOps Control Panel</h1>
                    <small class="opacity-75">Estado del servidor: <span class="badge bg-success">Online</span></small>
                </div>
                <div>
                    <span class="badge bg-white text-dark px-3 py-2 rounded-pill fw-semibold shadow-sm">Versión {VERSION}</span>
                </div>
            </div>
        </div>

        <div class="container">
            <div class="row g-4">
                
                <div class="col-12 col-md-6 col-lg-5">
                    <div class="card shadow-sm h-100">
                        <div class="card-body p-4 d-flex flex-column justify-content-between">
                            <div>
                                <div class="d-flex align-items-center mb-3">
                                    <div class="bg-primary-subtle text-primary rounded-3 p-2 me-3">
                                        <i class="bi bi-clock-history fs-3"></i>
                                    </div>
                                    <h5 class="card-title mb-0 fw-bold text-secondary">Tiempo del Servidor</h5>
                                </div>
                                <hr class="text-muted opacity-25">
                                <p class="text-muted small mb-1 text-uppercase fw-bold tracking-wider">Fecha Actual</p>
                                <h4 class="fw-semibold text-dark mb-4">{fecha_texto}</h4>
                            </div>
                            
                            <div class="bg-light rounded-3 p-3 text-center my-3 border border-light-subtle">
                                <p class="text-muted small mb-1 text-uppercase fw-bold">Hora Local</p>
                                <h1 class="display-4 fw-bold text-primary mb-0" style="letter-spacing: -1px;">{hora_texto}</h1>
                            </div>
                            
                            <div class="text-muted small d-flex align-items-center mt-2">
                                <i class="bi bi-info-circle me-2"></i> Refresca la página para actualizar la hora.
                            </div>
                        </div>
                    </div>
                </div>

                <div class="col-12 col-md-6 col-lg-7">
                    <div class="card shadow-sm h-100">
                        <div class="card-body p-4">
                            <div class="d-flex align-items-center mb-3">
                                <div class="bg-success-subtle text-success rounded-3 p-2 me-3">
                                    <i class="bi bi-calendar3 fs-3"></i>
                                </div>
                                <h5 class="card-title mb-0 fw-bold text-secondary">Calendario Mensual</h5>
                            </div>
                            <hr class="text-muted opacity-25">
                            
                            <div class="table-responsive">
                                {calendario_html}
                            </div>
                        </div>
                    </div>
                </div>

            </div>
        </div>

        <footer class="container text-center text-muted small my-5 py-3 border-top opacity-50">
            Desarrollado en Flask & Docker &bull; 2026
        </footer>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
        
        <script>
            document.addEventListener("DOMContentLoaded", function() {{
                const diaHoy = "{ahora.day}";
                const celdas = document.querySelectorAll(".table td:not(.noday)");
                
                celdas.forEach(celda => {{
                    if (celda.innerText.trim() === diaHoy) {{
                        celda.innerHTML = '<span class="bg-primary text-white d-flex align-items-center justify-content-center mx-auto rounded-circle fw-bold shadow-sm" style="width: 38px; height: 38px;">' + diaHoy + '</span>';
                    }}
                }});
            }});
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)