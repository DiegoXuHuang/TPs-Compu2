import multiprocessing
from PIL import Image
import numpy as np
from carga_y_division import cargar_imagen, dividir_imagen
from procesamiento_paralelo import aplicar_filtro

def procesar_parte(conn, parte):
    resultado = aplicar_filtro(parte)
    conn.send(resultado)
    conn.close()

def procesar_imagen_en_paralelo(ruta_imagen, num_partes):
    imagen = cargar_imagen(ruta_imagen)
    partes = dividir_imagen(imagen, num_partes)
    parent_conns, child_conns = zip(*[multiprocessing.Pipe() for _ in range(num_partes)])
    procesos = []
    for i in range(num_partes):
        p = multiprocessing.Process(target=procesar_parte, args=(child_conns[i], partes[i]))
        procesos.append(p)
        p.start()
    
    resultados = [conn.recv() for conn in parent_conns]
    
    for p in procesos:
        p.join()
    
    return resultados

if __name__ == "__main__":
    ruta_imagen = '/home/diego/Escritorio/TP compu2/imagen/um_logo.png'
    num_partes = 4
    partes_procesadas = procesar_imagen_en_paralelo(ruta_imagen, num_partes)
    for i, parte in enumerate(partes_procesadas):
        parte_imagen = Image.fromarray(np.uint8(parte))
        parte_imagen = parte_imagen.convert("RGB")  # Convertir a modo RGB
        parte_imagen.save(f'/home/diego/Escritorio/TP compu2/resultado_comunicacion_y_sincronizacion/parte_combinada_{i}.jpg')
