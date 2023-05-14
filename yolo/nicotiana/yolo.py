"""
GREENS Yolo Decider Script
Version: 1.0
By: María Sánchez Martínez
Date: 17/4/2023
"""
import os
import torch                                      # Biblioteca deep learning - para cargar y ejecutar modelo YOLO
from pathlib import Path                          # Clase para manipular rutas de archivos
from PIL import Image                             # Clase para abrir y procesar imágenes
from yolov5.models.yolo import Model              # Clase que contiene la implementación de YOLOv5

def detect_invasive_species(image_path, model):   # Función que toma como entrada la imagen y el modelo YOLO - llamada por main()
    image = Image.open(image_path)              
    results = model(image, size=640)              # Utiliza el modelo YOLO para realizar la detección y almacena los resultados
    results.print()

    invasive_species_present = False
    detections = []                               # Lista de las coordenadas de las cajas delimitadoras para cada detección de la planta invasora 
  
    # Comprueba si la planta invasora (clase 0) está presente en los resultados recorriendo una lista de tuplas: cada tupla representa un objeto detectado en la imagen y contiene info, como la confianza y la clase -> clase es r[5]
    for scale_results in results.xyxy:              # Itera sobre las diferentes escalas de resultados de detección (hay 5 capas para detectar objetos de distintos tamaños)
        for r in scale_results:                     # Se itera sobre cada detección en la escala actual. Cada detección está representada por un objeto r, que contiene información sobre la detección, como las coordenadas de la caja delimitadora, la confianza y la clase
            if r[5] == 0:                           # Si se detecta la clase 0, es decir, Nicotiana Glauca ...
                invasive_species_present = True
                x1, y1, x2, y2 = map(int, r[:4])    # Se extraen las coordenadas de la caja delimitadora del objeto r - r[:4] contiene las coordenadas en formato float, por lo que se utiliza la función map() para convertirlos a enteros
                detections.append([x1, y1, x2, y2]) # Se agrega la caja delimitadora (en forma de lista de coordenadas) a la lista detections. Esta lista se utilizará para almacenar todas las detecciones de la planta invasora en la imagen

    return invasive_species_present, detections


def detect(image_path):         # Argumento: ruta de la carpeta con fotos y vídeos a analizar
    yaml_path = '/content/yolov5/models/yolov5s.yaml'               # Archivo yaml que describe la arquitectura usada, yolov5s
    weights_path = '/root/yolo/nicotiana/best.pt'                        # Se elige 'best.pt' (y no 'last.pt') porque contiene los pesos del modelo que logró mejores resultados en la validación durante el proceso de entrenamiento

    # Carga del modelo YOLOv5 utilizando el archivo yaml y los pesos del entrenamiento para la detección de Nicotiana Glauca
    model = torch.hub.load('ultralytics/yolov5', 'custom', path =weights_path, force_reload=True)       # Función de PyTorch que se utiliza para cargar modelos pre-entrenados a traves de un repositorio de GitHub (soluciona errores de la primera versión)
    model.eval()               # Se establece el modo de evaluación: no se actualizarán los pesos durante la inferencia (esto solo se hace en el entrenamiento)

    image_extensions = ['.jpg', '.jpeg', '.png']
    video_extensions = ['.mp4', '.avi', '.mkv']

      # Si se trata de un archivo con extensión de imagen o vídeo, se pasa la ruta del archivo (y el modelo) a la función de detección de plantas invasoras
    #if (image_path.suffix.lower() in image_extensions or image_path.suffix.lower() in video_extensions):
    return detect_invasive_species(image_path, model)[0]
