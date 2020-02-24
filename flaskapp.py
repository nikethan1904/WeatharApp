from flask import Flask, request
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
from flask_jsonpify import jsonify
from flask import render_template
from flask import abort
import json
import pandas as pd
from datetime import datetime, timedelta
from dateutil.parser import parse

db_connect = create_engine('sqlite:///daily.db')
app = Flask(__name__)
api = Api(app)

@app.route('/')
def homepage():
    return  render_template('index.html')

@app.route('/historical/', methods=['GET', 'POST'])
def historical():
    if request.method == 'GET':
        dates_list = []
        conn = db_connect.connect()
        query = conn.execute("select DATE from daily")
        my_hist = [i[0] for i in query.cursor.fetchall()]
        for item in my_hist:
            obj = {"DATE":item}
            dates_list.append(obj)
        return jsonify(dates_list)
    else:
        obj = {}
        conn = db_connect.connect()
        query = conn.execute("insert into daily(DATE,TMAX,TMIN) values (?,?,?)",(request.json["DATE"],request.json["TMAX"],request.json["TMIN"]))
        obj = {
            "DATE" : request.json["DATE"]
        }
        return jsonify(obj), 201


@app.route('/historical/<DATE>', methods=['GET','DELETE'])
def get_weather(DATE):
    if request.method == 'DELETE':
        conn = db_connect.connect()
        query = conn.execute("select DATE from daily where DATE=%d" % int(DATE))
        result = [dict(zip(tuple(query.keys()), i)) for i in query.cursor]
        if(len(result)>0):
            query = conn.execute("delete from daily where DATE=%d" % int(DATE))
            return " ", 204
        else:
            abort(404)
    else:
        obj = {}
        conn = db_connect.connect()
        query = conn.execute("select DATE,TMAX,TMIN from daily where DATE =%d" % int(DATE))
        result = [dict(zip(tuple(query.keys()), i)) for i in query.cursor]
        if(len(result)>0):
            for item in result:
                obj = {
                    "DATE": item['date'],
                    "TMAX": item['tmax'],
                    "TMIN": item['tmin']
                }
            return jsonify(obj)
        else:
            abort(404)


@app.route('/forecast/<DATE>')
def forecast_weather(DATE):
    lst_dates = []
    lst_obj = []
    current_date = pd.to_datetime(DATE,format='%Y%m%d')
    stop_date = current_date+timedelta(days=7)
    while current_date<stop_date:
        lst_dates.append(str(pd.to_datetime(current_date)).split(' ')[0].replace("-",""))
        current_date = current_date+timedelta(days=1)
    conn = db_connect.connect()
    for curr_date in lst_dates:
        query = conn.execute("select DATE,TMAX,TMIN from daily where DATE =%d" % int(curr_date))
        result = [dict(zip(tuple(query.keys()), i)) for i in query.cursor]
        if (len(result) > 0):
            for item in result:
                obj = {
                    "DATE": curr_date,
                    "TMAX": item['tmax'],
                    "TMIN": item['tmin']
                }
                lst_obj.append(obj)
        else:
            curr_1 = "2013"+curr_date[4:]
            query = conn.execute("select DATE,TMAX,TMIN from daily where DATE =%d" % int(curr_1))
            result = [dict(zip(tuple(query.keys()), i)) for i in query.cursor]
            for item in result:
                obj = {
                    "DATE": curr_date,
                    "TMAX": item['tmax'],
                    "TMIN": item['tmin']
                }
                lst_obj.append(obj)
        print(lst_obj)
    return jsonify(lst_obj)


if __name__ == '__main__':
     app.run(host='0.0.0.0' , port=5000 , debug="True")

