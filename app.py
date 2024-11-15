from flask import Flask, request, jsonify
from flask_cors import CORS
import influxdb
from datetime import datetime

app = Flask(__name__)
CORS(app)

# InfluxDB credentials
HOST = 'influx.linklab.virginia.edu'
PORT = 443
USERNAME = 'cps1f23'
PASSWORD = 'phah7goohohng5ooL9mae1quohpei1Ahsh1uGing'
DATABASE = 'gateway-generic'

# Connect to InfluxDB
client = influxdb.InfluxDBClient(HOST, PORT, USERNAME, PASSWORD, DATABASE, ssl=True, verify_ssl=True)

# Endpoint to get unique locations
@app.route('/get_locations', methods=['GET'])
def get_locations():
    query = 'SHOW TAG VALUES FROM "Temperature_°C" WITH KEY = "location_specific"'
    result = client.query(query)
    locations = [point['value'] for point in result.get_points()]
    return jsonify(locations)

# Endpoint to get temperature data based on time and location
@app.route('/get_temperature', methods=['GET'])
def get_temperature():
    #Get location
    location = request.args.get('location')

    #Get time period
    time1 = datetime.strptime(request.args.get('time1'), "%Y-%m-%dT%H:%M")
    time2 = datetime.strptime(request.args.get('time2'), "%Y-%m-%dT%H:%M")
    time1 = time1.strftime('%Y-%m-%dT%H:%M:%SZ')
    time2 = time2.strftime('%Y-%m-%dT%H:%M:%SZ')

    #Query
    query = f"""
    SELECT mean(value) FROM "Temperature_°C"
    WHERE time >= '{time1}' AND time <= '{time2}' AND location_specific = '{location}'
    GROUP BY device_id, time(30m)
    ORDER BY time ASC;
    """
    result = client.query(query)
    points = list(result.get_points())

    #Format data
    time = []
    temp = []
    for p in points:
        time.append(p["time"])
        temp.append(p["mean"])
    
    trace = {
        "x": time,
        "y": temp,
        "type": "scatter",
        "mode": "lines+markers",
        "name": "data"
    }
    
    return jsonify(trace)

if __name__ == '__main__':
    app.run(debug=True)
