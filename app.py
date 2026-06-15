from flask import Flask
from datetime import datetime
import calendar

app = Flask(__name__)

# Incrementamos la versión por este nuevo feature del calendario
VERSION = "1.1.0"

@app.route("/")
def inicio():
    # 1. Obtener fecha y hora actual
    ahora = datetime.now()
    fecha_hora_texto = ahora.strftime("%Y-%m-%d %H:%M:%S")
    
    # 2. Generar el calendario del mes actual en HTML
    # Empezamos la semana en lunes (0)
    cal = calendar.HTMLCalendar(firstweekday=0) 
    calendario_html = cal.formatmonth(ahora.year, ahora.month)
    
    # 3. Truco para resaltar el día actual en la tabla
    dia_actual = ahora.day
    etiqueta_hoy = f"<td>{dia_actual}</td>"
    etiqueta_resaltada = f"<td style='background-color: #007bff; color: white; font-weight: bold; border-radius: 5px;'>{dia_actual}</td>"
    calendario_html = calendario_html.replace(etiqueta_hoy, etiqueta_resaltada)

    # 4. Estilos CSS básicos para que la tabla del calendario se vea ordenada
    estilos_css = """
    <style>
        body { font-family: Arial, sans-serif; margin: 30px; }
        table.month { border-collapse: collapse; margin-top: 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        table.month th { background-color: #343a40; color: white; padding: 10px; text-align: center; }
        table.month td { border: 1px solid #dee2e6; padding: 12px; text-align: center; width: 40px; }
        table.month td.noday { background-color: #f8f9fa; }
    </style>
    """

    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        {estilos_css}
        <title>Reloj y Calendario</title>
    </head>
    <body>
        <h1>Aplicación Flask - Reloj & Calendario 📅</h1>
        <h2>Versión {VERSION}</h2>
        <p style="color: blue;"><strong>Servidor activo y respondiendo</strong></p>
        
        <h3>Información del Servidor:</h3>
        <ul>
            <li><strong>Fecha y Hora actual:</strong> {fecha_hora_texto}</li>
        </ul>

        <h3>Calendario Mensual:</h3>
        {calendario_html}
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)