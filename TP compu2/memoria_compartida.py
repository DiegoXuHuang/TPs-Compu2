import multiprocessing
import numpy as np
from PIL import Image
from carga_y_division import cargar_imagen, dividir_imagen
from procesamiento_paralelo import aplicar_filtro
import os

def procesar_parte(shared_array, shape, start_idx, parte):
    resultado = aplicar_filtro(parte)
    shared_array[start_idx:start_idx+len(resultado.flatten())] = resultado.flatten()

def procesar_imagen_en_paralelo(ruta_imagen, num_partes):
    imagen = cargar_imagen(ruta_imagen)
    partes = dividir_imagen(imagen, num_partes)
    
    alto, ancho, canales = imagen.shape
    total_size = alto * ancho * canales
    shared_array = multiprocessing.Array('d', total_size)  # Crear un array compartido

    procesos = []
    start_idx = 0
    
    for i in range(num_partes):
        parte = partes[i]
        p = multiprocessing.Process(target=procesar_parte, args=(shared_array, imagen.shape, start_idx, parte))
        procesos.append(p)
        p.start()
        start_idx += parte.size  # Actualizar el índice de inicio
    
    for p in procesos:
        p.join()
    
    # Convertir el array compartido de nuevo a una imagen numpy
    resultado_array = np.frombuffer(shared_array.get_obj())
    resultado_array = resultado_array.reshape(alto, ancho, canales)
    
    return resultado_array

if __name__ == "__main__":
    ruta_imagen = '/Users/diego/Desktop/TPs-Compu2/TP compu2/imagen/um_logo.png'
    num_partes = 4
    imagen_final = procesar_imagen_en_paralelo(ruta_imagen, num_partes)
    
    # Crear el directorio si no existe
    directorio_resultado = '/Users/diego/Desktop/TPs-Compu2/TP compu2/resultado_memoria_compartida'
    if not os.path.exists(directorio_resultado):
        os.makedirs(directorio_resultado)
    
    imagen_final = Image.fromarray(np.uint8(imagen_final))
    imagen_final = imagen_final.convert("RGB")
    imagen_final.save(f'{directorio_resultado}/imagen_final.jpg')
    print(f'Imagen final procesada y guardada como {directorio_resultado}/imagen_final.jpg')
