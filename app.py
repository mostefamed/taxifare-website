import random
import streamlit as st
import requests
import urllib.parse
import datetime
import folium
from folium.plugins import Draw, MeasureControl
from streamlit_folium import st_folium
import numpy as np
import time


def initialize_session_state():
    if "center" not in st.session_state:
        st.session_state["center"] = CENTER_START
    if "zoom" not in st.session_state:
        st.session_state["zoom"] = ZOOM_START
    if "markers" not in st.session_state:
        st.session_state["markers"] = []
    if "map_data" not in st.session_state:
        st.session_state["map_data"] = {}
    if "all_drawings" not in st.session_state["map_data"]:
        st.session_state["map_data"]["all_drawings"] = None
    if "upload_file_button" not in st.session_state:
        st.session_state["upload_file_button"] = False




def reset_session_state():
    # Delete all the items in Session state besides center and zoom
    for key in st.session_state.keys():
        if key in ["center", "zoom"]:
            continue
        del st.session_state[key]
    initialize_session_state()



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



TAXI_FARE_API_URL = 'https://taxifare-mostefa-bbkf4aq3na-ew.a.run.app'
GEO_LOCALISATION = "https://nominatim.openstreetmap.org/search"


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

headers = {

    "Accept-Language":"fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3"
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
                    'format': 'json',
                    'limit': 1
                }
                result = requests.get(GEO_LOCALISATION, params=params, headers=headers).json()
                pickup_latitude = result[0]['lat'] #-73.950655
                pickup_longitude = result[0]['lon']  # 40.783282

                # droppoff parameters
                params = {
                    'q': dropoff_address,
                    'format': 'json',
                    'limit': 1
                }
                time.sleep(4)
                result = requests.get(GEO_LOCALISATION, params=params, headers=headers).json()
                dropoff_latitude = result[0]['lat'] #-73.984365
                dropoff_longitude = result[0]['lon'] #40.769802

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


                initialize_session_state()

                m = initialize_map(center=st.session_state["center"], zoom=st.session_state["zoom"])


                fg = folium.FeatureGroup(name="Markers")
                for marker in st.session_state["markers"]:
                    fg.add_child(marker)

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

                # Create the map and store interaction data inside of session state
                map_data = st_folium(
                    m,
                    center=st.session_state["center"],
                    zoom=st.session_state["zoom"],
                    feature_group_to_add=fg,
                    key="new",
                    width=1285,
                    height=725,
                    returned_objects=["all_drawings"],
                    use_container_width=True
                )
                st.write("## map_data")
                st.write(map_data)
                st.write("## session_state")
                st.write(st.session_state)





with many_rides:
    st.write("Plusieurs courses - Dans la prochaine version 😎")
