import sqlite3
import json

class ConsultaSorteo:
    def __init__(self, db_path):
        self.db_path = db_path

    def crear_combinacion_usuario(self, numeros, estrellas):
        if isinstance(numeros, str) and isinstance(estrellas, str):
            self.combinacion_usuario = f"{numeros} - {estrellas}"
        elif isinstance(numeros, (list, tuple)) and isinstance(estrellas, (list, tuple)):
            numeros_formateados = ' - '.join([f"{n:02d}" for n in sorted(numeros)])
            estrellas_formateadas = ' - '.join([f"{e:02d}" for e in sorted(estrellas)])
            self.combinacion_usuario = f"{numeros_formateados} - {estrellas_formateadas}"
        else:
            raise ValueError("Los tipos de datos para números y estrellas no son válidos.")

        return self.combinacion_usuario

    def contar_aciertos(self, combinacion_usuario, combinacion_sorteo):
        # Dividir las combinaciones en números y estrellas
        partes_usuario = combinacion_usuario.split(' - ')
        numeros_usuario = set(map(int, partes_usuario[:5]))
        estrellas_usuario = set(map(int, partes_usuario[5:]))
        
        partes_sorteo = combinacion_sorteo.split(' - ')
        numeros_sorteo = set(map(int, partes_sorteo[:5]))
        estrellas_sorteo = set(map(int, partes_sorteo[5:]))

        # Contar aciertos
        aciertos_numeros = len(numeros_usuario.intersection(numeros_sorteo))
        aciertos_estrellas = len(estrellas_usuario.intersection(estrellas_sorteo))

        return aciertos_numeros, aciertos_estrellas


    def consulta_premio(self, fecha_sorteo, numeros, estrellas):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Preparar los números y estrellas para la consulta
        combinacion_usuario = self.crear_combinacion_usuario(numeros, estrellas)
        cursor.execute("SELECT id_sorteo, combinacion, escrutinio FROM resultados_sorteos WHERE fecha = ?", (fecha_sorteo,))
        sorteo = cursor.fetchone()

        if sorteo:
            _, combinacion_sorteo, escrutinio_json = sorteo
            print(combinacion_sorteo)

            aciertos_numeros, aciertos_estrellas = self.contar_aciertos(combinacion_usuario, combinacion_sorteo)

            escrutinio = json.loads(escrutinio_json)

            for categoria in escrutinio:
                try:
                    tipo_split = categoria["tipo"].split()
                    aciertos_necesarios_num = int(tipo_split[1])
                    aciertos_necesarios_est = int(tipo_split[3])
                except ValueError as e:
                    print(f"Error al procesar la categoría {categoria['tipo']}: {e}")
                    continue

                if aciertos_numeros == aciertos_necesarios_num and aciertos_estrellas == aciertos_necesarios_est:
                    print(f"Categoría: {categoria['categoria']}, Premio: {categoria['premio']}, Ganadores: {categoria['ganadores']}, Ganadores en EU: {categoria['ganadores_eu']}")
                    break
            else:
                print("No hay premio para esta combinación.")
        else:
            print("No se encontró el sorteo para la fecha proporcionada.")

        conn.close()

if __name__ == '__main__':
    # Uso de ejemplo
    db_path = 'euromillones_database.db'
    consulta = ConsultaSorteo(db_path)
    consulta.consulta_premio('2024-03-01', [1, 7, 20, 4, 5], [4, 3])
