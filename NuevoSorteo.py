import sqlite3
import json

class NuevoSorteo:
    def __init__(self, db_name):
        self.db_name = f"{db_name}.db"
        self.connect_db()
        self.create_table()

    def connect_db(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS resultados_sorteos
                        (id INTEGER PRIMARY KEY, combinacion TEXT, fecha DATETIME,
                            dia_semana TEXT, id_sorteo TEXT UNIQUE, 
                            anyo TEXT, numero INTEGER,
                            premio_bote REAL, apuestas INTEGER, combinacion_acta TEXT,
                            premios REAL, escrutinio TEXT,
                            num_pares INTEGER, num_impares INTEGER,
                            est_pares INTEGER, est_impares INTEGER,
                            num_bajos INTEGER, num_altos INTEGER,
                            secuencias INTEGER, decenas TEXT, terminaciones TEXT,
                            distribucion TEXT, desviacion_estandar REAL,
                            suma_total INTEGER, suma_total_con_estrellas INTEGER)''')
        self.conn.commit()

    def insert_combinacion(self, sorteo_id, combinacion, fecha, dia_semana, anyo, numero, premio_bote, apuestas, combinacion_acta, premios, escrutinio_json, verbose=False):
        try:
            escrutinio_serializado = json.dumps(escrutinio_json) if not isinstance(escrutinio_json, str) else escrutinio_json
            
            self.cursor.execute('''INSERT INTO resultados_sorteos (fecha, dia_semana, id_sorteo, anyo, numero, premio_bote, apuestas, combinacion, combinacion_acta, premios, escrutinio,
                                    num_pares, num_impares, est_pares, est_impares, num_bajos, num_altos, secuencias, decenas, terminaciones, distribucion, desviacion_estandar, suma_total, suma_total_con_estrellas)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                (fecha, dia_semana, sorteo_id, anyo, numero, premio_bote, apuestas, combinacion, combinacion_acta, premios, escrutinio_serializado, None, None, None, None, None, None, None, None, None, None, None, None, None))
            self.conn.commit()

            if verbose:
                print(f"El sorteo {sorteo_id} con la combinación {combinacion} se ha registrado correctamente en la base de datos")

        except Exception as e:
            print(f"No se ha podido registrar en la base de datos el sorteo {sorteo_id} con fecha {fecha}: {e}")

    # COMPRUEBA SI EXISTE EN LA BASE DE DATOS
    def sorteo_registrado(self, id_sorteo):
        self.cursor.execute("SELECT id FROM resultados_sorteos WHERE id_sorteo = ?", (id_sorteo,))
        return self.cursor.fetchone()

    # CLASIFICACION POR FIGURAS
    def clasificar_por_figura(self, sorteo_id, combinacion, verbose=False):
        numeros, estrellas = combinacion.split('-')[:5], combinacion.split('-')[5:]
        num_pares, num_impares = 0, 0
        est_pares, est_impares = 0, 0

        for numero in numeros:
            if int(numero.strip()) % 2 == 0:
                num_pares += 1
            else:
                num_impares += 1
        for estrella in estrellas:
            if int(estrella.strip()) % 2 == 0:
                est_pares += 1
            else:
                est_impares += 1
        
        if verbose:
            print(f"La combinacion {combinacion} tiene {num_pares} pares y {num_impares} impares.")
            print(f"Las estrellas son {est_pares} pares y {est_impares} impares")
        
        self.actualizar_figuras(sorteo_id, num_pares, num_impares, est_pares, est_impares)

    def actualizar_figuras(self, sorteo_id, num_pares, num_impares, est_pares, est_impares):
        self.cursor.execute('''UPDATE resultados_sorteos
                            SET num_pares = ?, num_impares = ?, est_pares = ?, est_impares = ?
                            WHERE id_sorteo = ?''',
                            (num_pares, num_impares, est_pares, est_impares, sorteo_id))
        self.conn.commit()

    # CLASIFICACION POR RANGOS
    def clasificar_por_rango(self, sorteo_id, combinacion, verbose=False):
        bajos = altos = 0
        numeros = [int(n) for n in combinacion.split('-')[:5]]
        for numero in numeros:
            if numero <= 25:
                bajos += 1
            else:
                altos += 1
        
        if verbose:
            print(f"La combinacion {combinacion} tiene {bajos} números bajos y {altos} números altos.")
        
        self.actualizar_rangos(sorteo_id, bajos, altos)

    def actualizar_rangos(self, sorteo_id, bajos, altos):
        self.cursor.execute('''UPDATE resultados_sorteos
                                SET num_bajos = ?, num_altos = ?
                                WHERE id_sorteo = ?''',
                                (bajos, altos, sorteo_id))
        self.conn.commit()

    # CLASIFICACION POR SECUENCIAS
    def clasificar_por_secuencia(self, sorteo_id, combinacion, verbose=False):
        numeros = sorted([int(n) for n in combinacion.split('-')[:5]])
        secuencias = 0
        for i in range(len(numeros) - 1):
            if numeros[i] + 1 == numeros[i + 1]:
                secuencias += 1
        
        if verbose:
            print(f"La combinacion {combinacion} tiene {secuencias} secuencias numéricas.")

        self.actualizar_secuencias(sorteo_id, secuencias)

    def actualizar_secuencias(self, sorteo_id, secuencias):
        self.cursor.execute('''UPDATE resultados_sorteos
                                SET secuencias = ?
                                WHERE id_sorteo = ?''',
                            (secuencias, sorteo_id))
        self.conn.commit()

    # CLASIFICACIÓN POR DECENAS
    def clasificar_por_decenas(self, sorteo_id, combinacion, verbose=False):
        decenas = {'1ª Decena': 0, '2ª Decena': 0, '3ª Decena': 0, '4ª Decena': 0, '5ª Decena': 0}
        numeros = [int(n) for n in combinacion.split('-')[:5]]
        
        for numero in numeros:
            if 1 <= numero <= 10:
                decenas['1ª Decena'] += 1
            elif 11 <= numero <= 20:
                decenas['2ª Decena'] += 1
            elif 21 <= numero <= 30:
                decenas['3ª Decena'] += 1
            elif 31 <= numero <= 40:
                decenas['4ª Decena'] += 1
            elif 41 <= numero <= 50:
                decenas['5ª Decena'] += 1

        decenas_json = json.dumps(decenas)

        if verbose:
            print(f"La combinación {combinacion} tiene la siguiente distribución por decenas: {decenas_json}")
        
        self.actualizar_decenas(sorteo_id, decenas_json)

    def actualizar_decenas(self, sorteo_id, decenas_json):
        self.cursor.execute('''UPDATE resultados_sorteos
                          SET decenas = ?
                          WHERE id_sorteo = ?''',
                       (decenas_json, sorteo_id))
        self.conn.commit()
    
    # CLASIFICACION POR TERMINACIONES
    def clasificar_por_terminaciones(self, sorteo_id, combinacion, verbose=False):
        terminaciones = {str(i): 0 for i in range(10)}
        numeros = [int(n) for n in combinacion.split('-')[:5]]
        for numero in numeros:
            terminaciones[str(numero % 10)] += 1

        # Serializar el diccionario de terminaciones a JSON para almacenamiento
        terminaciones_json = json.dumps(terminaciones)

        if verbose:
            print(f"La combinacion {combinacion} tiene las siguientes terminaciones: {terminaciones_json}")
        
        self.actualizar_terminaciones(sorteo_id, terminaciones_json)

    def actualizar_terminaciones(self, sorteo_id, terminaciones_json):
        self.cursor.execute('''UPDATE resultados_sorteos
                                SET terminaciones = ?
                                WHERE id_sorteo = ?''',
                            (terminaciones_json, sorteo_id))
        self.conn.commit()

    # CLASIFICACION POR DISTRIBUCIÓN AVANZADA
    def clasificar_por_distribucion_avanzada(self, sorteo_id, combinacion, verbose=False):
        numeros = sorted([int(n) for n in combinacion.split('-')[:5]])
        media = sum(numeros) / len(numeros)
        varianza = sum((x - media) ** 2 for x in numeros) / len(numeros)
        desviacion_estandar = varianza ** 0.5
        
        # Clasificación basada en la desviación estándar
        if desviacion_estandar < 5:
            distribucion = 'Muy uniforme'
        elif 5 <= desviacion_estandar < 10:
            distribucion = 'Moderadamente uniforme'
        else:
            distribucion = 'Variada'
        
        if verbose:
            print(f"La distribución es: {distribucion}. La desviación estandar es: {desviacion_estandar}")
        
        self.actualizar_distribucion_avanzada(sorteo_id, distribucion, desviacion_estandar)

    def actualizar_distribucion_avanzada(self, sorteo_id, distribucion, desviacion_estandar):
        self.cursor.execute('''UPDATE resultados_sorteos
                                SET distribucion = ?, desviacion_estandar = ?
                                WHERE id_sorteo = ?''',
                            (distribucion, desviacion_estandar, sorteo_id))
        self.conn.commit()

    # CLASIFICACION POR SUMA TOTAL
    def clasificar_por_suma_total(self, sorteo_id, combinacion, verbose=False):
        elementos = [int(n) for n in combinacion.split('-')]
        numeros = elementos[:5]
        estrellas = elementos[5:]

        suma_total = sum(numeros)
        suma_total_con_estrellas = sum(elementos)

        if verbose:
            print(f"La suma total de los números del sorteo, excluyendo las estrellas, es de: {suma_total}")
            print(f"La suma total de la combinación, incluyendo estrellas, es de: {suma_total_con_estrellas}")

        self.actualizar_suma_total(sorteo_id, suma_total, suma_total_con_estrellas)

    def actualizar_suma_total(self, sorteo_id, suma_total, suma_total_con_estrellas):
        self.cursor.execute('''UPDATE resultados_sorteos
                                SET suma_total = ?, suma_total_con_estrellas = ?
                                WHERE id_sorteo = ?''',
                            (suma_total, suma_total_con_estrellas, sorteo_id))
        self.conn.commit()


    def close(self):
        self.conn.close()
