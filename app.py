import streamlit as st
import requests
import urllib.parse
import datetime
import folium

TAXI_FARE_API_URL = 'https://taxifare-mostefa-bbkf4aq3na-ew.a.run.app'
GEO_LOCALISATION = "https://nominatim.openstreetmap.org"

st.header('Bienvenue chez RideEstimate 🛣️', divider='grey')
st.write("Ne laissez pas l'incertitude vous ralentir, RideEstimate trace votre chemin 🚕")

one_ride, many_rides = st.tabs(["Une course", "Plusieurs courses"])

st.markdown(
    """
    <style>
    p {
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Accept-Language":"en-US"
}

with one_ride:
    #st.header("Une course")

    with st.form("prediction_form"):
        #st.write("Veuillez remplir les informations ci-dessous")

        d = st.date_input("C'est pour quand ?", datetime.date.today())
        t = st.time_input("À quel heure ?", value="now")


        pickup_address = st.text_input("Adresse de départ", '')
        dropoff_address = st.text_input("Adresse d'arrivée", '')


        passenger_count = st.number_input("Nombre de passager", min_value=1, max_value=7)

        # Every form must have a submit button.
        submitted = st.form_submit_button("Estimer")

        if submitted:
            with st.spinner('Estimation en cours...'):
                # pickup parameters
                params = {
                    'q': pickup_address,
                    'format': 'json'
                }
                result = requests.get(GEO_LOCALISATION, params=params, headers=headers).json()
                pickup_latitude = result[0]['lat']
                pickup_longitude = result[0]['lon']

                # droppoff parameters
                params = {
                    'q': dropoff_address,
                    'format': 'json'
                }
                result = requests.get(GEO_LOCALISATION, params=params, headers=headers).json()
                dropoff_latitude = result[0]['lat']
                dropoff_longitude = result[0]['lon']

                url = urllib.parse.urljoin(TAXI_FARE_API_URL, "/predict")
                params = {
                    'pickup_datetime': f'{d} {t}',
                    'pickup_longitude':  pickup_longitude,
                    'pickup_latitude': pickup_latitude,
                    'dropoff_longitude':  dropoff_longitude,
                    'dropoff_latitude': dropoff_latitude,
                    'passenger_count': passenger_count

                }

                result = requests.get(url, params=params, headers=headers).json()
                amount = round(result.get("fare"), 2)
                st.write(f'ça vous coute: :blue[{amount}$]')

                m = folium.Map(location=(45.5236, -122.6750))
                folium.Marker(
                    location=[pickup_longitude, pickup_latitude],
                    tooltip="depart",
                    popup="Mt. Hood Meadows",
                    icon=folium.Icon(icon="cloud"),
                ).add_to(m)

                folium.Marker(
                    location=[dropoff_longitude, dropoff_latitude],
                    tooltip="destination",
                    popup="Timberline Lodge",
                    icon=folium.Icon(color="green"),
                ).add_to(m)

                st.write(m)




with many_rides:
    st.write("Plusieurs courses - Dans la prochaine version 😎")
