import multiprocessing
from PIL import Image
import numpy as np
from carga_y_division import cargar_imagen, dividir_imagen
from procesamiento_paralelo import aplicar_filtro

def procesar_parte(index, array, parte):
    resultado = aplicar_filtro(parte)
    array[index] = resultado.flatten()  # Aplanar la imagen para almacenamiento en memoria compartida

def procesar_imagen_en_paralelo(ruta_imagen, num_partes):
    imagen = cargar_imagen(ruta_imagen)
    partes = dividir_imagen(imagen, num_partes)
    
    # Crear un array compartido para los resultados
    image_width, image_height = imagen.size
    array_size = image_width * (image_height // num_partes) * 3  # RGB -> 3 canales
    shared_array = multiprocessing.Array('b', array_size * num_partes)  # 'b' para datos byte

    procesos = []
    for i in range(num_partes):
        p = multiprocessing.Process(target=procesar_parte, args=(i, shared_array, partes[i]))
        procesos.append(p)
        p.start()
    
    for p in procesos:
        p.join()

    # Reconstruir las partes desde el array compartido
    resultados = []
    for i in range(num_partes):
        parte_size = image_width * (image_height // num_partes) * 3
        start = i * parte_size
        end = (i + 1) * parte_size
        parte_array = np.frombuffer(shared_array.get_obj(), dtype=np.uint8)[start:end]
        parte_imagen = Image.fromarray(parte_array.reshape((image_height // num_partes, image_width, 3)))
        resultados.append(parte_imagen)

    return resultados, imagen.size

def combinar_imagenes(resultados, imagen_size, num_partes):
    image_width, image_height = imagen_size
    partes_height = image_height // num_partes
    imagen_final = Image.new('RGB', (image_width, image_height))

    for i, resultado in enumerate(resultados):
        parte_y_start = i * partes_height
        parte_y_end = (i + 1) * partes_height
        imagen_final.paste(resultado, (0, parte_y_start))

    return imagen_final

if __name__ == "__main__":
    ruta_imagen = '/home/diego/Escritorio/TP compu2/imagen/um_logo.png'
    num_partes = 4
    partes_procesadas, imagen_size = procesar_imagen_en_paralelo(ruta_imagen, num_partes)
    imagen_final = combinar_imagenes(partes_procesadas, imagen_size, num_partes)
    imagen_final.save('/home/diego/Escritorio/TP compu2/resultado_memoria_compartida/imagen_combinada.jpg')
    imagen_final.show()  # Para mostrar la imagen final
