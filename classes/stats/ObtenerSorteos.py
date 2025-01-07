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
            cursor.execute("""
                SELECT fecha, combinacion, num_pares, num_impares, est_pares, est_impares,
                num_bajos, num_altos, secuencias, terminaciones, distribucion,
                desviacion_estandar, suma_total, suma_total_con_estrellas 
                FROM resultados_sorteos
            """)
            sorteos = cursor.fetchall()

        return self._procesar_sorteos(sorteos)

    def obtener_sorteos_año(self, año):
        fecha_inicio = f"{año}-01-01"
        fecha_fin = f"{año}-12-31"
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT fecha, combinacion, num_pares, num_impares, est_pares, est_impares,
                num_bajos, num_altos, secuencias, terminaciones, distribucion,
                desviacion_estandar, suma_total, suma_total_con_estrellas 
                FROM resultados_sorteos WHERE fecha BETWEEN ? AND ?
            """, (fecha_inicio, fecha_fin))
            sorteos = cursor.fetchall()

        return self._procesar_sorteos(sorteos)

    def _procesar_sorteos(self, sorteos):
        resultados_sorteos = []
        for sorteo in sorteos:
            (fecha, combinacion_sorteo, num_pares, num_impares, est_pares, est_impares,
             num_bajos, num_altos, secuencias, terminaciones, distribucion,
             desviacion_estandar, suma_total, suma_total_con_estrellas) = sorteo
             
            numeros, estrellas = self._procesar_combinacion(combinacion_sorteo)
            terminaciones = json.loads(terminaciones)
            
            resultados_sorteos.append({
                'fecha': fecha,
                'numeros': numeros,
                'estrellas': estrellas,
                'num_pares': num_pares,
                'num_impares': num_impares,
                'est_pares': est_pares,
                'est_impares': est_impares,
                'num_bajos': num_bajos,
                'num_altos': num_altos,
                'secuencias': secuencias,
                'terminaciones': terminaciones,
                'distribucion': distribucion,
                'desviacion_estandar': desviacion_estandar,
                'suma_total': suma_total,
                'suma_total_con_estrellas': suma_total_con_estrellas
            })
        return resultados_sorteos
    
    def calcular_paridad_anual(self, verbose=False):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT strftime('%Y', fecha) AS year, SUM(num_pares), SUM(num_impares), SUM(est_pares), SUM(est_impares)
                FROM resultados_sorteos
                GROUP BY year
            """)
            resultados = cursor.fetchall()

        if verbose:
            for year, sum_num_pares, sum_num_impares, sum_est_pares, sum_est_impares in resultados:
                print(f"Año {year}: Números Pares {sum_num_pares}, Números Impares {sum_num_impares}, "
                    f"Estrellas Pares {sum_est_pares}, Estrellas Impares {sum_est_impares}")
        
        return resultados


if __name__ == '__main__':
    estadisticas = ObtenerSorteos()
    sorteos = estadisticas.obtener_sorteos_año(2020)
    print(sorteos)

