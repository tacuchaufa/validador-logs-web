import os
import re

def procesar_logs(ruta_codigos, carpeta_logs, ruta_salida):
    """
    Procesa los logs buscando códigos de error.

    Parámetros:
    - ruta_codigos: archivo .txt con códigos
    - carpeta_logs: carpeta con logs (ya extraídos)
    - ruta_salida: archivo donde se guardará el resultado
    """

    # --------------------------------
    # Leer códigos de error
    # --------------------------------
    with open(ruta_codigos, "r", encoding="utf-8") as archivo_codigos:
        codigos_error = [linea.strip() for linea in archivo_codigos if linea.strip()]

    # --------------------------------
    # Preparar regex (preciso)
    # --------------------------------
    patrones = [
        re.compile(rf'\b{re.escape(codigo)}\b', re.IGNORECASE)
        for codigo in codigos_error
    ]

    # --------------------------------
    # Inicializar contadores
    # --------------------------------
    total_archivos_analizados = 0
    total_coincidencias = 0
    se_encontraron_resultados = False

    # Conteo por código (por si lo usas después)
    conteo_por_codigo = {codigo: 0 for codigo in codigos_error}

    # --------------------------------
    # Procesamiento
    # --------------------------------
    with open(ruta_salida, "w", encoding="utf-8") as archivo_resultado:

        for carpeta_actual, _, archivos in os.walk(carpeta_logs):
            for nombre_archivo in archivos:

                if not nombre_archivo.lower().endswith((".txt", ".log")):
                    continue

                ruta_completa_log = os.path.join(carpeta_actual, nombre_archivo)
                total_archivos_analizados += 1

                try:
                    with open(ruta_completa_log, "r", encoding="utf-8", errors="ignore") as archivo_log:

                        for linea in archivo_log:

                            for i, patron in enumerate(patrones):
                                if patron.search(linea):

                                    codigo = codigos_error[i]

                                    archivo_resultado.write(
                                        f"[{codigo}] - {ruta_completa_log}\n"
                                    )

                                    total_coincidencias += 1
                                    conteo_por_codigo[codigo] += 1
                                    se_encontraron_resultados = True

                                    break  # pasar a la siguiente línea

                except Exception:
                    # Ignorar archivos no legibles
                    continue

        # --------------------------------
        # Caso sin resultados
        # --------------------------------
        if not se_encontraron_resultados:
            archivo_resultado.write("No se encontraron errores en la revisión\n")

        # --------------------------------
        # Resumen
        # --------------------------------
        archivo_resultado.write("\n\n")
        archivo_resultado.write("RESUMEN DE LA REVISIÓN\n")
        archivo_resultado.write(f"Total de archivos analizados: {total_archivos_analizados}\n")
        archivo_resultado.write(f"Total de coincidencias: {total_coincidencias}\n")

        # --------------------------------
        # Conteo por código (extra)
        # --------------------------------
        archivo_resultado.write("\nConteo por código:\n")
        for codigo, cantidad in conteo_por_codigo.items():
            archivo_resultado.write(f"{codigo}: {cantidad}\n")