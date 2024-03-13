import pandas as pd
from collections import defaultdict

class MayorFrecuencia:
    def __init__(self, sorteos):
        self.sorteos = sorteos
        self.estadisticas = defaultdict(lambda: defaultdict(int))

    def procesar_sorteos(self):
        for sorteo in self.sorteos:
            año = pd.to_datetime(sorteo['fecha']).year
            for numero in sorteo['numeros']:
                self.estadisticas[numero][año] += 1
                self.estadisticas[numero]['total'] += 1
            for estrella in sorteo['estrellas']:
                # Usamos un offset para diferenciar estrellas de números, por ejemplo, 100 + estrella
                self.estadisticas[100 + estrella][año] += 1
                self.estadisticas[100 + estrella]['total'] += 1

    def numeros_mas_frecuentes(self, X, año=None):
        # Ordenar por total o por año específico
        key = 'total' if año is None else año
        más_frecuentes = sorted(self.estadisticas.items(), key=lambda x: x[1][key], reverse=True)[:X]
        return {k: v for k, v in más_frecuentes}

    def numeros_menos_frecuentes(self, X, año=None):
        # Filtrar por números que han aparecido al menos una vez
        filtrados = {k: v for k, v in self.estadisticas.items() if v['total'] > 0}
        key = 'total' if año is None else año
        menos_frecuentes = sorted(filtrados.items(), key=lambda x: x[1][key])[:X]
        return {k: v for k, v in menos_frecuentes}


# Ejemplo de uso
if __name__ == '__main__':
    sorteos = [
        {'numeros': [4, 7, 23, 41, 50], 'estrellas': [2, 12], 'fecha': '2024-01-10'},
        {'numeros': [12, 19, 28, 41, 45], 'estrellas': [1, 12], 'fecha': '2024-01-17'},
        # Añadir más sorteos aquí...
    ]

    estadisticas = MayorFrecuencia(sorteos)
    estadisticas.procesar_sorteos()
    print("Números más frecuentes globalmente:", estadisticas.numeros_mas_frecuentes(5))
    print("Números menos frecuentes globalmente:", estadisticas.numeros_menos_frecuentes(5))
    print("Números más frecuentes en 2024:", estadisticas.numeros_mas_frecuentes(5, 2024))
    print("Números menos frecuentes en 2024:", estadisticas.numeros_menos_frecuentes(5, 2024))
