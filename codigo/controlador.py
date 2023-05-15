#!/usr/bin/python3

"""
GREENS Controller
Version: 1.0
By: Adolfo Trocolí Naranjo
Date: 4/5/2023
"""

import gps
import subprocess
import os
import sys
import re
import csv
from pathlib import Path 
import time
sys.path.insert(1, '/root/yolo/girasol/')
import yolo
sample_image_folder = "/root/yolo/girasol/fotos"
images = os.scandir(sample_image_folder)
image_extensions = ['.jpg', '.jpeg', '.png']
coord = None # should be a (latitude, longitude) tuple
coordinates_regex = re.compile("\n?(.*)\n(.*)\n?")
update_count = 0
positive_count = 0
file_count = 0
log_file = '/root/log/log_file.txt'
species_location_file = '/root/R/species_location.csv'
get_prediction_file = '/root/R/DEF_update_map.r'
next_coord_file = '/root/R/DEF_next_move.r'
open(log_file, 'w').close() # clear log file

def next_file():
    """Returns file path if there are more images to inspect in folder. Returns None if there are no more.
    Updates file_count with each iteration
    """
    global file_count
    try:
        entry = next(images)
        file_count += 1
    except StopIteration as e:
        return
    if entry.is_file() and (Path(entry.path).suffix.lower() in image_extensions or Path(entry.path).suffix.lower() in video_extensions):
        return entry.path

def log(log_message):
    """Log messages to log file"""
    with open(log_file, 'a') as file:
        file.write(log_message + '\n')

def close():
    """Closing method por proof of concept"""
    log('Demo finished, all images inspected.')
    log(f'{positive_count} de {file_count} imágenes contenían Nicotiana Glauca')
    quit()

def SIGINT_handler():
    """Closing method for keyboard interruptions by user"""
    log('Program closed by SIGINT signal.')
    log(f'{positive_count} de {file_count} imágenes contenían Nicotiana Glauca')
    quit()

def update_map(coord):
    """Llama al script de actualización del mapa"""
    log('Actualizando el mapa')
    lat, lon = coord
    with open(species_location_file, 'a', newline='') as archivo_csv:
       writer = csv.writer(archivo_csv, quoting=csv.QUOTE_NONNUMERIC)
       writer.writerow(["Nicotiana glauca Graham", lat, lon])
    subprocess.run(f"R --vanilla -q < {get_prediction_file}", shell=True)

def check_next_coord(coord):
    """Ejecuta el script para obtener una nueva coordenada y la devuelve si se ha hallado con éxito"""
    lat, lon = coord
    out = subprocess.run(f"Rscript --vanilla -q {next_coord_file} {lon} {lat}", shell=True, capture_output=True).stdout.decode('UTF-8')
    log(f'Obteniendo siguientes coordenadas: {lon}, {lat}.')
    next_coord = re.search(coordinates_regex, out)
    if(next_coord is None):
        return
    try:
        return(float(next_coord.group(2)), float(next_coord.group(1))) # devuelve la tupla (lat, lon) = coord
    except:
        return None

def yolo_detect(image_path):
    """ Llamada a Yolo para detectar si existe objeto de interés en la imagen"""
    global positive_count
    result = yolo.detect(image_path)
    if(result):
        positive_count += 1
        log(f'YOLO: Positive detection. Number of positives: {positive_count}')
    else:
        log(f'YOLO: Negative detection.')
    return result

def new_positive(coord):
    """ Cuenta un nuevo positivo y, al llegar a 10, actualiza el mapa."""
    global update_count
    update_count += 1
    if (update_count == 10):
        update_map(coord)
        update_count = 0

def main():
    """ Bucle infinito en el que, por orden:
        - Consigue las coordenadas actuales del gps.
        - Consigue una nueva imagen.
        - Comprueba si existe un acierto en la imagen. De haberlo, actualiza el mapa.
    """
    moduloGPS = gps.GPS()
    while(True):
        start_time = time.time()
        coord = moduloGPS.get_coord()
        image_path = next_file()
        if(image_path is None):
            close()
        if(yolo_detect(image_path)):
            new_positive(coord)
        next_coord = check_next_coord(coord)
        if(next_coord is not None):
            moduloGPS.update(next_coord)
        log(f'--- Last cycle: {time.time() - start_time} seconds ---\n')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        SIGINT_handler()
