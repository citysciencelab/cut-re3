import pandas as pd, geopandas as gpd, json, mesa
from flask import Flask, jsonify, request
from flask_sock import Sock

app = Flask(__name__)
sock = Sock(app)


# HTTP Implementation
# Retrieves either a GET Request (Standard parameters for the model run) or a POST request (Individual parameters can be passed on)

@app.route("/http", methods = ["GET", "POST"])
def model_run():

    from model import GeoModel

    # Standard model parameters
    agents_per_10000_inhabitants = 1
    number_iterations = 1
    number_steps = 50


    if request.method == "POST":
        parameters = request.json
        agents_per_10000_inhabitants = parameters.get("agents_per_10000_inhabitants", 1)
        number_iterations = parameters.get("number_iterations", 1)
        number_steps = parameters.get("number_steps", 50)

    params = {"agents_per_10000_inhabitants": agents_per_10000_inhabitants}

    results = mesa.batch_run(
        GeoModel,
        parameters=params,
        iterations=number_iterations,
        max_steps=number_steps,
        number_processes=None,
        data_collection_period=1,
        display_progress=True,
    )

    gdf = gpd.GeoDataFrame(pd.DataFrame(results), geometry="geometry")

    return jsonify(json.loads(gdf.to_json()))

# WebSocket Implementation
# Retrieves data via a Websocket Connection

@sock.route('/socket')
def echo(sock):
    while True:
        data = json.loads(sock.receive())
        sock.send("-- INFO: Data retrieved")
        sock.send("-- INFO: Parameters are " + str(data))
        #app.logger.info(type(data))

        from model import GeoModel

        agents_per_10000_inhabitants = int(data.get("agents_per_10000_inhabitants", 1))
        number_iterations = int(data.get("number_iterations", 1))
        number_steps = int(data.get("number_steps", 50))

        params = {"agents_per_10000_inhabitants": agents_per_10000_inhabitants}

        sock.send("-- INFO: Model run started")
        results = mesa.batch_run(
            GeoModel,
            parameters=params,
            iterations=number_iterations,
            max_steps=number_steps,
            number_processes=None,
            data_collection_period=1,
            display_progress=True,
        )

        gdf = gpd.GeoDataFrame(pd.DataFrame(results), geometry="geometry")

        sock.send("-- INFO: Results")
        sock.send(json.loads(gdf.to_json()))