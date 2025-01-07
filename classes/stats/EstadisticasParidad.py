import sqlite3
import pandas as pd

class EstadisticasParidad:
    def __init__(self, db_path='estadisticas'):
        self.db_path = f'data/{db_path}.db'
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.crear_tablas()

    def crear_tablas(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ParidadAnual (
                año INTEGER PRIMARY KEY,
                num_pares INTEGER,
                num_impares INTEGER,
                est_pares INTEGER,
                est_impares INTEGER
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ParidadFigurasNumeros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                año INTEGER NOT NULL,
                figura TEXT NOT NULL, -- Ejemplo de formato: '3/2'
                cantidad INTEGER NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ParidadFigurasEstrellas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                año INTEGER NOT NULL,
                figura TEXT NOT NULL, -- Ejemplo de formato: '2-0'
                cantidad INTEGER NOT NULL
            )
        ''')
        self.conn.commit()
    
    def calcular_figuras(self, sorteos):
        estadisticas = {}

        for sorteo in sorteos:
            fecha = sorteo['fecha']
            año = pd.to_datetime(fecha).year

            num_pares = sorteo['num_pares']
            num_impares = sorteo['num_impares']
            est_pares = sorteo['est_pares']
            est_impares = sorteo['est_impares']
            
            figura_numeros = f"{num_pares}-{num_impares}"
            figura_estrellas = f"{est_pares}-{est_impares}"
            
            if año not in estadisticas:
                estadisticas[año] = {'numeros': {}, 'estrellas': {}}
            
            if figura_numeros not in estadisticas[año]['numeros']:
                estadisticas[año]['numeros'][figura_numeros] = 0
            estadisticas[año]['numeros'][figura_numeros] += 1

            if figura_estrellas not in estadisticas[año]['estrellas']:
                estadisticas[año]['estrellas'][figura_estrellas] = 0
            estadisticas[año]['estrellas'][figura_estrellas] += 1

        self.ordenar_figuras_numeros(estadisticas)
        self.ordenar_figuras_estrellas(estadisticas)
        return estadisticas
    
    def ordenar_figuras_numeros(self, estadisticas):
        figuras_orden_numeros = ['5-0', '4-1', '3-2', '2-3', '1-4', '0-5']
        
        for año, datos in estadisticas.items():
            figuras_ordenadas_temp = {figura: datos['numeros'].get(figura, 0) for figura in figuras_orden_numeros}
            estadisticas[año]['numeros'] = figuras_ordenadas_temp

        return estadisticas
    
    def ordenar_figuras_estrellas(self, estadisticas):
        figuras_orden_estrellas = ['2-0', '1-1', '0-2']
        
        for año, datos in estadisticas.items():
            figuras_ordenadas_temp = {figura: datos['estrellas'].get(figura, 0) for figura in figuras_orden_estrellas}
            estadisticas[año]['estrellas'] = figuras_ordenadas_temp

        return estadisticas

    def insertar_datos_anuales(self, datos_paridad):
        for dato in datos_paridad:
            año, num_pares, num_impares, est_pares, est_impares = dato
            self.cursor.execute('''
                INSERT INTO ParidadAnual (año, num_pares, num_impares, est_pares, est_impares) 
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(año) DO UPDATE SET
                num_pares = excluded.num_pares,
                num_impares = excluded.num_impares,
                est_pares = excluded.est_pares,
                est_impares = excluded.est_impares
            ''', (int(año), num_pares, num_impares, est_pares, est_impares))
        self.conn.commit()

    def insertar_figuras(self, estadisticas, tipo):

        # Determina la tabla adecuada basada en el tipo
        tabla = 'ParidadFigurasNumeros' if tipo == 'numeros' else 'ParidadFigurasEstrellas'

        # Recorre el diccionario de estadísticas e inserta los datos en la base de datos
        for año, datos in estadisticas.items():
            for figura, cantidad in datos[tipo].items():
                self.cursor.execute(f'''
                    INSERT INTO {tabla} (año, figura, cantidad)
                    VALUES (?, ?, ?)
                ''', (año, figura, cantidad))

        self.conn.commit()
        self.cerrar_conexion()

    def cerrar_conexion(self):
        self.conn.close()

# Ejemplo de uso:
if __name__ == "__main__":
    gestor_paridad = EstadisticasParidad()
    # Asumiendo que 'resultados' contiene los datos de paridad obtenidos
    resultados = [(2004, 108, 127, 42, 52), (2005, 127, 133, 38, 66)]
    gestor_paridad.insertar_datos_paridad(resultados)
    gestor_paridad.cerrar_conexion()
