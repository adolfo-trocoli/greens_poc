"""
GREENS GPS Mock Module
Version: 1.0
By: Adolfo Trocolí Naranjo, Sergio Roca Montesa
Date: 24/4/2023
"""

import random

class GPS:
    LATITUD_MIN = 28.930
    LATITUD_MAX = 29.116
    LONGITUD_MIN = -13.828
    LONGITUD_MAX = -13.464

    def __init__(self):
        self.coord = None
        self.updated = False

    def update(self, coordinates):
        self.coord = coordinates
        self.updated = True
    
    def get_random(self):
        lat = round(random.uniform(self.LATITUD_MIN, self.LATITUD_MAX), 6)
        long = round(random.uniform(self.LONGITUD_MIN, self.LONGITUD_MAX), 6)
        return (lat, long)

    def get_coord(self):
        if(self.updated):
            self.updated = False
        else:
            self.coord = self.get_random()
        return self.coord
