from flask import Flask, jsonify
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)

@app.route("/")
def home():
    return(
        f"Hawaii weather information<br/>"
        f"Included data; Date, Percipitation, Station<br/>"
        f"Start date of the data is 2010-01-01<br/>"
        f"The last date of data is 2017-08-23<br/>"
        f"---------------------------------------<br/>"
        f"Available routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/put_start_date_here (Find the min, max and avg temp from the start date on, Date format is the same as above)<br/>"
        f"/api/v1.0/put_start_date_here/put_end_date_here (Find the min, max and avg temp between two dates, Date format is the same as above)<br/>"
    )
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    sel= [Measurement.date, 
      func.max(Measurement.prcp)]
    results = session.query(*sel).\
        filter(func.date(Measurement.date) >= '2016-08-23').\
        group_by((Measurement.date)).\
        order_by(Measurement.date).all()
    session.close()
    all_prcp = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        all_prcp.append(prcp_dict)

    return jsonify(all_prcp)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station).all()
    session.close()
    all_stations = []
    for station in results:
        all_stations.append(station)
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    most_active = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()

    results = session.query(Measurement.date, Measurement.tobs).\
        filter_by(station = most_active[0]).\
        filter(func.date(Measurement.date) >= '2016-08-23').\
        order_by(Measurement.date).all()
    session.close()

    active_prcp = []
    for date, prcp in results:
        active_prcp.append(date)
        active_prcp.append(prcp)

    return jsonify(active_prcp)

@app.route("/api/v1.0/<start>")
def start_only(start):
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.tobs).all()


    station_min = session.query(func.min(Measurement.tobs)).filter(func.date(Measurement.date) >= start).first()
    station_max = session.query(func.max(Measurement.tobs)).filter(func.date(Measurement.date) >= start).first()
    station_avg = session.query(func.avg(Measurement.tobs)).filter(func.date(Measurement.date) >= start).first()
    return (f"The min, max and avg temperatures from {start} to 2017-08-23 were {station_min[0]}, {station_max[0]}, and {station_avg[0]}")

    session.close()

@app.route("/api/v1.0/<start>/<end>")
def start_and_end(start=None, end=None):
    
    session = Session(engine)
    station_min = session.query(func.min(Measurement.tobs)).filter(func.date(Measurement.date) >= start).\
        filter(func.date(Measurement.date) <= end).first()
    station_max = session.query(func.max(Measurement.tobs)).filter(func.date(Measurement.date) >= start).\
        filter(func.date(Measurement.date) <= end).first()
    station_avg = session.query(func.avg(Measurement.tobs)).filter(func.date(Measurement.date) >= start).\
        filter(func.date(Measurement.date) <= end).first()
    return (f"The min, max and avg temperatures from {start} to {end} were {station_min[0]}, {station_max[0]}, and {station_avg[0]}")
    
    session.close()

if __name__ == "__main__":
    app.run(debug=True)