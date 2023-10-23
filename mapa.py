# Integrantes: xxx

from flask import Flask
import folium
import sqlite3
import math

app = Flask(__name__)

#melbourne = (-37.840935, 144.946457)
osorno=(-40.57611891208618, -73.11679310991)
server='127.0.0.1'

@app.route("/")
def base():
    # this is base map
    map = folium.Map(
        location=osorno,
        zoom_start=13
    )
    
    try:
        sqliteConnection = sqlite3.connect("C:\\code\\beautifulsoup-test\\database.db")
        cursor = sqliteConnection.cursor()
        print("Connected to SQLite")

        sqlite_select_query = """SELECT Comuna, Latitud, Longitud, Poblacion, Alcalde FROM Coordenadas;"""
    
        cursor.execute(sqlite_select_query)
    
        items = cursor.fetchall()
        max_poblacion = max(item[3] for item in items)
        min_poblacion = min(item[3] for item in items)
        for item in items:
            poblacion_radius = (item[3] - min_poblacion) / (max_poblacion - min_poblacion)
            radius = 1000 + int(poblacion_radius * 4000)  # Ajusta el rango de tamaño deseado
            folium.Circle(location = (item[1], item[2]),
                        radius = radius,
                        color="black",
                        weight=1,
                        fill_opacity=0.6,
                        opacity=1,
                        fill_color="green",
                        fill=False,  # gets overridden by fill_color
                        popup='<h4><b>Comuna:</b> {}</h4><h4><b>Alcalde:</b> {}</h4><h4><b>Habitantes:</b> {}</h4>'.format(item[0],item[4],item[3]),
                        tooltip='<h4><b>{}</b></h4>'.format(item[0]),).add_to(map)
        
        cursor.close()

    except sqlite3.Error as error:
        print("Failed to read data from sqlite table", error)
    finally:
            if (sqliteConnection):
                sqliteConnection.close()
                print("The SQLite connection is closed")
    return map._repr_html_()

@app.route("/open-street-map")
def open_street_map():
    # this map using stamen toner
    map = folium.Map(
        location=[45.52336, -122.6750],
        tiles='Stamen Toner',
        zoom_start=13
    )

    folium.Marker(
        location=[45.52336, -122.6750],
        popup="<b>Marker here</b>",
        tooltip="Click Here!"
    ).add_to(map)
    
    return map._repr_html_()

@app.route("/map-marker")
def map_marker():
    # this map using stamen terrain
    # we add some marker here
    map = folium.Map(
        location=[45.52336, -122.6750],
        tiles='Stamen Terrain',
        zoom_start=12
    )

    folium.Marker(
        location=[45.52336, -122.6750],
        popup="<b>Marker here</b>",
        tooltip="Click Here!"
    ).add_to(map)

    folium.Marker(
        location=[45.55736, -122.8750],
        popup="<b>Marker 2 here</b>",
        tooltip="Click Here!",
        icon=folium.Icon(color='green')
    ).add_to(map)

    folium.Marker(
        location=[45.53236, -122.8750],
        popup="<b>Marker 3 here</b>",
        tooltip="Click Here!",
        icon=folium.Icon(color='red')
    ).add_to(map)

    folium.Circle(
        location=[-27.551667, -48.478889],
        radius=radius,
        color="black",
        weight=1,
        fill_opacity=0.6,
        opacity=1,
        fill_color="green",
        fill=False,  # gets overridden by fill_color
        popup="{} meters".format(radius),
        tooltip="I am in meters",
    ).add_to(m)

    return map._repr_html_()

if __name__ == "__main__":
    app.run(debug=True, host=server)