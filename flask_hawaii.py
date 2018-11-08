# dependencies
from flask import Flask, jsonify

import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

from datetime import datetime

# Database Set up
engine = create_engine('sqlite:///Resources/hawaii.sqlite', connect_args={'check_same_thread': False})

Base = automap_base()
Base.prepare(engine, reflect=True)

# Save tables as variables
Measurement = Base.classes.measurements
Station = Base.classes.stations

session = Session(engine)

# Set up Flask
app = Flask(__name__)

# Create route
@app.route("/")
def home():
    return ("Hawaii Weather Data API<br/>"
    "/api/v1.0/precipitation<br/>"
    "/api/v1.0/stations<br/>"
    "/api/v1.0/tobs<br/>"
    "/api/v1.0/yyyy-mm-dd/<br/>"
    "/api/v1.0/yyyy-mm-dd/yyyy-mm-dd/")

# Functions for precip and temp data routes
def prcp_or_temps(choice):
    #create date range dynamically based on last date in database
    most_current = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = most_current[0]
    year_before = last_date.replace(year = (last_date.year - 1))
    year_before = year_before.strftime("%Y-%m-%d")
    #query
    twelve_months = session.query(Station.name, Station.station, Measurement.date, choice).filter(Station.station == Measurement.station, Measurement.date > year_before).order_by(Measurement.date.desc()).all()
    #holder for complete dictionary to be returned
    choice_dict = {}
    # list for each station's data 
    record_list = []
    for x in range(1, len(twelve_months)):
        # create record for each station 
        record_dict = {"station_id": twelve_months[x-1][1], "station name": twelve_months[x-1][0], "station %s measure" % (choice): twelve_months[x-1][3]}
        record_list.append(record_dict)
        #if date changes record date, use as key, and use choice list as values, then dump choice list for next date
        if twelve_months[x-1][2] != twelve_months[x][2]:
            date_str =  twelve_months[x-1][2].strftime("%Y-%m-%d")
            choice_dict[date_str] = record_list
            record_list = []
        # if last record in query add it and append to choice list
        if x == (len(twelve_months)-1):
            record_dict = {"station_id": twelve_months[x][1], "station name": twelve_months[x][0], "station prcp measure": twelve_months[x][3]}
            record_list.append(record_dict)
            date_str =  twelve_months[x][2].strftime("%Y-%m-%d")
            choice_dict[date_str] = record_list
    return choice_dict

# Precip route
@app.route("/api/v1.0/precipitation")
def precip_json():
    #call prcp_or temps function with proper datapoint
    results = prcp_or_temps(Measurement.prcp)
    return jsonify(results)

# Station route
@app.route("/api/v1.0/stations")
def stations():
    # Create a list of data
    stations_list = []
    # Create a Query
    stations = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()
    # Create a dictionary for each station's info and append to list
    for station in stations:
        station_dict = {"station_id": station[0], "name": station[1], "latitude": station[2], "longitude": station[3], "elevation": station[4]}
        stations_list.append(station_dict)
    # Return to user
    return jsonify(stations_list)

# Temp route
@app.route("/api/v1.0/tobs")
def temps_json():
    results = prcp_or_temps(Measurement.tobs)
    return jsonify(results)

# Start date route
@app.route("/api/v1.0/<start_date>/")
def temp_stats(start_date):
    # Query using start date
    temps = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).first()
    # Create a dictionary
    temps_dictionary1 = {"minimum temperuture": temps[0], "maximum temperature": temps[1], "average temperature": temps[2]}
    return jsonify(temps_dictionary1)

# End date route
@app.route("/api/v1.0/<start_date>/<end_date>/")
def temp_range(start_date, end_date):
    # Create a Query
    temps = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start_date, Measurement.date <= end_date).first()
    # Create a dictionary
    temps_dictionary2 = {"TMIN": temps[0], "TMAX": temps[1], "TAVG": temps[2]}
    return jsonify(temps_dictionary2)

if __name__ == '__main__':
    app.run(debug=True)