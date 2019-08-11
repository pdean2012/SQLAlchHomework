


#################################################
# Database Setup
#################################################
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

def calc_temps(start_date, end_date):
    return session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()


#################################################
# Making queries necessary for Flask pages (copied from ipynb file)
#################################################
# Design a query to retrieve the last 12 months of precipitation data and plot the results
sel = [Measurement.date,
       Measurement.prcp]

# Calculate the date 1 year ago from the last data point in the database
last_date = dt.date(2017,8,23)
year_ago=last_date-dt.timedelta(days=365)
#year_ago is 2016,08,23

# Perform a query to retrieve the data and precipitation scores
query = session.query(*sel).filter(Measurement.date.between('2016-08-23', '2017-08-23')).all()

#FOR FLASK: Dictionary of date and prcp
prcp_dict={}
for item in query:
    prcp_dict.update({item[0]:item[1]})

# Choose the station with the highest number of temperature observations.
# Query the last 12 months of temperature observation data for this station
sel2 = [Measurement.date,
       Measurement.tobs]

query2 = session.query(*sel2).filter(Measurement.date.between('2016-08-23', '2017-08-23')).filter(Measurement.station == "USC00519281").all()

#FOR FLASK: Dictionary of date and tobs
temp_dict={}
for item in query2:
    temp_dict.update({item[0]:item[1]})

#getting station list
active_stations = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).all()

station_list=[]

for entry in active_stations:
    station_list.append(entry[0])

# This function called `calc_temps` will accept start date and end date in the format '%Y-%m-%d' 
# and return the minimum, average, and maximum temperatures for that range of dates



#################################################
# Flask Setup
#################################################
from flask import Flask, jsonify, request
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List of all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"You may also query temperature data between two end dates by using the following URL syntax:<br/>"
        f"/api/v1.0/dateroute?start=yyyy-mm-dd&end=yyyy-mm-dd<br/>"

    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a JSONIFY of prcp"""
    return jsonify(prcp_dict)


@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations"""

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSONIFY of tobs"""
    return jsonify(temp_dict)

@app.route("/api/v1.0/dateroute", methods=['GET'])
def dateroute():
    ###connecting to the engine again to avoid error "SQLite objects created in a thread can only be used in that same thread"
    engine = create_engine("sqlite:///Resources/hawaii.sqlite")
    Base = automap_base()
    Base.prepare(engine, reflect=True)
    Measurement = Base.classes.measurement
    Station = Base.classes.station
    session = Session(engine)
    #################################

    def calc_temps(start_date, end_date):
        return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()


    start = request.args.get('start', default = 1, type = str)
    end = request.args.get('end', default = '2018-8-23', type = str)

    return jsonify(calc_temps(start,end))

if __name__ == '__main__':
    app.run(debug=True)
