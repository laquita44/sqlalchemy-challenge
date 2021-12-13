import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/station<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
             
    )

    # Retrieve data for date and precipitation
    # Decorator and Handler
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all dates and prcp"""
    # Query the results
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    # Convert the query results to a dictionary using date as the key and prcp as the value.
    # Return a results by JSONIFYING  the dictionary 
    all_prcp_date = []
    for date, prcp in results:
        date_prcp_dict = {}
        date_prcp_dict["date"] = date
        date_prcp_dict["prcp"] = prcp
        all_prcp_date.append(date_prcp_dict)
    return jsonify(all_prcp_date)

    
    # decorator and handler
@app.route("/api/v1.0/station")
def station():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all unique Stations"""
    # Query all unique Stations
    results = session.query(Measurement.station).group_by(Measurement.station).all()

    # Close the session so you want have any memory leaks
    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    # Return a JSON list of Stations
    return jsonify(all_stations)

    # Decorator and Handler
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Query the dates and temp observations of the most active station for last year of data"""
    # Query temperatures for last year data
    # Most active station with row count
    most_active_stations = session.query(Measurement.station,func.count(Measurement.station)).\
    group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()

    # The most active station
    most_active_stations = session.query(Measurement.station,func.count(Measurement.station)).\
    group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()    
    most_active_station = most_active_stations[0]

    # Calculate the date one year from the last date in data set.
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    # Get the dates and temperture for last year data
    station = session.query(Measurement.date,Measurement.tobs).filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date > year_ago).all()

    results = session.query(Measurement.tobs).filter(Measurement.station=='USC00519281').filter(Measurement.date >= year_ago).all()

    # Close the session so you want have any memory leaks
    session.close()

    # Convert list of tuples into normal list
    temps_previous_year = list(np.ravel(results))

    # Return a JSON list of temperature observations (TOBS) for the previous year.
    return jsonify(temps_previous_year)

# Decorator and Handler
@app.route("/api/v1.0/start")
@app.route("/api/v1.0/<start>")
def start_date(start='2010-01-01'):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the start date
    # start_date = session.query(Measurement.date).\
    # filter(Measurement.date > '2010-01-01').order_by(Measurement.date).all() 

    """ Query start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date"""
   
    results = session.query(Measurement.date,func.min(Measurement.tobs),\
    func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= start).all()

    # Close session out to prevent memory leaks
    session.close()
    
    # Create a empty list to loop through dictionaries and append results to a jsonify list
    start_temps = []
    for date, min, avg, max in results:
        temp_dict = {}
        temp_dict["Date"] = date
        temp_dict["TMIN"] = min
        temp_dict["TAVG"] = avg
        temp_dict["TMAX"] = max
        start_temps.append(temp_dict)

    return jsonify(start_temps)

# Decorator and Function Handler
@app.route("/api/v1.0/start/end")
def start_end_date(start='2010-01-01',end='2017-08-23'):

    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    """Return a list of minimum, average and max temperature for a given start date and end date"""
    # Query of min, max and avg temperature for dates between given start and end date.
    results = session.query(func.min(Measurement.tobs),\
         func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
             filter(Measurement.date >= start).filter(Measurement.date <= end).all()


    session.close()        
    
# Create a dictionary from the data and append to a list
    start_and_end_date_temps = []
    for min, avg, max in results:
        temps_dict = {}
        temps_dict["TMIN"] = min
        temps_dict["TAVG"] = avg
        temps_dict["TMAX "] = max
        start_and_end_date_temps.append(temps_dict)

    return jsonify(start_and_end_date_temps)
    # Launch condition
if __name__ == '__main__':
    app.run(debug=True)
