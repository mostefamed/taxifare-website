import streamlit as st
import requests
import urllib.parse
import datetime
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

TAXI_FARE_API_URL = 'https://taxifare.lewagon.ai'
ZOOM_START = 5


def css_style():
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

def header():
    st.header('Bienvenue chez RideEstimate 🛣️', divider='grey')
    st.write("Ne laissez pas l'incertitude vous ralentir, RideEstimate trace votre chemin 🚕")

def tabs():
    one_ride, many_rides = st.tabs(["Une course", "Plusieurs courses"])

    return one_ride, many_rides

def get_coordinates(pickup_address, dropoff_address):

    pu = Nominatim(user_agent='pu')
    pickup_coordinates = pu.geocode(pickup_address).raw
    pickup_latitude = pickup_coordinates.get('lat')
    pickup_longitude = pickup_coordinates.get('lon')

    do = Nominatim(user_agent='do')
    dropoff_coordinates = do.geocode(dropoff_address).raw
    dropoff_latitude = dropoff_coordinates.get('lat')
    dropoff_longitude = dropoff_coordinates.get('lon')

    return pickup_latitude, pickup_longitude, dropoff_latitude, dropoff_longitude

def perform_predict(d, t, pickup_latitude, pickup_longitude, dropoff_latitude, dropoff_longitude, passenger_count):

    url = urllib.parse.urljoin(TAXI_FARE_API_URL, "predict")
    st.write(url)
    params = {
        'pickup_datetime': f'{d} {t}',
        'pickup_longitude':  pickup_longitude,
        'pickup_latitude': pickup_latitude,
        'dropoff_longitude':  dropoff_longitude,
        'dropoff_latitude': dropoff_latitude,
        'passenger_count': passenger_count
    }

    result = requests.get(url, params=params).json()

    return round(result.get("fare"), 2)

def draw_map(pickup_latitude, pickup_longitude, dropoff_latitude, dropoff_longitude):
    CENTER_START = [pickup_latitude, pickup_longitude]
    m = folium.Map(location=CENTER_START, zoom_start=ZOOM_START, scrollWheelZoom=False)

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

def handle_form():

    with st.form("prediction_form"):

            d = st.date_input("C'est pour quand ?", datetime.date.today())
            t = st.time_input("À quel heure ?", value="now")
            pickup_address = st.text_input("Adresse de départ", '')
            dropoff_address = st.text_input("Adresse d'arrivée", '')
            passenger_count = st.number_input("Nombre de passager", min_value=1, max_value=7)

            submitted = st.form_submit_button("Estimer")

            if submitted:
                with st.spinner('Estimation en cours...'):

                    pickup_latitude, pickup_longitude, dropoff_latitude, dropoff_longitude = get_coordinates(
                        pickup_address,
                        dropoff_address
                    )
                    fare = perform_predict(d, t, pickup_latitude, pickup_longitude, dropoff_latitude, dropoff_longitude, passenger_count)
                    st.write(f'ça vous coute: :blue[{fare}$]')
                    draw_map(pickup_latitude, pickup_longitude, dropoff_latitude, dropoff_longitude)


def main():
    css_style()
    header()
    one_ride, many_rides = tabs()

    with one_ride:
        handle_form()

    with many_rides:
        st.write("Plusieurs courses - Dans la prochaine version 😎")

if __name__ == '__main__':
    main()
