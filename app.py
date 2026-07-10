from flask import Flask, request, render_template_string, jsonify
import random
import re

app = Flask(__name__)

VERSION = "3.0.0"
APP_NAME = "Angel & Troy"

PRODUCTS = [
    {
        "name": "Laptop Aurora 14",
        "price": "$899",
        "description": "Intel i7, 16GB RAM, SSD 512GB",
        "badge": "Más vendido"
    },
    {
        "name": "Smartwatch Pulse X",
        "price": "$179",
        "description": "Monitoreo avanzado, GPS y resistencia al agua",
        "badge": "Oferta"
    },
    {
        "name": "Auriculares Studio Pro",
        "price": "$129",
        "description": "Audio 3D y cancelación de ruido",
        "badge": "Nuevos"
    },
]

STORE_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ app_name }} | Tienda de Electrónicos</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #07111f; color: #f8fafc; }
        .hero { background: linear-gradient(135deg, #0f172a, #111827 45%, #2563eb); }
        .card { border: 1px solid rgba(255,255,255,0.12); background: rgba(15,23,42,0.8); }
        .badge-custom { background: #38bdf8; color: #082f49; }
    </style>
</head>
<body>
    <header class="hero py-5">
        <div class="container py-5">
            <div class="row align-items-center g-4">
                <div class="col-lg-7">
                    <p class="text-info fw-semibold mb-3">Tienda oficial {{ app_name }}</p>
                    <h1 class="display-5 fw-bold mb-3">Tecnología premium para tu día a día</h1>
                    <p class="lead text-light opacity-75">Laptops, smartwatches, audio y accesorios con entrega rápida desde el servidor 144.91.95.161.</p>
                    <a href="#productos" class="btn btn-primary btn-lg mt-3">Explorar productos</a>
                </div>
                <div class="col-lg-5">
                    <div class="card rounded-4 p-4 shadow-lg">
                        <h4 class="fw-bold mb-3">Envíos en 24 horas</h4>
                        <ul class="mb-0">
                            <li>Garantía de 12 meses</li>
                            <li>Pago seguro</li>
                            <li>Soporte técnico especializado</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </header>

    <main class="container py-5">
        <section id="productos" class="mb-5">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <div>
                    <h2 class="fw-bold">Productos destacados</h2>
                    <p class="text-muted mb-0">Lo más buscado este mes.</p>
                </div>
                <span class="badge badge-custom px-3 py-2">v{{ version }}</span>
            </div>
            <div class="row g-4">
                {% for product in products %}
                <div class="col-md-4">
                    <div class="card h-100 rounded-4 p-4">
                        <span class="badge badge-custom mb-3">{{ product.badge }}</span>
                        <h5 class="fw-bold">{{ product.name }}</h5>
                        <p class="text-muted">{{ product.description }}</p>
                        <div class="mt-auto d-flex justify-content-between align-items-center">
                            <strong class="text-info">{{ product.price }}</strong>
                            <button class="btn btn-outline-light btn-sm">Comprar</button>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </section>

        <section class="row g-4">
            <div class="col-md-6">
                <div class="card rounded-4 p-4">
                    <h4 class="fw-bold">Atención personalizada</h4>
                    <p class="text-muted">Nuestro equipo te ayuda a elegir el mejor equipo según tus necesidades y presupuesto.</p>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card rounded-4 p-4">
                    <h4 class="fw-bold">Servicio confiable</h4>
                    <p class="text-muted">Catálogo actualizado y soporte para instalación, mantenimiento y asesoría técnica.</p>
                </div>
            </div>
        </section>
    </main>
</body>
</html>
"""

DB_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Base de Datos | {{ app_name }}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>body{font-family:'Segoe UI',sans-serif;background:#020617;color:#f8fafc;}.card{background:#0f172a;border:1px solid #334155;}</style>
</head>
<body>
    <div class="container py-5">
        <div class="card rounded-4 p-4 p-md-5 shadow-lg">
            <p class="text-info fw-semibold mb-3">Panel de Base de Datos</p>
            <h1 class="display-6 fw-bold mb-3">pgangeltroy.byronrm.com</h1>
            <p class="text-muted">Gestión de inventario, stock y datos de productos para la tienda electrónica.</p>
            <div class="row g-3 mt-3">
                <div class="col-md-6">
                    <div class="card p-3"><h5 class="fw-bold">Estado</h5><p class="mb-0 text-success">Conectado</p></div>
                </div>
                <div class="col-md-6">
                    <div class="card p-3"><h5 class="fw-bold">Servidor</h5><p class="mb-0 text-info">144.91.95.161</p></div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

PORTAINER_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Portainer | {{ app_name }}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>body{font-family:'Segoe UI',sans-serif;background:#111827;color:#f9fafb;}.card{background:#1f2937;border:1px solid #374151;}</style>
</head>
<body>
    <div class="container py-5">
        <div class="card rounded-4 p-4 p-md-5 shadow-lg">
            <p class="text-info fw-semibold mb-3">Panel de administración</p>
            <h1 class="display-6 fw-bold mb-3">portainerat.byronrm.com</h1>
            <p class="text-muted">Gestión de contenedores, despliegues y servicios del proyecto Angel & Troy.</p>
            <div class="row g-3 mt-3">
                <div class="col-md-6">
                    <div class="card p-3"><h5 class="fw-bold">Servidor</h5><p class="mb-0 text-info">144.91.95.161</p></div>
                </div>
                <div class="col-md-6">
                    <div class="card p-3"><h5 class="fw-bold">Estado</h5><p class="mb-0 text-success">Listo para administrar</p></div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""


@app.route('/')
def index():
    host_name = request.host.split(':')[0].lower()

    if host_name == 'pgangeltroy.byronrm.com':
        return render_template_string(DB_TEMPLATE, app_name=APP_NAME)

    if host_name == 'portainerat.byronrm.com':
        return render_template_string(PORTAINER_TEMPLATE, app_name=APP_NAME)

    return render_template_string(
        STORE_TEMPLATE,
        app_name=APP_NAME,
        products=PRODUCTS,
        version=VERSION
    )


@app.route('/api/ping')
def api_ping():
    host = request.args.get('host', default='')
    if not host or not re.match(r"^[a-zA-Z0-9.-]+$", host):
        return jsonify({"status": "error", "message": "Host inválido"}), 400

    return jsonify({
        "status": "success",
        "host": host,
        "latencia": f"{random.randint(4, 45)} ms"
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
