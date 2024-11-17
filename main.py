import dash
from dash import dcc, html
from dash.dependencies import Output, Input
import plotly.graph_objects as go
import requests
from datetime import datetime

# Initialize Dash app
app = dash.Dash(__name__)
server = app.server  # For deployment purposes

def get_iss_position():
    """
    Fetches the current latitude and longitude of the ISS from the Open Notify API.

    Returns:
        tuple: (latitude, longitude, timestamp)
    """
    try:
        response = requests.get('http://api.open-notify.org/iss-now.json')
        data = response.json()
        position = data['iss_position']
        latitude = float(position['latitude'])
        longitude = float(position['longitude'])
        timestamp = data['timestamp']
        return latitude, longitude, timestamp
    except Exception as e:
        print(f"Error fetching ISS position: {e}")
        return None, None, None

# Initialize lists to store ISS trajectory data
trajectory_lat = []
trajectory_lon = []
trajectory_time = []

# Define the app layout
app.layout = html.Div([
    dcc.Graph(
        id='iss-map',
        config={'displayModeBar': False},  # Hide the mode bar for a cleaner look
        style={'height': '100vh', 'width': '100vw'}  # Full viewport height and width
    ),
    dcc.Interval(
        id='interval-component',
        interval=1000*60,  # Update every 5 seconds (5000 milliseconds)
        n_intervals=0      # Number of times the interval has passed
    )
], style={'margin': '0', 'padding': '0'})

# Define callback to update the map
@app.callback(
    Output('iss-map', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_map(n):
    # Fetch the latest ISS position
    lat, lon, timestamp = get_iss_position()

    if lat is not None and lon is not None:
        # Convert timestamp to readable format
        time_str = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S UTC')

        # Append the new position to the trajectory lists
        trajectory_lat.append(lat)
        trajectory_lon.append(lon)
        trajectory_time.append(time_str)

        # Optional: Limit the number of trajectory points to avoid performance issues
        MAX_POINTS = 100  # Adjust as needed
        if len(trajectory_lat) > MAX_POINTS:
            trajectory_lat.pop(0)
            trajectory_lon.pop(0)
            trajectory_time.pop(0)

        # Create Scattergeo trace for the trajectory (lines)
        trace_trajectory = go.Scattergeo(
            lon=trajectory_lon,
            lat=trajectory_lat,
            mode='lines',
            line=dict(width=2, color='blue'),
            name='Trajectory'
        )

        # **Modify trace_points to exclude the current position**
        # This prevents overlapping markers for the current position
        if len(trajectory_lat) > 1:
            trace_points = go.Scattergeo(
                lon=trajectory_lon[:-1],  # Exclude the last point
                lat=trajectory_lat[:-1],
                mode='markers',
                marker=dict(
                    size=6,
                    color='red',
                    symbol='circle',
                    line=dict(width=1, color='black')
                ),
                text=trajectory_time[:-1],  # Exclude the last timestamp
                hoverinfo='text',
                name='Previous Positions'
            )
        else:
            # If there's only one point, no previous positions to plot
            trace_points = go.Scattergeo(
                lon=[],
                lat=[],
                mode='markers',
                marker=dict(
                    size=6,
                    color='red',
                    symbol='circle',
                    line=dict(width=1, color='black')
                ),
                text=[],
                hoverinfo='text',
                name='Previous Positions'
            )

        # Create Scattergeo trace for the current position
        trace_current = go.Scattergeo(
            lon=[lon],
            lat=[lat],
            mode='markers',
            marker=dict(
                size=12,
                color='red',
                symbol='circle',
                line=dict(width=2, color='black')
            ),
            text=[f'Current Position<br>{time_str}'],
            hoverinfo='text',
            name='Current Position'
        )

        # Combine all traces
        data = [trace_trajectory, trace_points, trace_current]

        # Define the layout of the map
        layout = go.Layout(
            geo=dict(
                scope='world',
                projection_type='natural earth',
                showland=True,
                landcolor='lightgray',
                showcountries=True,
                countrycolor='gray',
                showocean=True,
                oceancolor='LightBlue',
                showlakes=True,
                lakecolor='LightBlue',
                showrivers=True,
                rivercolor='LightBlue',
            ),
            margin=dict(l=50, r=50, t=50, b=50),
            showlegend=False
        )

        # Create the figure
        fig = go.Figure(data=data, layout=layout)

        return fig
    else:
        # If fetching fails, return the existing figure without changes
        return dash.no_update

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=False)
