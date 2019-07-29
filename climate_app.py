# NAME
#     climate_app.py
# 
# DESCRIPTION
#     This is a Flask application that exposes an API to explore climate in
#     Honolulu, Hawaii.
#
# REMARKS
#     Created on Jul 28, 2019 by Gilberto Ramirez (gramirez77@gmail.com).
#     UNC Data Analytics Bootcamp Homework, Week 10 (SQLAlchemy).


import numpy as np

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


#~~~~~~~~~~~~~~~~~~
# Database Setup
#~~~~~~~~~~~~~~~~~~

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station


#~~~~~~~~~~~~~~~
# Flask Setup
#~~~~~~~~~~~~~~~

# First, we need to import our Flask class and jsonify.
from flask import Flask, jsonify

# Now, we need to create an instance of the Flask class. The first argument 
# is the name of the application’s module or package. Since we are using a 
# single module, we need to use __name__ because depending on if it’s started 
# as application or imported as module the name will be different ('__main__' 
# versus the actual import name). This is needed so that Flask knows where to 
# look for templates, static files, and so on.
app = Flask(__name__)

# Time to define `routes`. Routes() are decorators that tell Flask what URL 
# should trigger which function

# Home page
@app.route("/")
def home():
    """List all available routes."""
    return (
        f"<h1>This is the Home Page</h1>"
        f"<hr/>"
        f"These are the available routes:<ul>"
        f"  <li>/api/v1.0/precipitation"
        f"  <li>/api/v1.0/stations</li>"
        f"  <li>/api/v1.0/tobs</li>"
        f"  <li>/api/v1.0/&ltstart&gt</li>"
        f"  <li>/api/v1.0/&ltstart&gt/&ltend&gt</li></ul>"
    )

# Average Precipitation (Last Year)
@app.route("/api/v1.0/precipitation")
def precipitation():
    """List average precipitation per day for last year."""
    session = Session(engine)

    # calculate last date of measurements data
    lastdate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]

    # calculate date for one year ago before last date
    d = datetime.strptime(lastdate, '%Y-%m-%d') - relativedelta(years=1)
    yearago = d.strftime('%Y-%m-%d')

    results = session.query(Measurement.date, func.avg(Measurement.prcp)).\
        filter(Measurement.date >= yearago).\
        group_by(Measurement.date).\
        order_by(Measurement.date).all()
    
    # create a dictionary base on the results fetched from the database
    prcp_list = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict['date'] = date
        prcp_dict['prcp'] = prcp
        prcp_list.append(prcp_dict)

    return jsonify(prcp_list)
# Convert the query results to a Dictionary using date as the key and prcp as the value.

# Stations
@app.route("/api/v1.0/stations")
def stations():
    """List all stations in the dataset."""
    session = Session(engine)

    # results is a list of lists
    results = session.query(Station.station).order_by(Station.station).all()

    # to make it serializable (list) and flat (NumPy ravel) in JSON
    stations_list = list(np.ravel(results))

    return jsonify(stations_list)

# Temperature Observations (Last Year)
@app.route("/api/v1.0/tobs")
def tobs():
    """List temperature observations for last year."""
    session = Session(engine)

    # calculate last date of measurements data
    lastdate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]

    # calculate date for one year ago before last date
    d = datetime.strptime(lastdate, '%Y-%m-%d') - relativedelta(years=1)
    yearago = d.strftime('%Y-%m-%d')

    # results is a list of lists
    results = session.query(Measurement.tobs).\
        filter(Measurement.date >= yearago).\
        order_by(Measurement.date, Measurement.station).all()
    
    # to make it serializable (list) and flat (NumPy ravel) in JSON
    tobs_list = list(np.ravel(results))

    return jsonify(tobs_list)

# Calculate minimum, average, and maximum temperature for all dates greater 
# than and equal to the start date defined in the URL
@app.route("/api/v1.0/<start>")
def calc_temps_start(start):
    """Minimum, average, and maximum temperature for all dates greater than 
    or equal to <start>."""
    session = Session(engine)

    # results is a list of lists
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    
     # to make it serializable (list) and flat (NumPy ravel) in JSON
    temps_list = list(np.ravel(results))

    return jsonify(temps_list)

# Calculate minimum, average, and maximum temperature for a dates range
@app.route("/api/v1.0/<start>/<end>")
def calc_temps_start_end(start, end):
    """Minimum, average, and maximum temperature for a dates range."""
    session = Session(engine)
    
    # results is a list of lists
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    # to make it serializable (list) and flat (NumPy ravel) in JSON
    temps_list = list(np.ravel(results))

    return jsonify(temps_list)


if __name__ == '__main__':
    app.run(debug=True)
