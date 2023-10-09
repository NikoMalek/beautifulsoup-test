import requests
from bs4 import BeautifulSoup
import sqlite3
import re

url = "https://es.wikipedia.org/wiki/Regi%C3%B3n_de_Los_Lagos"
response = requests.get(url)


soup = BeautifulSoup(response.text, 'html.parser')
tabla = soup.find('table', {'class': 'wikitable'})


comunas = []
href = []

for fila in tabla.find_all('tr')[1:]:
    celdas = fila.find_all('td')
    comuna_href = celdas[0].find('a')['href']
    #print (celdas)
    if len(celdas) > 0:
        comuna = celdas[0].text.strip()
        if 'align' not in celdas[0].attrs or celdas[0]['align'] != 'center':
            comunas.append(comuna)
            href.append(comuna_href)
            
        else:
            comuna = celdas[2].text.strip()
            comunas.append(comuna)
            comuna_href = celdas[2].find('a')['href']
            href.append(comuna_href)

coordenadas=[]
poblacion_total=[]
for comuna_href in href:
    enlace=("https://es.wikipedia.org/" + comuna_href)
    response = requests.get(enlace)
    soup_enlace = BeautifulSoup(response.text, 'html.parser')
    if response.status_code == 200:
        geo = soup_enlace.find('span', class_='geo')
        latitud = geo.find('span', class_='latitude').text.strip().rstrip(',')

        longitud = geo.find('span', class_='longitude').text.strip().rstrip(',')
        coordenada = (latitud,longitud)
        coordenadas.append(coordenada)
        tabla_poblacion = soup_enlace.find('table', {'class': 'infobox'})
        if tabla_poblacion:
            for fila in tabla_poblacion.find_all('tr'):
                if 'hab.' in fila.text:
                    poblacion_text = fila.find('td').text.strip()
                    poblacion_text = re.sub(r'\[\d+\]', '', poblacion_text)
                    poblacion_text = re.sub(r'[^\d,]', '', poblacion_text)
                    poblacion_text = poblacion_text.replace(',', '')
                    poblacion = poblacion_text.strip()
                    poblacion_total.append(poblacion)


    else:
        print("No se pudo hacer conexion a la pagina")

for comuna, poblacion, coordenada in zip(comunas, poblacion_total, coordenadas):
    print("Comuna:", comuna)
    print("Habitantes:", poblacion)
    print("Coordenadas:", coordenada)
    print("-----------------------------------")

try:
    sqliteConnection = sqlite3.connect("C:\\Proyectos\\beautifulsoup\\database.db")
    cursor = sqliteConnection.cursor()

    for i in range(len(comunas)):
        nombre_comuna = comunas[i]
        latitud, longitud = coordenadas[i]
        poblacion_ = poblacion_total[i]

        cursor.execute("INSERT INTO Coordenadas(Comuna, Latitud, Longitud, Poblacion) VALUES (?, ?, ?, ?)", (nombre_comuna, latitud, longitud, poblacion_,))
        
    sqliteConnection.commit()
    cursor.close()

except sqlite3.Error as error:
    print("Error al insertar datos:", error)

finally:
    if sqliteConnection:
        sqliteConnection.close()
