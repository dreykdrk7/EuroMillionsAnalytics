import sqlite3
from datetime import datetime

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

    def resumen_jugada_por_combinacion(self, combinacion):
        id_jugada = self.buscar_id_jugada(combinacion)
        if id_jugada is None:
            print("La combinación proporcionada no corresponde a ninguna jugada activa.")
            return
        
        sql = """
        SELECT fecha_sorteo, coste_apuesta, premio_ganado, balance_post_sorteo
        FROM resultados_jugadas
        WHERE id_jugada = ?
        ORDER BY fecha_sorteo
        """
        self.cursor.execute(sql, (id_jugada,))
        resultados = self.cursor.fetchall()
        
        if resultados:
            print(f"Resumen de la jugada: {combinacion}")
            print(f"{'Fecha Sorteo':<15} {'Coste Apuesta':<15} {'Premio Ganado':<15} {'Balance Post Sorteo':<20}")
            for resultado in resultados:
                fecha_sorteo, coste_apuesta, premio_ganado, balance_post_sorteo = resultado
                print(f"{fecha_sorteo:<15} {coste_apuesta:<15.2f} {premio_ganado:<15.2f} {balance_post_sorteo:<20.2f}")
        else:
            print("No se encontraron resultados para la jugada especificada.")

    def cerrar_conexion(self):
        self.conexion.close()

# Ejemplo de uso:
if __name__ == "__main__":

    combinacion = '1 - 4 - 37 - 25 - 49 - 1 - 2 - 7 - 12'
    gestion_jugadas = GestionJugadas(combinacion)
    gestion_jugadas.agregar_jugada_activa("2023-10-01", 10000, "Mi primera jugada", "combinada")

    gestion_jugadas.registrar_resultado(combinacion, "2023-10-02", 2.5, 0)
    print("Balance actual de la jugada:", gestion_jugadas.consultar_balance())
    gestion_jugadas.cerrar_conexion()
