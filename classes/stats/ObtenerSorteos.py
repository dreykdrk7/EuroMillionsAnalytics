import sqlite3
import json
import pandas as pd

import sqlite3
import json

class ObtenerSorteos:
    def __init__(self, db_path='euromillones_database'):
        self.db_path = f'data/{db_path}.db'

    def _procesar_combinacion(self, combinacion_sorteo):
        partes = combinacion_sorteo.split(' - ')
        numeros = [int(n) for n in partes[:5]]
        estrellas = [int(e) for e in partes[5:]]
        return numeros, estrellas

    def obtener_todos(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT fecha, combinacion, premio_bote, escrutinio FROM resultados_sorteos")
            sorteos = cursor.fetchall()

        return self._procesar_sorteos(sorteos)

    def obtener_sorteos_año(self, año):
        fecha_inicio = f"{año}-01-01"
        fecha_fin = f"{año}-12-31"
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT fecha, combinacion, premio_bote, escrutinio FROM resultados_sorteos WHERE fecha BETWEEN ? AND ?", (fecha_inicio, fecha_fin))
            sorteos = cursor.fetchall()

        return self._procesar_sorteos(sorteos)

    def _procesar_sorteos(self, sorteos):
        resultados_sorteos = []
        for sorteo in sorteos:
            fecha, combinacion_sorteo, premio_bote, escrutinio_json = sorteo
            escrutinio = json.loads(escrutinio_json)
            numeros, estrellas = self._procesar_combinacion(combinacion_sorteo)
            resultados_sorteos.append({
                'fecha': fecha,
                'numeros': numeros,
                'estrellas': estrellas,
                'premio_bote': premio_bote,
                'escrutinio': escrutinio
            })
        return resultados_sorteos

if __name__ == '__main__':
    estadisticas = ObtenerSorteos()
    sorteos = estadisticas.obtener_sorteos_año(2020)
    print(sorteos)

