Cosas que hacer para los euromillions:

1.- Guardar resultados de los sorteos en database
    - [ ] Terminar la clase
2.- [ ] Generar un script que genere una apuesta, recoja los resultados historicos, guarde el tests en la base de datos
3.- [ ] Usar multiprocesos para generar apuestas simultaneamente
    - [ ] Comprobar que no falle el acceso simultaneo desde diferentes subprocesoos a la base de datos
4.- [ ] Probar a entrenar una IA con todos los recursos que tenemos disponibles
5.- [ ]  Estadisticas
    - [ ] Basarse en este ejemplo: 
    https://www.loteriasyapuestas.es/portal/site/loterias/template.PAGE/lnacStats/;jsessionid=3E1B77652DC08F43DEDD01CE441797A2.appdelivery2?vgnextoid=5afb402b4cb3b310VgnVCM100000c7ab1eacRCRD&lang=es_ES&javax.portlet.sync=69b98b821121ceffb05900f60dbab1ca&javax.portlet.tpst=d3928e547d24c5c39f6de2504cbae1ca&javax.portlet.prp_d3928e547d24c5c39f6de2504cbae1ca=action%3DeuromillonesStats%26type%3D6&javax.portlet.begCacheTok=com.vignette.cachetoken&javax.portlet.endCacheTok=com.vignette.cachetoken
    - [ ] Estadisticas de premios por numero <--- Esto podria ser interesante
    - [ ] Numeros y estrellas que menos aparecen




2.- Combinadas : https://blog.serviapuestas.es/apuestas-multiples-euromillones-informacion/
    -- Mas complementacion para las combinadas
    Para estadísticas específicas de números y estrellas respecto a la apuesta combinada y términos de rentabilidad, puedes considerar incluir:

    Probabilidad de Aparición: Calcular la probabilidad real de aparición de cada número y estrella dentro de las combinaciones premiadas y compararla con la probabilidad teórica. Esto te dará una visión de qué tan "afortunados" han sido ciertos números o estrellas en relación con su esperanza matemática.

    Rendimiento Relativo: Evaluar el rendimiento relativo de incluir ciertos números o estrellas en una apuesta. Esto se puede hacer calculando cuánto habría contribuido cada número o estrella a la rentabilidad total de las apuestas si se hubieran elegido en cada sorteo.

    Contribución al Premio: Determinar cuánto ha contribuido cada número o estrella al total de premios obtenidos. Esto implica analizar las combinaciones premiadas y sumar los premios donde aparece cada número o estrella.

    Índice de Rentabilidad: Crear un índice que combine la frecuencia de aparición de cada número o estrella con la cantidad de premios que han contribuido a obtener. Este índice podría darte una idea más clara de qué números o estrellas son más "valiosos" para incluir en una apuesta combinada.

Para implementar estas ideas, puedes comenzar calculando la probabilidad de aparición y luego avanzar hacia métricas más complejas. Aquí tienes un ejemplo de cómo podrías calcular la probabilidad de aparición real y compararla con la probabilidad teórica:

python

def calcular_probabilidad_aparicion(frecuencias, total_sorteos, total_elementos):
    """
    Calcula la probabilidad de aparición de cada elemento (número o estrella) y la compara con la probabilidad teórica.
    
    Args:
        frecuencias (dict): Diccionario con las frecuencias de aparición de cada elemento.
        total_sorteos (int): Número total de sorteos analizados.
        total_elementos (int): Número total de elementos posibles (números o estrellas en el sorteo).
    
    Returns:
        pd.DataFrame: DataFrame con las frecuencias, probabilidades reales y teóricas.
    """
    df = pd.DataFrame.from_dict(frecuencias, orient='index', columns=['Frecuencia'])
    df['Probabilidad Real (%)'] = (df['Frecuencia'] / total_sorteos) * 100
    df['Probabilidad Teórica (%)'] = (1 / total_elementos) * 100
    df['Desviación de la Probabilidad (%)'] = df['Probabilidad Real (%)'] - df['Probabilidad Teórica (%)']
    df.sort_values(by='Probabilidad Real (%)', ascending=False, inplace=True)
    
    return df

Este método te proporcionará un marco inicial para analizar cómo cada número o estrella se desempeña en relación con lo que estadísticamente se esperaría en un sorteo perfectamente aleatorio. Desde aquí, puedes avanzar hacia el cálculo del rendimiento relativo y la contribución al premio, lo que requerirá un análisis más detallado de las combinaciones premiadas y los premios asociados a cada una.



3.-
