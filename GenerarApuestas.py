import random

class GenerarApuestaAleatoria:
    def __init__(self):
        self.numeros, self.estrellas = self.generar_apuesta()

    def generar_apuesta(self):
        total_numeros = random.randint(5, 10)  # Total de números entre 5 y 10
        total_estrellas = random.randint(2, 5)  # Total de estrellas entre 2 y 5

        numeros = self._generar_numeros_aleatorios(total_numeros, 1, 50)
        estrellas = self._generar_numeros_aleatorios(total_estrellas, 1, 12)
        return numeros, estrellas

    def _generar_numeros_aleatorios(self, total, inicio, fin):
        numeros_aleatorios = []
        while len(numeros_aleatorios) < total:
            numero = random.randint(inicio, fin)
            if numero not in numeros_aleatorios:
                numeros_aleatorios.append(numero)
        return sorted(numeros_aleatorios)

if __name__ == "__main__":
    nueva_apuesta = GenerarApuestaAleatoria()
    print("Números aleatorios:", nueva_apuesta.numeros)
    print("Estrellas aleatorias:", nueva_apuesta.estrellas)

