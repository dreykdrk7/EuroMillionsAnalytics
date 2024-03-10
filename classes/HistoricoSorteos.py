import sqlite3
import json
from classes.ConsultarSorteo import ConsultaSorteo
import pandas as pd

class HistoricoSorteos(ConsultaSorteo):
    def __init__(self, db_path):
        super().__init__(db_path)

    def obtener_resultados_desde(self, fecha_inicio):
        """Obtiene todos los resultados de los sorteos a partir de una fecha dada."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT fecha, id_sorteo, combinacion, premio_bote, escrutinio FROM resultados_sorteos WHERE fecha >= ? ORDER BY fecha ASC"
        cursor.execute(query, (fecha_inicio,))
        
        sorteos = cursor.fetchall()
        self.historico_resultados = []
        for sorteo in sorteos:
            fecha, id_sorteo, combinacion, premio_bote, escrutinio_json = sorteo
            escrutinio = json.loads(escrutinio_json)
            self.historico_resultados.append({
                "fecha": fecha,
                "id_sorteo": id_sorteo,
                "combinacion": combinacion,
                "premio_bote": premio_bote,
                "escrutinio": escrutinio
            })
        
        conn.close()
        return self.historico_resultados
    
    def consultar_historico_premios(self, numeros, estrellas, fecha_inicio, solo_premiados=False):
        self.crear_combinacion_usuario(numeros, estrellas)
        self.obtener_resultados_desde(fecha_inicio)
        
        datos_premios = []

        for sorteo in self.historico_resultados:
            premio_info = self.calcula_premio(self.combinacion_usuario, sorteo['combinacion'], sorteo['premio_bote'], sorteo['escrutinio'])

            if solo_premiados and not premio_info["premiado"]:
                continue
            datos_premios.append({
                "fecha": sorteo['fecha'],
                "id_sorteo": sorteo['id_sorteo'],
                "resultado_premio": premio_info["resultado"]
            })

        df_premios = pd.DataFrame(datos_premios)
        
        return df_premios

if __name__ == '__main__':
    # Uso de ejemplo:
    db_path = 'euromillones_database.db'
    historico = HistoricoSorteos(db_path)
    numeros = [3, 4, 12, 23, 47]
    estrellas = [2, 7]
    fecha_desde = '2024-02-01'

    print(historico.consultar_historico_premios(numeros, estrellas, fecha_desde, True))
    # resultados_desde = historico.obtener_resultados_desde('2024-02-01')
    # for resultado in resultados_desde:
    #     print(resultado)

