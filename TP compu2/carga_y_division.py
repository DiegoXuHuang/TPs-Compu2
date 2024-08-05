from PIL import Image
import numpy as np

def cargar_imagen(ruta):
    imagen = Image.open(ruta)
    return np.array(imagen)

def dividir_imagen(imagen, num_partes):
    alto, ancho, _ = imagen.shape
    partes = []
    altura_parte = alto // num_partes
    for i in range(num_partes):
        inicio = i * altura_parte
        fin = (i + 1) * altura_parte if i < num_partes - 1 else alto
        partes.append(imagen[inicio:fin, :, :])
    return partes

if __name__ == "__main__":
    ruta_imagen = '/Users/diego/Desktop/TPs-Compu2/TP compu2/imagen/um_logo.png'
    num_partes = 4
    imagen = cargar_imagen(ruta_imagen)
    partes = dividir_imagen(imagen, num_partes)
    for i, parte in enumerate(partes):
        parte_imagen = Image.fromarray(parte)
        parte_imagen = parte_imagen.convert("RGB")  
        parte_imagen.save(f'/Users/diego/Desktop/TPs-Compu2/TP compu2/resultado_carga_y_division/parte_{i}.jpg')










