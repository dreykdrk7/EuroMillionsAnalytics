import sqlite3
from datetime import datetime
from collections import defaultdict
import pandas as pd

class EstadisticasSecuencia:
    def __init__(self, sorteos, db_path='estadisticas'):
        self.sorteos = sorteos
        self.secuencias_numeros = defaultdict(lambda: defaultdict(int))
        self.secuencias_estrellas = defaultdict(lambda: defaultdict(int))

        self.db_path = f'data/{db_path}.db'
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.crear_tablas()
    
    def crear_tablas(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS SecuenciasNumeros (
                id INTEGER PRIMARY KEY,
                valor INTEGER NOT NULL,
                año INTEGER NOT NULL,
                veces INTEGER NOT NULL
            );
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS SecuenciasEstrellas (
                id INTEGER PRIMARY KEY,
                valor INTEGER NOT NULL,
                año INTEGER NOT NULL,
                veces INTEGER NOT NULL
            );
        ''')
        self.conn.commit()
    
    def reiniciar_secuencias_anuales(self, año):
        self.cursor.execute("DELETE FROM SecuenciasNumeros WHERE año = ?", (año,))
        self.cursor.execute("DELETE FROM SecuenciasEstrellas WHERE año = ?", (año,))
        self.conn.commit()
    
    def calcular_secuencias(self):
        año_actual = datetime.now().year
        self.reiniciar_secuencias_anuales(año_actual)

        sorteos_anteriores = {"numeros": set(), "estrellas": set()}
        secuencias_numeros_por_año = defaultdict(lambda: defaultdict(int))
        secuencias_estrellas_por_año = defaultdict(lambda: defaultdict(int))
        
        for sorteo in self.sorteos:
            año_sorteo = pd.to_datetime(sorteo["fecha"]).year
            numeros_actual = set(sorteo["numeros"])
            estrellas_actual = set(sorteo["estrellas"])
            
            # Identifica los números y estrellas que aparecen en sorteos consecutivos
            numeros_consecutivos = sorteos_anteriores["numeros"].intersection(numeros_actual)
            estrellas_consecutivas = sorteos_anteriores["estrellas"].intersection(estrellas_actual)
            
            # Actualiza el conteo de secuencias consecutivas para el año del sorteo
            for numero in numeros_consecutivos:
                secuencias_numeros_por_año[año_sorteo][numero] += 1
            for estrella in estrellas_consecutivas:
                secuencias_estrellas_por_año[año_sorteo][estrella] += 1
            
            # Prepara para el próximo sorteo
            sorteos_anteriores = {"numeros": numeros_actual, "estrellas": estrellas_actual}

        # print(secuencias_numeros_por_año)
        # print(secuencias_estrellas_por_año)
        # quit()
        # Guardar las estadísticas en la base de datos
        self.guardar_secuencias(secuencias_numeros_por_año, 'SecuenciasNumeros')
        self.guardar_secuencias(secuencias_estrellas_por_año, 'SecuenciasEstrellas')

    def guardar_secuencias(self, estadisticas, tabla):
        for año, datos in estadisticas.items():
            for valor, veces in datos.items():
                self.cursor.execute(f'''
                    INSERT INTO {tabla} (año, valor, veces)
                    VALUES (?, ?, ?)
                ''', (año, valor, veces))
        self.conn.commit()
    
    def mostrar_estadisticas(self, valor=None, tipo='numeros'):
        if tipo.lower().startswith('n'):
            tabla = 'SecuenciasNumeros'
        else:
            tabla = 'SecuenciasEstrellas'
        
        try:
            if valor:
                query = f"SELECT año, valor, veces FROM {tabla} WHERE valor = ? ORDER BY año, veces DESC"
                self.cursor.execute(query, (valor,))
            else:
                query = f'SELECT año, valor, veces FROM {tabla} ORDER BY año, veces DESC'
                self.cursor.execute(query)

            resultados = self.cursor.fetchall()
            for año, valor, veces in resultados:
                print(f"Año {año}: Valor {valor} aparece {veces} veces en sorteos consecutivos.")
        except Exception as e:
            print(f"Error al mostrar estadísticas: {e}")

    # def mostrar_estadisticas(self):
    #     print("\nResumen de Secuencias de Números por Año:")
    #     for año in sorted({año for datos in self.secuencias_numeros.values() for año in datos}):
    #         print(f"Año {año}:")
    #         for numero, datos_año in self.secuencias_numeros.items():
    #             if año in datos_año:
    #                 print(f"  Número {numero} se repite {datos_año[año]+1} veces en secuencia")

    #     print("\nResumen de Secuencias de Estrellas por Año:")
    #     for año in sorted({año for datos in self.secuencias_estrellas.values() for año in datos}):
    #         print(f"Año {año}:")
    #         for estrella, datos_año in self.secuencias_estrellas.items():
    #             if año in datos_año:
    #                 print(f"  Estrella {estrella} se repite {datos_año[año]+1} veces en secuencia")
