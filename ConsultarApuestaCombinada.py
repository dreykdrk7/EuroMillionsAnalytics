from HistoricoSorteos import HistoricoSorteos
import itertools
from itertools import combinations
import pandas as pd

class ConsultarApuestaCombinada(HistoricoSorteos):
    def __init__(self, db_path):
        super().__init__(db_path)

    def numero_total_sorteos_jugados(self, fecha_inicio):
        if len(self.historico_resultados) < 1:
            self.obtener_resultados_desde(fecha_inicio)

        return len(self.historico_resultados)
    
    def numero_de_apuestas_por_sorteo(self):
        return len(self.combinaciones_usuario)
    
    def generar_combinaciones_apuesta(self, numeros, estrellas):
        """Genera todas las combinaciones válidas para una apuesta de Euromillones."""
        combinaciones_numeros = list(combinations(numeros, 5))
        combinaciones_estrellas = list(combinations(estrellas, 2))

        # Producto cartesiano para generar todas las combinaciones de números y estrellas
        todas_combinaciones = list(itertools.product(combinaciones_numeros, combinaciones_estrellas))

        # Formatear las combinaciones para que coincidan con el formato de entrada esperado por contar_aciertos
        combinaciones_formateadas = [
            (' - '.join(map(lambda x: f"{x:02d}", combo_num)) + " - " + ' - '.join(map(lambda x: f"{x:02d}", combo_est)))
            for combo_num, combo_est in todas_combinaciones
        ]

        return combinaciones_formateadas

    def consultar_aciertos_combinados(self, numeros, estrellas, fecha_inicio):
        """Consulta los aciertos para apuestas combinadas desde una fecha dada."""
        self.obtener_resultados_desde(fecha_inicio)
        self.combinaciones_usuario = self.generar_combinaciones_apuesta(numeros, estrellas)

        resultados = []

        for sorteo in self.historico_resultados:
            combinacion_sorteo = sorteo['combinacion']
            premio_bote = sorteo['premio_bote']
            escrutinio = sorteo['escrutinio']

            for combinacion_actual in self.combinaciones_usuario:
                resultado_premio = self.calcula_premio(combinacion_actual, combinacion_sorteo, premio_bote, escrutinio)
                if resultado_premio["premiado"]:
                    # Agregar resultados premiados a la lista de resultados
                    resultados.append({
                        "fecha": sorteo['fecha'],
                        "combinacion_usuario": combinacion_actual,
                        "resultado_premio": resultado_premio['resultado']
                    })

        return resultados
    
    def resumen_frecuencias(self, resultados_premiados):
        frecuencias_numeros = {}
        frecuencias_estrellas = {}

        for resultado in resultados_premiados:
            # Asumiendo que 'combinacion_usuario' contiene los números y estrellas
            combinacion_usuario = resultado['combinacion_usuario'].split(' - ')
            numeros = combinacion_usuario[:5]
            estrellas = combinacion_usuario[5:]

            for numero in numeros:
                frecuencias_numeros[numero] = frecuencias_numeros.get(numero, 0) + 1

            for estrella in estrellas:
                frecuencias_estrellas[estrella] = frecuencias_estrellas.get(estrella, 0) + 1

        return frecuencias_numeros, frecuencias_estrellas
    
    def distribucion_premios_por_categoria(self, resultados_premiados):
        self.distribucion_premios = {}

        for resultado in resultados_premiados:
            categoria_premio = resultado.get('resultado_premio')
            if "Categoría" in categoria_premio:
                # Asegúrate de que la categoría se maneje como entero
                categoria = int(categoria_premio.split(",")[0].split(":")[1].strip())
                premio = float(categoria_premio.split(",")[1].split(":")[1].strip())

                if categoria not in self.distribucion_premios:
                    self.distribucion_premios[categoria] = {'conteo': 0, 'suma_premios': 0.0}

                self.distribucion_premios[categoria]['conteo'] += 1
                self.distribucion_premios[categoria]['suma_premios'] += premio

        return self.crear_dataframe_premios(self.distribucion_premios)

    def crear_dataframe_premios(self, distribucion_premios):
        categorias = []
        conteos = []
        sumas_premios = []

        for categoria, info in sorted(distribucion_premios.items()):
            categorias.append(categoria)
            conteos.append(info['conteo'])
            sumas_premios.append(info['suma_premios'])

        categorias.append('Total')
        conteos.append(sum(conteos))
        sumas_premios.append(sum(sumas_premios))

        dataframe = pd.DataFrame({
            'Categoría': categorias,
            'Premios ganados': conteos,
            'Suma total de premios': sumas_premios
        }).set_index('Categoría')

        return dataframe
    
    def analizar_rentabilidad_por_categoria(self, costo_apuesta):
        premios_por_categoria = self.distribucion_premios
        numero_apuestas = sum(info['conteo'] for info in premios_por_categoria.values())

        df_premios = pd.DataFrame.from_dict(premios_por_categoria, orient='index')
        df_premios.reset_index(inplace=True)
        df_premios.rename(columns={'index': 'Categoría', 'conteo': 'Premios ganados', 'suma_premios': 'Suma total de premios'}, inplace=True)
        df_premios['Categoría'] = df_premios['Categoría'].astype(int)
        
        # Calcula el coste total de las apuestas
        coste_total_apuestas = numero_apuestas * costo_apuesta
        
        # Calcula la rentabilidad por categoría
        df_premios['Coste Total'] = coste_total_apuestas
        df_premios['Rentabilidad (%)'] = (df_premios['Suma total de premios'] - coste_total_apuestas) / coste_total_apuestas * 100

        # Ordenar el DataFrame por categoría
        df_premios.sort_values(by='Categoría', inplace=True)

        df_premios_con_totales = self.agregar_totales_a_rentabilidad(df_premios)
        return df_premios_con_totales

    def agregar_totales_a_rentabilidad(self, df_rentabilidad):
        total_premios_ganados = df_rentabilidad['Premios ganados'].sum()
        total_suma_premios = df_rentabilidad['Suma total de premios'].sum()
        total_costes = df_rentabilidad['Coste Total'].sum()

        nueva_fila = pd.DataFrame({
            'Categoría': ['Total'],
            'Premios ganados': [total_premios_ganados],
            'Suma total de premios': [total_suma_premios],
            'Coste Total': [total_costes],
            'Rentabilidad (%)': [(total_suma_premios - total_costes) / total_costes * 100]
        })

        df_con_totales = pd.concat([df_rentabilidad, nueva_fila], ignore_index=True)
        return df_con_totales
    
    def ampliar_analisis(self, resultados_premiados, numero_sorteos, jugadas_por_sorteo):
        # Suponiendo que `resultados_premiados` es una lista de diccionarios como el mostrado
        # `numero_sorteos` es el número de sorteos analizados
        # `jugadas_por_sorteo` es el número de combinaciones jugadas por sorteo
        
        combinaciones_totales = numero_sorteos * jugadas_por_sorteo
        premio_total = 0
        combinaciones_premiadas = 0
        
        frecuencias_numeros = {}
        frecuencias_estrellas = {}
        
        for resultado in resultados_premiados:
            combinacion = resultado['combinacion_usuario'].split(' - ')
            numeros = map(int, combinacion[:5])
            estrellas = map(int, combinacion[5:])
            
            if "Categoría" in resultado['resultado_premio']:
                premio_info = resultado['resultado_premio'].split(',')
                premio = float(premio_info[1].split(':')[1].strip())
                premio_total += premio
                combinaciones_premiadas += 1
            
            for numero in numeros:
                frecuencias_numeros[numero] = frecuencias_numeros.get(numero, 0) + 1
            for estrella in estrellas:
                frecuencias_estrellas[estrella] = frecuencias_estrellas.get(estrella, 0) + 1
        
        # Calcular porcentajes de aparición y K de rentabilidad
        for numero in frecuencias_numeros:
            frecuencias_numeros[numero] = {
                "frecuencia": frecuencias_numeros[numero],
                "porcentaje": (frecuencias_numeros[numero] / combinaciones_totales) * 100
            }
        for estrella in frecuencias_estrellas:
            frecuencias_estrellas[estrella] = {
                "frecuencia": frecuencias_estrellas[estrella],
                "porcentaje": (frecuencias_estrellas[estrella] / combinaciones_totales) * 100
            }
        
        k_rentabilidad = premio_total / combinaciones_premiadas if combinaciones_premiadas else 0
        
        return frecuencias_numeros, frecuencias_estrellas, k_rentabilidad

    def convertir_a_dataframe(self, diccionario_frecuencias, nombre_indice):
        df = pd.DataFrame.from_dict(diccionario_frecuencias, orient='index')
        df.index.name = nombre_indice
        df.reset_index(inplace=True)
        df.rename(columns={'frecuencia': 'Frecuencia', 'porcentaje': 'Porcentaje (%)'}, inplace=True)
        return df
    
    def generar_sumario(self, numeros_apuesta, estrellas_apuesta, fecha_inicio):
        resultados = self.consultar_aciertos_combinados(numeros_apuesta, estrellas_apuesta, fecha_inicio)
        distribucion = self.distribucion_premios_por_categoria(resultados)
        total_sorteos_jugados = self.numero_total_sorteos_jugados(fecha_inicio)
        numero_apuestas_por_sorteo = self.numero_de_apuestas_por_sorteo()
        costo_apuesta = 2.5  # Asume un costo constante por apuesta.
        df_rentabilidad_categoria = self.analizar_rentabilidad_por_categoria(costo_apuesta)

        frecuencias_numeros, frecuencias_estrellas, k_rentabilidad = self.ampliar_analisis(resultados, total_sorteos_jugados, numero_apuestas_por_sorteo)
        frecuencias_numeros_df = self.convertir_a_dataframe(frecuencias_numeros, 'Número')
        frecuencias_estrellas_df = self.convertir_a_dataframe(frecuencias_estrellas, 'Estrella')

        # Imprimir sumario
        # print("Distribución de premios por categoría:")
        # print(distribucion.to_string())

        print(f"Se juegan: {numero_apuestas_por_sorteo} apuestas por sorteo. Con un coste de {numero_apuestas_por_sorteo * costo_apuesta} €.")
        print(f"Número de sorteos desde la fecha {fecha_inicio}: {total_sorteos_jugados}")
        print(f"El coste de las apuestas ha sido de: {numero_apuestas_por_sorteo * costo_apuesta * total_sorteos_jugados} €.")
        
        # Imprime la rentabilidad por categoría
        print("\nRentabilidad por categoría de premio:")
        print(df_rentabilidad_categoria.to_string(index=False))

        print("\nFrecuencias de Números en premios:")
        print(frecuencias_numeros_df.to_string(index=False), "\n")
        
        print("Frecuencias de Estrellas en premios:")
        print(frecuencias_estrellas_df.to_string(index=False), "\n")

        print(f"Coeficiente de Rentabilidad (K): {k_rentabilidad:.2f}")


    # def simular_estrategia(self, numeros_frecuentes, estrellas_frecuentes, fecha_inicio, num_simulaciones=1000):
    #     """Simula apuestas basadas en los números y estrellas más frecuentes."""
    #     resultados_simulacion = []
    #     for _ in range(num_simulaciones):
    #         # Selecciona al azar 5 números y 2 estrellas de los conjuntos de frecuentes
    #         numeros_seleccionados = random.sample(numeros_frecuentes, 5)
    #         estrellas_seleccionadas = random.sample(estrellas_frecuentes, 2)
            
    #         # Realiza una consulta simulada (o usa datos históricos para evaluar esta combinación)
    #         resultados = self.consultar_aciertos_combinados(numeros_seleccionados, estrellas_seleccionadas, fecha_inicio)
    #         resultados_simulacion.append(resultados)
        
    #     # Análisis de los resultados de la simulación
    #     # Por ejemplo, contar el número de simulaciones que resultaron en al menos un premio
    #     premios_ganados = sum(1 for resultado in resultados_simulacion if resultado['es_premiado'])
    #     print(f"Premios ganados en {num_simulaciones} simulaciones: {premios_ganados}")


if __name__ == "__main__":
    db_path = "euromillones_database.db"
    consulta_combinada = ConsultarApuestaCombinada(db_path)
    
    # Definir los números y estrellas para la apuesta combinada
    numeros_apuesta = [4, 7, 19, 20, 34, 47, 49]  # Ejemplo de 6 números para una apuesta combinada
    estrellas_apuesta = [4, 1, 3]  # Ejemplo de 3 estrellas para una apuesta combinada
    
    # Fecha desde la cual se desea comenzar la consulta de sorteos
    fecha_inicio = "2024-02-01"
    
    consulta_combinada.generar_sumario(numeros_apuesta, estrellas_apuesta, fecha_inicio)
    quit()

    ## SI POR LO QUE SEA, NECESITAS CALCULAR UNICAMENTE LAS FRECUENCIAS CON LAS QUE SE REPITEN LOS NUMEROS Y LAS ESTRELLAS
    for categoria, info in distribucion.items():
        print(f"Categoría {categoria}: Premios ganados: {info['conteo']}, Suma total de premios: {info['suma_premios']}")
    
    frecuencias_numeros, frecuencias_estrellas = consulta_combinada.resumen_frecuencias(resultados)

    print("Frecuencias de Números en combinaciones premiadas:")
    for numero, frecuencia in frecuencias_numeros.items():
        print(f"Número {numero}: {frecuencia} veces")

    print("\nFrecuencias de Estrellas en combinaciones premiadas:")
    for estrella, frecuencia in frecuencias_estrellas.items():
        print(f"Estrella {estrella}: {frecuencia} veces")
    
