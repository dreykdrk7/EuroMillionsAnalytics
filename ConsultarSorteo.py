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
        cursor.execute("SELECT id_sorteo, combinacion, premio_bote,escrutinio FROM resultados_sorteos WHERE fecha = ?", (fecha_sorteo,))
        sorteo = cursor.fetchone()

        if sorteo:
            _, combinacion_sorteo, premio_bote, escrutinio_json = sorteo
            escrutinio = json.loads(escrutinio_json)

            print(f"La combinación del usuario es: {combinacion_usuario}")
            print(f"La combinación ganadora del sorteo es: {combinacion_sorteo}")
            aciertos_numeros, aciertos_estrellas = self.contar_aciertos(combinacion_usuario, combinacion_sorteo)
            print(f"Números acertados: {aciertos_numeros} - Estrellas acertadas: {aciertos_estrellas}")

            # Verificamos si hay acertantes para la categoría 1
            categoria_1 = next((cat for cat in escrutinio if cat['categoria'] == 1), None)
            if categoria_1 and int(categoria_1['ganadores']) == 0 and aciertos_numeros == 5 and aciertos_estrellas == 2:
                print(f"No hay acertantes para la categoría 1. Premio Bote: {premio_bote}")
            else:
                for categoria in escrutinio:
                    tipo_split = categoria["tipo"].split()
                    aciertos_necesarios_num = int(tipo_split[1])
                    aciertos_necesarios_est = int(tipo_split[3])

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
    consulta.consulta_premio('2024-03-01', [4, 7, 19, 20, 34], [4, 2])
