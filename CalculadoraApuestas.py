
class CalculadoraApuestas:
    def __init__(self):
        # Precio base por apuesta
        self.precio_base = 2.5
        
        # Tabla de apuestas múltiples (números, estrellas) -> cantidad de apuestas
        self.tabla_apuestas = {
            (5, 2): 1,  # Una combinación estándar de 5 números y 2 estrellas equivale a 1 apuesta
            (5, 3): 3,
            (5, 4): 6,
            (5, 5): 10,
            (6, 2): 6,
            (6, 3): 18,
            (6, 4): 36,
            (6, 5): 60,
            (7, 2): 21,
            (7, 3): 63,
            (7, 4): 126,
            (7, 5): 210,
            (8, 2): 56,
            (8, 3): 168,
            (8, 4): 336,
            (8, 5): 560,
            (9, 2): 126,
            (9, 3): 378,
            (9, 4): 756,
            (9, 5): 1260,
            (10, 2): 252,
            (10, 3): 756,
            (10, 4): 1512,
            (10, 5): 2520
        }
    
    def calcular_precio(self, numeros, estrellas):
        # Clave para buscar en la tabla de apuestas
        clave = (numeros, estrellas)
        if clave in self.tabla_apuestas:
            cantidad_apuestas = self.tabla_apuestas[clave]
            precio_total = cantidad_apuestas * self.precio_base
            return precio_total
        else:
            return "Combinación no válida"

if __name__ == '__main__':
    calculadora = CalculadoraApuestas()
    precio = calculadora.calcular_precio(5, 2)
    print(f"El precio de la apuesta estándar es: {precio} euros")

    precio = calculadora.calcular_precio(5, 3)
    print(f"El precio de la apuesta de 5 números y 3 estrellas es: {precio} euros")

    precio = calculadora.calcular_precio(6, 3)
    print(f"El precio de la apuesta de 6 números y 3 estrellas es: {precio} euros")

