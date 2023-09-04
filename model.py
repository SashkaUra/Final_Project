import mysql.connector
from views import config

db_name = 'stations_db'


def get_countrylist():
    cnx = mysql.connector.connect(host=config.your_host,
                                  user=config.user_ID,
                                  password=config.passwd,
                                  database=db_name)
    cursor = cnx.cursor()

    query_country = ("""SELECT country_name FROM country ORDER BY country_name ASC""")
    cursor.execute(query_country)
    countrylist = [item[0] for item in cursor.fetchall()]

    cursor.close()
    cnx.close()
    return countrylist


def get_station_country(country):
    cnx = mysql.connector.connect(host=config.your_host,
                                  user=config.user_ID,
                                  password=config.passwd,
                                  database=db_name)
    cursor = cnx.cursor()

    query = ("""SELECT wmo_id, station_name, lat, lon, alt, start, end 
               FROM country INNER JOIN station ON station.idcountry=country.idcountry
               WHERE country_name=%s;""")

    cursor.execute(query, (country,))

    cont = []
    for (wmo_id, station_name, lat, lon, alt, start, end) in cursor:
        cont.append((wmo_id, station_name, lat, lon, alt, start, end))

    cursor.close()
    cnx.close()

    return cont

def get_station_marker():
    cnx = mysql.connector.connect(host=config.your_host,
                                  user=config.user_ID,
                                  password=config.passwd,
                                  database=db_name)
    cursor = cnx.cursor()

    query = ("""SELECT station_name, lat, lon, wmo_id
               FROM station""")

    cursor.execute(query)

    markers = []
    for (station_name, lat, lon, wmo_id) in cursor:
        markers.append((station_name, lat, lon, wmo_id))

    cursor.close()
    cnx.close()

    return markers