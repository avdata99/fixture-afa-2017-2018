'''
Analizar todos los datos y grabar las conclusiones
'''
import csv
import sys

clubes = {}  # diccionario de los 28 equipos de primera división
path_datos = '../datos'
clubes_fechas = {}  # para guardar por separado sus fechas

# iterar la tabla de promedios actuales para listar los equipos y guardar estos datos
headers = ['Club','2015','2016','2016/2017','2017/2018','puntos','PJ']
with open('{}/promedios-actuales.csv'.format(path_datos), newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        nombre_afa = row['Nombre AFA'].strip()
        pts_2015 = int(row['2015'])
        pts_2016 =int(row['2016'])
        # hay equipos que no jugaron la temporada pasada, ese cero ensucia, 43 es el promedio de puntos de todos los equipos
        pts_2016_2017 = int(row['2016/2017'])
        pts_2017_2018 = int(row['2017/2018'])
        pts_acumulado = int(row['puntos'])
        partidos_jugados = int(row['PJ'])

        # test de los datos
        if pts_acumulado != pts_2015 + pts_2016 + pts_2016_2017 + pts_2017_2018:
            print('Error en conteo {}'.format(nombre))
            sys.exit(1)

        pts_2016_2017 = 43 if row['2016/2017'] == "0" else int(row['2016/2017'])

        nombre = row['Club']
        club = {'nombre': nombre, 'Nombre AFA': nombre_afa, 'Pts 2015': pts_2015, 'Pts 2016': pts_2016,
                'Pts 2016/2017': pts_2016_2017 ,'Pts 2017/2018': pts_2017_2018,
                'PJ': partidos_jugados, 'prom_al_iniciar': row['prom al iniciar'],
                'partidos_locales': 0, 'partidos_visitantes': 0,
                'puntos_de_los_que_visito': 0, 'puntos_de_los_que_recibo': 0}



        clubes[nombre_afa] = club
        clubes_fechas[nombre_afa] = {}


# abrir el fixture y organizarlo, el archivo ya viene mal de origen
headers = ['local1', 'vs1', 'visitante1']  # se los puse yo despues de limpiar detalles
with open('{}/tabula-Fixture-Torneo-2017-2018-1ra-Div.csv'.format(path_datos), newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    fecha_nro = 0
    for row in reader:
        local1 = row['local1'].strip()
        # ver si es un encabezado o linea vacia
        if local1 == '' or local1.startswith('Fecha'):
            print('fin fecha: {}'.format(row))
            fecha_nro += 1
            continue

        visitante1 = row['visitante1'].strip()

        # test de los datos
        if local1 not in clubes.keys():
            print('No existe {} como local1 en la fecha {}'.format(local1, fecha_nro))
            sys.exit(1)

        if visitante1 not in clubes.keys():
            print('No existe {} como visitante1 en la fecha {}'.format(visitante1, fecha_nro))
            sys.exit(1)

        # tenemos los partidos.
        # vemos cuantos de local y visitante tiene cada uno
        clubes[local1]['partidos_locales'] += 1
        clubes[visitante1]['partidos_visitantes'] += 1

        # vemos ahora contra quienes (puntos de la temporada pasada como estimador) juega de local y de visitante
        # quiero ver si hay un patron, si de local juego contra los más fáciles y los visitantes

        clubes[local1]['puntos_de_los_que_recibo'] += clubes[visitante1]['Pts 2016/2017']
        clubes[visitante1]['puntos_de_los_que_visito'] += clubes[local1]['Pts 2016/2017']

        # grabo ese partido en la fecha
        clubes_fechas[local1][fecha_nro] = {'vs': clubes[visitante1]['Nombre AFA'], 'modo': 'L', 'ptos rival tem pasada': clubes[visitante1]['Pts 2016/2017'], 'anterior': ''}
        clubes_fechas[visitante1][fecha_nro] = {'vs': clubes[local1]['Nombre AFA'], 'modo': 'V', 'ptos rival tem pasada': clubes[local1]['Pts 2016/2017'], 'anterior': ''}

        if fecha_nro > 1:  # ver contra quien jugo la fecha anterior el rival
            clubes_fechas[local1][fecha_nro]['anterior'] = clubes_fechas[visitante1][fecha_nro - 1]['vs']
            clubes_fechas[visitante1][fecha_nro]['anterior'] = clubes_fechas[local1][fecha_nro - 1]['vs']


# grabar un archivo con los totales
with open('resultados.csv', 'w', newline='') as csvfile:
    fieldnames = list(clubes['C.A. BOCA JRS.'].keys())
    fieldnames += ['prom ptos adversarios recibidos', 'prom ptos adversarios vistados', 'dif']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for nombre, club in clubes.items():
        # agregar campos calculados
        club['prom ptos adversarios recibidos'] = round(club['puntos_de_los_que_recibo'] / club['partidos_locales'], 3)
        club['prom ptos adversarios vistados'] = round(club['puntos_de_los_que_visito'] / club['partidos_visitantes'], 3)
        club['dif'] = club['prom ptos adversarios recibidos'] - club['prom ptos adversarios vistados']
        writer.writerow(club)

# grabar un archivo con cada equipo
for nombre, club in clubes.items():
    with open('{}.csv'.format(club['nombre']), 'w', newline='') as csvfile:
        fieldnames = ['fecha', 'vs', 'modo', 'puntos adversario 2016-2017', 'rival fecha anterior']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for nro, fecha in clubes_fechas[nombre].items():
            row = {'fecha': nro, 'vs': fecha['vs'], 'modo': fecha['modo'],
                    'puntos adversario 2016-2017': fecha['ptos rival tem pasada'],
                    'rival fecha anterior': fecha['anterior']}
            writer.writerow(row)

        print('TERMINADO {}'.format(nombre))
print('TERMINADO')
