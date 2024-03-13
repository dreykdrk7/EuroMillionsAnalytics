import sqlite3
from collections import defaultdict
import pandas as pd

class EstadisticasFrecuencia:
    def __init__(self, db_path='estadisticas'):
        self.db_path = f'data/{db_path}.db'
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.crear_tablas()

    def crear_tablas(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS FrecuenciaNumeros (
                id INTEGER PRIMARY KEY,
                valor INTEGER NOT NULL,
                frecuencia INTEGER NOT NULL,
                año INTEGER NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS FrecuenciaEstrellas (
                id INTEGER PRIMARY KEY,
                valor INTEGER NOT NULL,
                frecuencia INTEGER NOT NULL,
                año INTEGER NOT NULL
            );
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS FrecuenciasTotales (
                año INTEGER PRIMARY KEY,
                total_sorteos INTEGER NOT NULL,
                total_numeros INTEGER NOT NULL,
                total_estrellas INTEGER NOT NULL
            );
        ''')
        self.conn.commit()

    def reiniciar_totales_anuales(self, año):
        self.cursor.execute("DELETE FROM FrecuenciaNumeros WHERE año = ?", (año,))
        self.cursor.execute("DELETE FROM FrecuenciaEstrellas WHERE año = ?", (año,))
        self.conn.commit()

    def procesar_sorteos(self, sorteos, año=None):
        if año:
            self.reiniciar_totales_anuales(año)

        estadisticas_numeros = defaultdict(lambda: defaultdict(int))
        estadisticas_estrellas = defaultdict(lambda: defaultdict(int))
        totales_anuales = defaultdict(lambda: defaultdict(int))

        for sorteo in sorteos:
            fecha = sorteo['fecha']
            año = pd.to_datetime(fecha).year
            totales_anuales[año]['total_sorteos'] += 1
            totales_anuales[año]['total_numeros'] += len(sorteo['numeros'])
            totales_anuales[año]['total_estrellas'] += len(sorteo['estrellas'])
            
            for numero in sorteo['numeros']:
                estadisticas_numeros[numero][año] += 1
            for estrella in sorteo['estrellas']:
                estadisticas_estrellas[estrella][año] += 1

        self.guardar_estadisticas(estadisticas_numeros, 'FrecuenciaNumeros')
        self.guardar_estadisticas(estadisticas_estrellas, 'FrecuenciaEstrellas')
        self.actualizar_totales_anuales(totales_anuales)

    def guardar_estadisticas(self, estadisticas, tabla):
        for valor, frecuencias_año in estadisticas.items():
            for año, frecuencia in frecuencias_año.items():
                self.cursor.execute(f'''
                    INSERT INTO {tabla} (valor, frecuencia, año)
                    VALUES (?, ?, ?)
                ''', (valor, frecuencia, año))
        self.conn.commit()
    
    def actualizar_totales_anuales(self, totales_anuales):
        for año, totales in totales_anuales.items():
            self.cursor.execute("SELECT total_sorteos, total_numeros, total_estrellas FROM FrecuenciasTotales WHERE año = ?", (año,))
            fila = self.cursor.fetchone()
            if fila:
                total_sorteos, total_numeros, total_estrellas = fila
                total_sorteos = totales['total_sorteos']
                total_numeros = totales['total_numeros']
                total_estrellas = totales['total_estrellas']
                self.cursor.execute("""
                    UPDATE FrecuenciasTotales 
                    SET total_sorteos = ?, total_numeros = ?, total_estrellas = ? 
                    WHERE año = ?
                """, (total_sorteos, total_numeros, total_estrellas, año))
            else:
                self.cursor.execute("""
                    INSERT INTO FrecuenciasTotales (año, total_sorteos, total_numeros, total_estrellas) 
                    VALUES (?, ?, ?, ?)
                """, (año, totales['total_sorteos'], totales['total_numeros'], totales['total_estrellas']))
        self.conn.commit()

    def obtener_mas_frecuentes(self, tabla, año=None, X=10):
        """
        Obtiene los valores más frecuentes de la tabla especificada.

        Args:
            tabla (str): Nombre de la tabla ('FrecuenciaNumeros' o 'FrecuenciaEstrellas').
            año (int, optional): Año específico para filtrar. Si es None, considera todos los años.
            X (int, optional): Número de resultados a retornar.
        
        Returns:
            list: Lista de diccionarios con 'valor', 'frecuencia' total y 'porcentaje'.
        """
        # Primero, calculamos el total de frecuencias
        total_query = f"SELECT SUM(frecuencia) FROM {tabla}"
        total_params = []
        if año:
            total_query += " WHERE año = ?"
            total_params.append(año)
        self.cursor.execute(total_query, total_params)
        total_frecuencias = self.cursor.fetchone()[0]

        # Luego, obtenemos los valores más frecuentes
        query_base = f'''
            SELECT valor, SUM(frecuencia) as total_frecuencia
            FROM {tabla}
        '''
        params = []

        if año:
            query_base += " WHERE año = ?"
            params.append(año)

        query_base += '''
            GROUP BY valor
            ORDER BY total_frecuencia DESC
            LIMIT ?
        '''
        params.append(X)

        self.cursor.execute(query_base, params)
        resultados = self.cursor.fetchall()

        # Calculamos el porcentaje de cada valor respecto al total de frecuencias
        resultados_con_porcentaje = []
        for valor, frecuencia in resultados:
            porcentaje = (frecuencia / total_frecuencias) * 100
            resultados_con_porcentaje.append({
                'valor': valor,
                'frecuencia': frecuencia,
                'porcentaje': porcentaje
            })

        return resultados_con_porcentaje

    def obtener_menos_frecuentes(self, tabla, año=None, X=10):
        """
        Obtiene los valores menos frecuentes de la tabla especificada, incluyendo el porcentaje de aparición.

        Args:
            tabla (str): Nombre de la tabla ('FrecuenciaNumeros' o 'FrecuenciaEstrellas').
            año (int, optional): Año específico para filtrar. Si es None, considera todos los años.
            X (int, optional): Número de resultados a retornar.
        
        Returns:
            list: Lista de diccionarios con 'valor', 'frecuencia' total y 'porcentaje'.
        """
        # Calcula el total de frecuencias para el año o en general
        total_query = f"SELECT SUM(frecuencia) FROM {tabla}"
        total_params = []
        if año:
            total_query += " WHERE año = ?"
            total_params.append(año)
        self.cursor.execute(total_query, total_params)
        total_frecuencias = self.cursor.fetchone()[0]

        # Obtiene los valores menos frecuentes
        query_base = f'''
            SELECT valor, SUM(frecuencia) as total_frecuencia
            FROM {tabla}
        '''
        params = []

        if año:
            query_base += " WHERE año = ?"
            params.append(año)

        query_base += '''
            GROUP BY valor
            ORDER BY total_frecuencia ASC
            LIMIT ?
        '''
        params.append(X)

        self.cursor.execute(query_base, params)
        resultados = self.cursor.fetchall()

        # Calcula el porcentaje de cada valor
        resultados_con_porcentaje = []
        for valor, frecuencia in resultados:
            porcentaje = (frecuencia / total_frecuencias) * 100
            resultados_con_porcentaje.append({
                'valor': valor,
                'frecuencia': frecuencia,
                'porcentaje': porcentaje
            })

        return resultados_con_porcentaje

    def cerrar_conexion(self):
        self.conn.close()


# Uso de la clase simplificado para el ejemplo
if __name__ == '__main__':
    sorteos = [
        {'fecha': '2024-01-10', 'numeros': [4, 7, 23, 41, 50], 'estrellas': [2, 12]},
        {'fecha': '2024-01-17', 'numeros': [12, 19, 28, 41, 45], 'estrellas': [1, 12]},
    ]

    gestor = EstadisticasFrecuencia()
    gestor.procesar_sorteos(sorteos)
    print("Estadísticas de frecuencia guardadas en la base de datos.")
    gestor.cerrar_conexion()

