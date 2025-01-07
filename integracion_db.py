import sqlite3

# Conectar a la base de datos SQLite
conn = sqlite3.connect('euromillones_database.db')

import pandas as pd

query = "SELECT * FROM resultados_sorteos"
df = pd.read_sql_query(query, conn)

# Asegúrate de cerrar la conexión una vez que hayas terminado de leer los datos
conn.close()

# Ejemplo de preprocesamiento: Normalizar columnas numéricas
from sklearn.preprocessing import MinMaxScaler

scaler = MinMaxScaler()
df['apuestas_normalizadas'] = scaler.fit_transform(df[['apuestas']])

# Suponiendo que 'combinacion' es lo que quieres predecir
X = df.drop('combinacion', axis=1)
y = df['combinacion']

# Aquí podrías necesitar más pasos de preprocesamiento, como convertir 'y' en una forma adecuada para tu red neuronal

