import streamlit as st
import requests
import urllib.parse
import datetime
import folium
from folium.plugins import Draw, MeasureControl
from streamlit_folium import st_folium
import numpy as np

def initialize_map(center, zoom):
    m = folium.Map(location=center, zoom_start=zoom, scrollWheelZoom=False)
    draw = Draw(export=False,
                filename='custom_drawn_polygons.geojson',
                position='topright',
                draw_options={'polyline': False,  # disable polyline option
                              'rectangle': False,  # disable rectangle option for now
                              # enable polygon option
                              #   'polygon': {'showArea': True, 'showLength': False, 'metric': False, 'feet': False},
                              'polygon': False,  # disable rectangle option for now
                              # enable circle option
                              'circle': {'showArea': True, 'showLength': False, 'metric': False, 'feet': False},
                              'circlemarker': False,  # disable circle marker option
                              'marker': False,  # disable marker option
                              },
                edit_options={'poly': {'allowIntersection': False}})
    draw.add_to(m)
    MeasureControl(position='bottomleft', primary_length_unit='miles',
                   secondary_length_unit='meters', primary_area_unit='sqmiles', secondary_area_unit=np.nan).add_to(m)
    return m



TAXI_FARE_API_URL = 'https://taxifare.lewagon.ai/predict'
GEO_LOCALISATION = "https://api-adresse.data.gouv.fr/search/"


# Set up initial map state
CENTER_START = [37.8, -96]
ZOOM_START = 5

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

with one_ride:
    #st.header("Une course")

    with st.form("prediction_form"):

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
                    'limit': 3
                }
                result = requests.get(GEO_LOCALISATION, params=params).json()
                result = result.get('features')[0]
                coord = result.get('geometry').get('coordinates')

                pickup_latitude = coord[1] #-73.950655
                pickup_longitude = coord[0] # 40.783282

                CENTER_START = [pickup_latitude, pickup_longitude]

                # droppoff parameters
                params = {
                    'q': dropoff_address,
                    'limit': 3
                }

                result = requests.get(GEO_LOCALISATION, params=params).json()
                result = result.get('features')[0]
                coord = result.get('geometry').get('coordinates')

                dropoff_latitude = coord[1] #-73.984365
                dropoff_longitude = coord[0] #40.769802

                url = urllib.parse.urljoin(TAXI_FARE_API_URL, "/predict")
                params = {
                    'pickup_datetime': f'{d} {t}',
                    'pickup_longitude':  pickup_longitude,
                    'pickup_latitude': pickup_latitude,
                    'dropoff_longitude':  dropoff_longitude,
                    'dropoff_latitude': dropoff_latitude,
                    'passenger_count': passenger_count

                }

                result = requests.get(url, params=params).json()
                amount = round(result.get("fare"), 2)
                st.write(f'ça vous coute: :blue[{amount}$]')

                m = initialize_map(center=CENTER_START, zoom=ZOOM_START)

                folium.Marker(
                    location=[pickup_latitude, pickup_longitude],
                    tooltip="Click me!",
                    popup="Départ",
                    icon=folium.Icon(icon="cloud"),
                ).add_to(m)

                folium.Marker(
                    location=[dropoff_latitude, dropoff_longitude],
                    tooltip="Click me!",
                    popup="Destination",
                    icon=folium.Icon(color="green"),
                ).add_to(m)


                st_folium(
                    m,
                    center=CENTER_START,
                    zoom=ZOOM_START,
                    key="new",
                    width=1285,
                    height=725,
                    returned_objects=["all_drawings"],
                    use_container_width=True
                )





with many_rides:
    st.write("Plusieurs courses - Dans la prochaine version 😎")
