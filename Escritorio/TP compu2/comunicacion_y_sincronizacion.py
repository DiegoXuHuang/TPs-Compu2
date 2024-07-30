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
    
    return resultados, imagen.shape  # Devolver también la forma original de la imagen

def combinar_partes(partes_procesadas, imagen_shape, num_partes):
    alto, ancho, _ = imagen_shape
    altura_parte = alto // num_partes
    imagen_final = np.zeros(imagen_shape, dtype=np.uint8)
    
    for i, parte in enumerate(partes_procesadas):
        inicio = i * altura_parte
        fin = (i + 1) * altura_parte if i < num_partes - 1 else alto
        imagen_final[inicio:fin, :, :] = parte
    
    return imagen_final

if __name__ == "__main__":
    ruta_imagen = '/home/diego/Escritorio/TP compu2/imagen/um_logo.png'
    num_partes = 4
    partes_procesadas, imagen_shape = procesar_imagen_en_paralelo(ruta_imagen, num_partes)
    
    imagen_final = combinar_partes(partes_procesadas, imagen_shape, num_partes)
    
    parte_imagen = Image.fromarray(imagen_final)
    parte_imagen = parte_imagen.convert("RGB")  
    parte_imagen.save(f'/home/diego/Escritorio/TP compu2/resultado_comunicacion_y_sincronizacion/imagen_final.jpg')
