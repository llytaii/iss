import plotly.graph_objects as go
import requests

iss = requests.get('http://api.open-notify.org/iss-now.json').json()

latitude, longitude = map(float, iss['iss_position'].values())

fig = go.Figure(go.Scattergeo(
    lat = [latitude],
    lon = [longitude],
    mode = 'markers',
    marker = dict(
        size = 10,
        color = 'red',
        symbol = 'circle'
    )
))

fig.update_geos(projection_type="natural earth")

fig.update_layout(title='Weilheim')

fig.show()
