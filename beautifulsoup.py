import requests
from bs4 import BeautifulSoup
import pandas as pd
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

df_pandas=pd.read_html(url, attrs = {'class': 'wikitable'})[0]

alcaldes = df_pandas["Alcalde"].tolist() + df_pandas["Alcalde.1"].tolist()

data = list(zip(comunas, coordenadas, poblacion_total))
data.sort(key=lambda x: x[0])


for i in range(len(comunas)):
        nombre_comuna, (latitud, longitud), poblacion_ = data[i]
        alcalde = alcaldes[i]
        print("Comuna:", nombre_comuna)
        print("Alcalde:", alcalde)
        print("Habitantes:", poblacion)
        print("Coordenadas:", latitud,longitud)
        print("-----------------------------------")
try:
    sqliteConnection = sqlite3.connect("C:\\code\\beautifulsoup-test\\database.db")
    cursor = sqliteConnection.cursor()
    cursor.execute("SELECT COUNT(*) FROM Coordenadas")
    data_count = cursor.fetchone()[0]
    if data_count > 0:
        # Si hay datos, elimina los registros existentes en la tabla Comunas
        cursor.execute("DELETE FROM Coordenadas")
        print("Se han eliminado los datos anteriores de la base de datos.")

    for i in range(len(comunas)):
            nombre_comuna, (latitud, longitud), poblacion_ = data[i]
            alcalde = alcaldes[i]
            cursor.execute("INSERT INTO Coordenadas(Comuna, Latitud, Longitud, Poblacion, Alcalde) VALUES (?, ?, ?, ?, ?)",
                        (nombre_comuna, latitud, longitud, poblacion_, alcalde))
        
    sqliteConnection.commit()
    cursor.close()

except sqlite3.Error as error:
    print("Error al insertar datos:", error)

finally:
    if sqliteConnection:
        sqliteConnection.close()
