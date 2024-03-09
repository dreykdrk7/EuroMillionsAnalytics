import sqlite3
import pandas as pd

class GestionJugadas:
    def __init__(self, combinacion):
        self.db_path = f'data/jugadas.db'
        self.conexion = sqlite3.connect(self.db_path)
        self.cursor = self.conexion.cursor()
        self.inicializar_tablas()
        self.combinacion = combinacion
        self.buscar_id_jugada(combinacion)

    def inicializar_tablas(self):
        jugadas_activas_sql = """
        CREATE TABLE IF NOT EXISTS jugadas_activas (
            id_jugada INTEGER PRIMARY KEY AUTOINCREMENT,
            combinacion TEXT NOT NULL,
            fecha_inicio DATE NOT NULL,
            balance_inicial REAL DEFAULT 0,
            balance_actual REAL DEFAULT 0,
            descripcion TEXT,
            tipo_jugada TEXT,
            estado TEXT DEFAULT 'activa'
        );
        """
        resultados_jugadas_sql = """
        CREATE TABLE IF NOT EXISTS resultados_jugadas (
            id_resultado INTEGER PRIMARY KEY AUTOINCREMENT,
            id_jugada INTEGER NOT NULL,
            fecha_sorteo DATE NOT NULL,
            coste_apuesta REAL DEFAULT 0,
            premio_ganado REAL DEFAULT 0,
            balance_post_sorteo REAL DEFAULT 0,
            FOREIGN KEY (id_jugada) REFERENCES jugadas_activas (id_jugada)
        );
        """
        self.cursor.execute(jugadas_activas_sql)
        self.cursor.execute(resultados_jugadas_sql)
        self.conexion.commit()

    def agregar_jugada_activa(self, fecha_inicio, balance_inicial, descripcion, tipo_jugada):
        sql = """
        INSERT INTO jugadas_activas (combinacion, fecha_inicio, balance_inicial, balance_actual, descripcion, tipo_jugada, estado)
        VALUES (?, ?, ?, ?, ?, ?, 'activa');
        """
        self.cursor.execute(sql, (self.combinacion, fecha_inicio, balance_inicial, balance_inicial, descripcion, tipo_jugada))
        self.conexion.commit()
        self.id_jugada = self.cursor.lastrowid
    
    def buscar_id_jugada(self, combinacion):
        """Busca el ID de la jugada por su combinación."""
        self.cursor.execute("SELECT id_jugada FROM jugadas_activas WHERE combinacion = ?", (combinacion,))
        resultado = self.cursor.fetchone()
        if resultado:
            self.id_jugada = resultado[0]
        else:
            self.id_jugada = None
    
    def consultar_balance(self):
        self.cursor.execute("SELECT balance_actual FROM jugadas_activas WHERE id_jugada = ?", (self.id_jugada,))
        resultado = self.cursor.fetchone()
        if resultado:
            balance_actual = resultado[0]
        else:
            print("Error al obtener el balance actual de la jugada.")
            return None

        return balance_actual

    def actualizar_balance(self, coste_apuesta, premio_ganado):
        balance_actual = self.consultar_balance()
        if balance_actual is not None:
            nuevo_balance = balance_actual - coste_apuesta + premio_ganado

            self.cursor.execute("UPDATE jugadas_activas SET balance_actual = ? WHERE id_jugada = ?", (nuevo_balance, self.id_jugada))
            self.conexion.commit()
            return nuevo_balance
        else:
            print("No se pudo actualizar el balance de la jugada.")
            return None

    def registrar_resultado(self, combinacion, fecha_sorteo, coste_apuesta, premio_ganado):
        self.buscar_id_jugada(combinacion)
        balance_actualizado = self.actualizar_balance(coste_apuesta, premio_ganado)

        sql = """
        INSERT INTO resultados_jugadas (id_jugada, fecha_sorteo, coste_apuesta, premio_ganado, balance_post_sorteo)
        VALUES (?, ?, ?, ?, ?);
        """

        self.cursor.execute(sql, (self.id_jugada, fecha_sorteo, coste_apuesta, premio_ganado, balance_actualizado))
        self.conexion.commit()

    def obtener_detalles(self):
        sql_jugada = """
        SELECT fecha_inicio, balance_inicial, descripcion, tipo_jugada
        FROM jugadas_activas
        WHERE id_jugada = ?;
        """
        self.cursor.execute(sql_jugada, (self.id_jugada,))
        detalles_jugada = self.cursor.fetchone()
        
        if detalles_jugada:
            fecha_inicio, balance_inicial, descripcion, tipo_jugada = detalles_jugada
            return fecha_inicio, balance_inicial, descripcion, tipo_jugada
        else:
            print("No se encontraron detalles para la jugada especificada.")
            return None, None, None, None
    
    def obtener_lista_resultados(self):
        # Obtener resultados de sorteos para la jugada
        sql_resultados = """
        SELECT fecha_sorteo, coste_apuesta, premio_ganado, balance_post_sorteo
        FROM resultados_jugadas
        WHERE id_jugada = ?
        ORDER BY fecha_sorteo
        """
        self.cursor.execute(sql_resultados, (self.id_jugada,))
        return self.cursor.fetchall()
    
    def generar_sumario(self, combinacion):
        self.buscar_id_jugada(combinacion)
        if self.id_jugada is None:
            print("La combinación proporcionada no corresponde a ninguna jugada activa.")
            return pd.DataFrame()
        
        fecha_inicio, balance_inicial, descripcion, tipo_jugada = self.obtener_detalles()
        resultados = self.obtener_lista_resultados()
        
        if resultados:
            df = pd.DataFrame(resultados, columns=['Fecha Sorteo', 'Coste Apuesta', 'Premio Ganado', 'Balance Post Sorteo'])
            total_invertido = df['Coste Apuesta'].sum()  # Corregido, asegúrate de que el nombre de la columna es correcto.
            total_ganado = df['Premio Ganado'].sum()
            balance_final = df['Balance Post Sorteo'].iloc[-1]
            
            print(f"Descripción de la jugada: {descripcion}")
            print(f"Combinación jugada: {combinacion}")
            print(f"Tipo: {tipo_jugada}")
            print(f"Fecha inicio de la jugada: {fecha_inicio}")
            print(f"Balance inicial: {balance_inicial}")
            print(f"Total invertido: {total_invertido}")
            print(f"Total ganado: {total_ganado}")
            print(f"Balance final: {balance_final}")
            
            return df
        else:
            print("No se encontraron resultados para la jugada especificada.")
            return pd.DataFrame()
    
    def cerrar_conexion(self):
        if self.cursor is not None:
            self.cursor.close()
        if self.conexion is not None:
            self.conexion.close()

# Ejemplo de uso:
if __name__ == "__main__":

    combinacion = '1 - 4 - 37 - 25 - 49 - 1 - 2 - 7 - 12'
    gestion_jugadas = GestionJugadas(combinacion)
    gestion_jugadas.agregar_jugada_activa("2023-10-01", 10000, "Mi primera jugada", "combinada")

    gestion_jugadas.registrar_resultado(combinacion, "2023-10-02", 2.5, 0)
    # print("Balance actual de la jugada:", gestion_jugadas.consultar_balance())

    print(gestion_jugadas.generar_sumario(combinacion))
    gestion_jugadas.cerrar_conexion()
