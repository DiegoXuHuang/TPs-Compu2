import multiprocessing
import signal
import sys
import numpy as np
from PIL import Image
from carga_y_division import cargar_imagen, dividir_imagen
from procesamiento_paralelo import aplicar_filtro
import time
import os

procesos = []
pipes = []

def manejador_senal(signum, frame):
    print("Interrupción recibida. Terminando procesos...")
    for p in procesos:
        p.terminate()
    for parent_conn in pipes:
        parent_conn.close()
    sys.exit(0)

def procesar_parte(conexion, parte):
    try:
        resultado = aplicar_filtro(parte)
        conexion.send(resultado)
    except Exception as e:
        conexion.send({'error': str(e)})
    finally:
        conexion.close()

def procesar_imagen_en_paralelo(ruta_imagen, num_partes):
    imagen = cargar_imagen(ruta_imagen)
    partes = dividir_imagen(imagen, num_partes)
    global pipes
    parent_conns, child_conns = zip(*[multiprocessing.Pipe() for _ in range(num_partes)])
    pipes = parent_conns
    global procesos
    procesos = []
    
    for i in range(num_partes):
        p = multiprocessing.Process(target=procesar_parte, args=(child_conns[i], partes[i]))
        procesos.append(p)
        p.start()
    
    resultados = []
    for conn in parent_conns:
        try:
            resultado = conn.recv()
            if 'error' in resultado:
                print(f"Error en el procesamiento de una parte: {resultado['error']}")
            else:
                resultados.append(resultado)
        except EOFError:
            pass
    
    # for p in procesos:
    #     p.join(timeout=10)  
    
    return resultados

if __name__ == "__main__":
    signal.signal(signal.SIGINT, manejador_senal)

    print("Presiona Ctrl+C para interrumpir el proceso o espere 15 segundo hasta que se termine la ejecucion")
    
    ruta_imagen = '/home/diego/Escritorio/TP compu2/imagen/um_logo.png'
    num_partes = 4
    try:
        partes_procesadas = procesar_imagen_en_paralelo(ruta_imagen, num_partes)
        
        # Esperar 15 segundos antes de imprimir los resultados
        time.sleep(15)
        
        # Crear el directorio si no existe
        directorio_resultado = '/home/diego/Escritorio/TP compu2/resultado_manejo_de_senales'
        if not os.path.exists(directorio_resultado):
            os.makedirs(directorio_resultado)
        
        for i, parte in enumerate(partes_procesadas):
            parte_imagen = Image.fromarray(np.uint8(parte))
            parte_imagen = parte_imagen.convert("RGB")  
            nombre_archivo = os.path.join(directorio_resultado, f'parte_{i}.jpg')
            parte_imagen.save(nombre_archivo)
            print(f'Parte {i} procesada y guardada como {nombre_archivo}')
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Esperando a que los procesos terminen...")
        time.sleep(5)  # Esperar 5 segundos adicionales para permitir la limpieza completa
