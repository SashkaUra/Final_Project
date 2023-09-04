from flask import Flask, render_template, request, url_for, redirect, flash
import folium
import csv



app = Flask(__name__)
app.secret_key = 'secret_key'

from views import model, data_acquirer


SITE_URL = "http://weather.uwyo.edu/cgi-bin/sounding?"
PARAMETERS_FORMAT = "region=naconf&TYPE=TEXT%3ALIST&YEAR=<<year>>&MONTH=<<month>>&FROM=<<from>>&TO=<<to>>&STNM=<<station_number>>"

def genFileName(params):
    fn = str(params['station_number']) + '_'
    fn += str(params['year']) + '_'
    fn += str(params['month']) + '_'
    fn += str(params['from']) + '.csv'
    return fn

def get_data(year, month, srok, station_id):
    acq = data_acquirer.DataAcquirer(SITE_URL, PARAMETERS_FORMAT)
    params = {}
    params['year'] = year
    params['month'] = month
    params['from'] = params['to'] = srok
    params['station_number'] = station_id
    acq.prepareRequest(params)
    acq.getData()

    with open(genFileName(params), 'w', newline='') as csvfile:
        tablewriter = csv.writer(csvfile, delimiter=';', quotechar='\'', quoting=csv.QUOTE_MINIMAL)
        tablewriter.writerow(acq.headers)
        tablewriter.writerow(acq.dims)
        for r in acq.data:
            tablewriter.writerow(r)

@app.route('/access_to_data', methods=['GET', 'POST'])
def index():
    start_coords = (60, 30)
    folium_map = folium.Map(
        location=start_coords,
        tiles="Stamen Terrain",
        zoom_start=5)
    mark = model.get_station_marker()
    for row in mark:
        folium.Marker(
            location=[row[1], row[2]],
            popup=row[3],
            tooltip=row[0],
            icon=folium.Icon(color='red')
        ).add_to(folium_map)
    folium_map.save('templates/map.html')
    if request.method == "POST":
        try:
            year = str(request.form['YEAR'])
            month = str(request.form['MONTH'])
            srok = str(request.form['DAY'])+str(request.form['Observation'])
            station_id = str(request.form['STNM'])
            get_data(year, month, srok, station_id)
            return render_template('weather.html')
        except IndexError:
            flash("No observation in this day, try another one")
            return render_template('failed_download.html')
    else:
        return render_template('nav_1.html')


@app.route('/map')
def map():
    return render_template('map.html')

@app.route('/', methods=['GET', 'POST'])
def form_countrylist():
    countrylist = model.get_countrylist()
    if request.method == 'POST':
        country_f = request.form["search_country"]
        return redirect(url_for('get_station_info', country=country_f))
    else:
        return render_template('station_info.html', countrylist=countrylist)

@app.route('/<path:country>')
def get_station_info(country):
    cont = model.get_station_country(country)
    return render_template('station_info_detail.html', cont=cont, country=country)


if __name__ == "__main__":
    app.run(debug=True)


