import argparse
import requests
import json
from datetime import datetime
from time import sleep
from dateutil.relativedelta import relativedelta
from classes.NuevoSorteo import NuevoSorteo


parser = argparse.ArgumentParser(description='Recopila y clasifica datos de sorteos de Euromillones.')
parser.add_argument('--historico', action='store_true', help='Recopilar todo el histórico de sorteos desde una fecha específica.')
parser.add_argument('--inicio', type=str, help='Fecha de inicio para recopilar el histórico en formato YYYY-MM-DD. Solo funciona si --historico está presente.')
parser.add_argument('--periodo', type=str, choices=['semana', 'mes'], default='semana', help='Especifica el período para los últimos sorteos: "semana" o "mes".')
args = parser.parse_args()
fecha_fin = datetime.now()


if __name__ == '__main__':

    if args.historico:

        if args.inicio:
            fecha_inicio = datetime.strptime(args.inicio, '%Y-%m-%d')
        else:
            fecha_inicio = datetime.strptime('2004-01-01', '%Y-%m-%d')
    else:

        if args.periodo == 'semana':
            fecha_inicio = fecha_fin - relativedelta(days=8)
        elif args.periodo == 'mes':
            fecha_inicio = fecha_fin - relativedelta(days=32)

    db = NuevoSorteo('euromillones_database')

    # URL de la API
    url = 'https://www.loteriasyapuestas.es/servicios/buscadorSorteos'

    while fecha_inicio < fecha_fin:
        fecha_fin_ciclo = fecha_inicio + relativedelta(months=3)
        if fecha_fin_ciclo > fecha_fin:
            fecha_fin_ciclo = fecha_fin

        fecha_inicio_str = fecha_inicio.strftime('%Y%m%d')
        fecha_fin_ciclo_str = fecha_fin_ciclo.strftime('%Y%m%d')

        params = {
            'game_id': 'EMIL',
            'celebrados': 'true',
            'fechaInicioInclusiva': fecha_inicio_str,
            'fechaFinInclusiva': fecha_fin_ciclo_str
        }

        response = requests.get(url, params=params)

        print(f"Buscando sorteos entre las fechas {fecha_inicio} y {fecha_fin_ciclo}")
        if response.status_code == 200:
            try:
                data = response.json()
                if not isinstance(data, list):
                    print("Respuesta de la API no es un objeto JSON esperado.")
                    continue
            except ValueError:
                print("Error: Respuesta de la API no es un JSON válido.")
                continue


            fecha_inicio = fecha_fin_ciclo + relativedelta(days=1)
            print("Descansando unos segundos antes de la siguiente petición.....")
            sleep(5)

            for sorteo in data:

                if "id_sorteo" not in sorteo and "fecha_sorteo" not in sorteo:
                    print("El sorteo no contiene todas las claves esperadas.")
                    continue

                try:
                    esta_registrado = db.sorteo_registrado(sorteo["id_sorteo"])

                    if esta_registrado:
                        print(f"El sorteo {sorteo['id_sorteo']} ya está registrado en la base de datos")
                        continue
                except TypeError:
                    print(f"Error: el objeto 'sorteo' no tiene el formato esperado. ID Sorteo: {sorteo.get('id_sorteo', 'Desconocido')}")
                    print(sorteo)
                    continue
                except Exception as e:
                    print(f"Error de tipo {type(e).__name__} al procesar el sorteo {sorteo.get('id_sorteo', 'Desconocido')}: {e}")
                    continue

                try:
                    # print(json.dumps(sorteo, indent=4))
                    # break
                    # atributos_deseados = [
                    #     "fecha_sorteo", "dia_semana", "id_sorteo",
                    #     "anyo", "numero", "premio_bote", "apuestas",
                    #     "recaudacion", "combinacion", "combinacion_acta",
                    #     "premios", "fondo_bote", "escrutinio"
                    # ]

                    try:
                        fecha_sorteo = datetime.strptime(sorteo["fecha_sorteo"], "%Y-%m-%d %H:%M:%S").date()
                    except ValueError:
                        fecha_sorteo = datetime.strptime("2010-01-01 22:00", "%Y-%m-%d %H:%M").date()
                
                    db.insert_combinacion(sorteo["id_sorteo"], sorteo["combinacion"].strip(), str(fecha_sorteo), 
                                        sorteo.get("dia_semana", ""), sorteo.get("anyo", ""), 
                                        sorteo.get("numero", 0), sorteo.get("premio_bote", ""), 
                                        sorteo.get("apuestas", ""), sorteo.get("combinacion_acta", ""), 
                                        sorteo.get("premios", ""), sorteo.get("escrutinio", []), verbose=True)

                    # Clasificación por figuras
                    db.clasificar_por_figura(sorteo['id_sorteo'], sorteo["combinacion"], True)

                    # Clasificación por rangos
                    db.clasificar_por_rango(sorteo['id_sorteo'], sorteo["combinacion"], True)

                    # Clasificación por secuencias
                    db.clasificar_por_secuencia(sorteo['id_sorteo'], sorteo["combinacion"], True)

                    # Clasificación por terminaciones
                    db.clasificar_por_terminaciones(sorteo['id_sorteo'], sorteo["combinacion"], True)

                    # Clasificación por distribución avanzada
                    db.clasificar_por_distribucion_avanzada(sorteo['id_sorteo'], sorteo["combinacion"], True)

                    # Clasificación por suma total
                    db.clasificar_por_suma_total(sorteo['id_sorteo'], sorteo["combinacion"], True)

                except Exception as e:
                    print(f"Ocurrió un error al procesar el sorteo {sorteo['id_sorteo']} con fecha {sorteo['fecha_sorteo']}: {e}")
                    continue

        else:
            print(f"Error al hacer la petición: {response.status_code}")

        

    db.close()

