import multiprocessing
from scipy.ndimage import gaussian_filter
import numpy as np
from PIL import Image  

def aplicar_filtro(parte):
    return gaussian_filter(parte, sigma=10)

def procesar_partes(partes):
    with multiprocessing.Pool(processes=len(partes)) as pool:
        resultados = pool.map(aplicar_filtro, partes)
    return resultados

if __name__ == "__main__":
    from carga_y_division import cargar_imagen, dividir_imagen

    ruta_imagen = '/home/diego/Escritorio/TP compu2/imagen/um_logo.png'
    num_partes = 4
    imagen = cargar_imagen(ruta_imagen)
    partes = dividir_imagen(imagen, num_partes)
    partes_procesadas = procesar_partes(partes)
    for i, parte in enumerate(partes_procesadas):
        parte_imagen = Image.fromarray(np.uint8(parte))
        parte_imagen = parte_imagen.convert("RGB")  
        parte_imagen.save(f'/home/diego/Escritorio/TP compu2/resultado_procesamiento_paralelo/parte_procesada_{i}.jpg')
