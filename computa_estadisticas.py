import pandas as pd
from classes.stats.ObtenerSorteos import ObtenerSorteos
from classes.stats.EstadisticasFrecuencia import EstadisticasFrecuencia
from classes.stats.EstadisticasSecuencia import EstadisticasSecuencia
from classes.stats.EstadisticasParidad import EstadisticasParidad

if __name__ == '__main__':
    # Asume que ObtenerSorteos tiene un método obtener_todos() que devuelve una lista de sorteos
    año = 2004
    obtener_sorteos = ObtenerSorteos()  # Asegúrate de pasar la ruta correcta de tu base de datos
    sorteos = obtener_sorteos.obtener_todos()  # Aquí puedes especificar desde qué año deseas obtener los sorteos, o quitar el parámetro para obtener todos

    # Asegúrate de que los sorteos obtenidos estén en el formato correcto para la clase MayorFrecuencia
    # Es decir, cada sorteo debería ser un diccionario con 'fecha', 'numeros' y 'estrellas'
    # sorteos_procesados = []
    # for sorteo in sorteos:
    #     sorteos_procesados.append({
    #         'fecha': sorteo['fecha'],
    #         'numeros': sorteo['numeros'],
    #         'estrellas': sorteo['estrellas']
    #     })

    # estadisticas_secuencia = EstadisticasSecuencia(sorteos_procesados)
    # estadisticas_secuencia.calcular_secuencias()
    # estadisticas_secuencia.mostrar_estadisticas(37, 'n')
    
    # gestor_estadisticas = EstadisticasFrecuencia()
    # gestor_estadisticas.procesar_sorteos(sorteos_procesados, año)

    # # Ahora puedes obtener las estadísticas más y menos frecuentes directamente desde la base de datos
    # print("Números más frecuentes globalmente:", gestor_estadisticas.obtener_mas_frecuentes(tabla='FrecuenciaNumeros', X=10))
    # print("Números menos frecuentes globalmente:", gestor_estadisticas.obtener_menos_frecuentes(tabla='FrecuenciaNumeros', X=10))
    # print("Estrellas más frecuentes globalmente:", gestor_estadisticas.obtener_mas_frecuentes(tabla='FrecuenciaEstrellas', X=10))
    # print("Estrellas menos frecuentes globalmente:", gestor_estadisticas.obtener_menos_frecuentes(tabla='FrecuenciaEstrellas', X=10))

    # # Ejemplos de consultas para un año específico
    # print(f"Números más frecuentes en {año}:", gestor_estadisticas.obtener_mas_frecuentes(tabla='FrecuenciaNumeros', año=año, X=10))
    # print(f"Números menos frecuentes en {año}:", gestor_estadisticas.obtener_menos_frecuentes(tabla='FrecuenciaNumeros', año=año, X=10))

    # # Cierra la conexión a la base de datos
    # gestor_estadisticas.cerrar_conexion()

    estadisticas_por_año = obtener_sorteos.calcular_paridad_anual(verbose=False)
    estadisticas_paridad = EstadisticasParidad()

    estadisticas_paridad.insertar_datos_anuales(estadisticas_por_año)
    print(estadisticas_paridad.calcular_figuras(sorteos))
