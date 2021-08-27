import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from datetime import datetime

from flask import Flask, jsonify
app = Flask(__name__)

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect = True)
Station = Base.classes.station
Measurement = Base.classes.measurement

#################################################
# Flask Routes
#################################################



@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def prcpdictionary():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()
    date_dictionary = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        date_dictionary.append(prcp_dict)
    # Convert list of tuples into normal list
    return jsonify(date_dictionary)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    station_que = session.query(Station).all()
    station_list = []
    for stat in station_que:
        station_list.append(stat.station)
    
    session.close()
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobscode():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    station_que = session.query(Station)
    measure_que = session.query(Measurement)
    most_recent_date_list = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    most_recent_date = dt.datetime.strptime(most_recent_date_list[0], '%Y-%m-%d')
    print("------------------------", most_recent_date)
    oldest_date = str(most_recent_date - dt.timedelta(days=365))
    print("------------------", oldest_date)
    max_station_tobs_que = session.query(Measurement.tobs).\
        filter(Measurement.date > oldest_date).\
        filter(Measurement.station == 'USC00519281').\
        order_by(Measurement.date).all()
    session.close()
    tobs_list = []
    print("--------------------", max_station_tobs_que)
    return jsonify(list(np.ravel(max_station_tobs_que)))
        

@app.route('/api/v1.0/<start>')
@app.route('/api/v1.0/<start>/<end>')
def stats(start, end = None):
    session = Session(engine)
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    if not end:
        results = session.query(*sel).filter(Measurement.date > start).all()
        final_result = list(np.ravel(results))
        return jsonify(temps = final_result)
    else:
        results = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
        final_result = list(np.ravel(results))
        return jsonify(temps = final_result)

if __name__ == "__main__":
    app.run(debug=True)