from flask import Flask, request, jsonify
from flask_cors import CORS
import influxdb
import pandas as pd

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

# Endpoint to get time range
# @app.route('/get_time_range', methods=['GET'])
# def get_time_range():
#     query = """
#     SELECT FIRST("time") as start, LAST("time") as end FROM "Temperature_°C"
#     """
#     result = client.query(query)
#     points = list(result.get_points())
#     time_range = {
#         "start": points[0]["start"],
#         "end": points[0]["end"]
#     }
#     return jsonify(time_range)

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
    location = request.args.get('location')

    query = f"""
    SELECT mean(value) FROM "Temperature_°C"
    WHERE time >= '2024-09-03T00:00:00Z' AND time <= '2024-09-10T00:00:00Z' AND location_specific = '{location}'
    GROUP BY time(30m), location_specific
    ORDER BY time ASC;
    """
    
    result = client.query(query)
    points = list(result.get_points())

    # Convert results to JSON format
    data = [{"time": point["time"], "temperature": point["mean"]} for point in points]
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
