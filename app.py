from flask import Flask, request, render_template, send_file
from procesador import procesar_logs
import os
import zipfile
import shutil
from datetime import datetime

# --------------------------------
# Configuración inicial
# --------------------------------
app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
LOGS_FOLDER = os.path.join(BASE_DIR, "logs_extraidos")

# Crear carpetas si no existen
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(LOGS_FOLDER, exist_ok=True)

# --------------------------------
# Ruta principal (carga la página)
# --------------------------------
@app.route("/")
def index():
    return render_template("index.html")

# --------------------------------
# Ruta para procesar archivos
# --------------------------------
@app.route("/procesar", methods=["POST"])
def procesar():

    # Validar que los archivos existan
    #if "codigos" not in request.files or "logs" not in request.files:
    if "logs" not in request.files:
        return "Faltan archivos", 400

    #archivo_codigos = request.files["codigos"]
    archivo_logs = request.files["logs"]

    if archivo_logs.filename == "":
        return "Debe seleccionar archivos", 400

    # --------------------------------
    # Guardar archivos en servidor
    # --------------------------------
    # antiguo, pidiendo archivo cada vez
    # ruta_codigos = os.path.join(UPLOAD_FOLDER, archivo_codigos.filename)
    # nuevo, archivo fija en carpeta dentro del proyecto
    
    ruta_codigos = os.path.join(BASE_DIR, "data", "ERROR_CODES.txt")
    ruta_logs = os.path.join(UPLOAD_FOLDER, archivo_logs.filename)

    #archivo_codigos.save(ruta_codigos)
    archivo_logs.save(ruta_logs)

    # --------------------------------
    # Preparar carpeta de logs
    # --------------------------------
    carpeta_logs_procesados = LOGS_FOLDER

    # Limpiar carpeta antes de usarla

    for archivo in os.listdir(carpeta_logs_procesados):
        ruta_archivo = os.path.join(carpeta_logs_procesados, archivo)
    try:
        if os.path.isfile(ruta_archivo):
            os.remove(ruta_archivo)
        elif os.path.isdir(ruta_archivo):
            shutil.rmtree(ruta_archivo)  # ✅ elimina carpetas completas
    except Exception:
        pass


    # --------------------------------
    # Si es ZIP, descomprimir
    # --------------------------------
    if ruta_logs.lower().endswith(".zip"):
        try:
            with zipfile.ZipFile(ruta_logs, 'r') as zip_ref:
                zip_ref.extractall(carpeta_logs_procesados)
        except Exception as e:
            return f"Error al descomprimir ZIP: {str(e)}", 500
    else:
        # Si no es ZIP, simplemente copiar archivo como log único
        destino = os.path.join(carpeta_logs_procesados, archivo_logs.filename)
        os.replace(ruta_logs, destino)

    # --------------------------------
    # Generar archivo de salida
    # --------------------------------
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_salida = f"resultado_val_queries_{timestamp}.txt"
    ruta_salida = os.path.join(UPLOAD_FOLDER, nombre_salida)

    # --------------------------------
    # Ejecutar procesamiento real
    # --------------------------------
    
    try:
        from procesador import procesar_logs
        procesar_logs(ruta_codigos, carpeta_logs_procesados, ruta_salida)
    except Exception as e:
        return f"Error durante el procesamiento: {str(e)}", 500

    # --------------------------------
    # Descargar archivo resultante
    # --------------------------------
    return send_file(ruta_salida, as_attachment=True)


# --------------------------------
# Ejecutar aplicación (modo local)
# --------------------------------
if __name__ == "__main__":
    app.run(debug=True)
