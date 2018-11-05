# Author: Snehith Raj Bada

import sys
from datetime import datetime
import time
import os
import collections
from numpy import vstack,array
from scipy.cluster.vq import kmeans,vq
import io
from flask import Flask, render_template, request
import csv
import sqlite3
import math
import plotly.plotly as py
import plotly.graph_objs as go
import plotly
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as pyplot
from pygal.style import LightStyle

con = sqlite3.connect('database.db')
#Connect to SQL Database
con.execute('CREATE TABLE if not exists earthquake(time VARCHAR(50),latitude DECIMAL,longitude DECIMAL,depth DECIMAL,mag DECIMAL,magType VARCHAR(50),nst int,gap DECIMAL,dmin DECIMAL,rms DECIMAL,id VARCHAR(50),place VARCHAR(50),depthError DECIMAL,magError DECIMAL,magNst int,locationSource VARCHAR(50))')
cur=con.cursor()

# print a nice greeting.
application = Flask(__name__)
IMAGE_FOLDER = os.path.join('static', 'images')
application.config['UPLOAD_FOLDER'] = IMAGE_FOLDER

@application.route('/')
def hello_world():
    filename = os.path.join(application.config['UPLOAD_FOLDER'], 'me.jpg')
    # return render_template("result.html", user_image=filename)
    return render_template('home.html',user_image=filename)
#Method for reading the uploaded csv file
@application.route('/upload', methods=['POST', 'GET'])
def insert_table():
    if request.method == 'POST':
        con = sqlite3.connect('database.db')
        cur = con.cursor()
        f = request.files['data_file']
        if not f:
            return "No file"
        stream = io.StringIO(f.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.reader(stream)
        next(csv_input)
        for row in csv_input:
            print(row)
            try:
                print("Inside try")
                cur.execute(
                    "INSERT INTO earthquake(time, latitude, longitude, depth, mag, magType, nst, gap, dmin, rms, id, place, depthError, magError, magNst, locationSource) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    row)
                con.commit()
                msg = "Record successfully added"
                print(msg)
            except Exception as e:
                print(e)
                con.rollback()
        return render_template('home.html')


@application.route('/getrecords', methods=['POST', 'GET'])
def get_records():
    if request.method == 'POST':
        con=sqlite3.connect('database.db')
        cur = con.cursor()
        cur.execute('''SELECT * from earthquake''')
        rv = cur.fetchall()
        print(len(rv))
        print(rv)
        return render_template("dataeqsmall.html", msg=rv)

#Method to delete all the records
@application.route('/deleterecords', methods=['POST', 'GET'])
def delete_records():
    if request.method == 'POST':
        cur.execute("delete from earthquake")
        con.commit()
        rows = cur.fetchall();
        print(rows)
        return render_template("result.html", msg="All records deleted")

@application.route('/piechart', methods=['POST', 'GET'])
def get_piechart():
    if request.method == 'POST':
        date1 = request.form['date1']
        date2 = request.form['date2']
        mag1,mag2=0,2
        number=[]
        mag=[]
        while(mag2<=6.5):
            cur.execute("select * from earthquake where ((mag between ? and ?) and (time between ? and ?)) ",
                    (mag1,mag2,date1, date2,))
            row=cur.fetchall()
            print(len(row))
            number.append(len(row))
            mag.append(str(mag1)+'-'+str(mag2))
            mag1=mag2
            mag2=mag2+0.5
        print(number)
        print(mag)
    return render_template('piechart.html',zipped_data= number,x2=mag)

@application.route('/cluster', methods=['POST', 'GET'])
def cluster():
   if request.method == 'POST':
       column1=str(request.form['col1'])
       column2=str(request.form['col2'])
       k = str(request.form['cluster'])
       k = int(k)
       dataset = []
       input = csv.reader(open('titanic3.csv', "r"), delimiter=",")
       headers = next(input)
       column1 = headers.index(column1)
       column2 = headers.index(column2)
       for row in input:
           value = []
           if row[column1] != '' and row[column2] != '':
               value.append(float(row[column1]))
               value.append(float(row[column2]))
               dataset.append(value)
       data = vstack(dataset)
       result1=[]
       result2=[]
       result3=[]
       centroids, distortion = kmeans(data, k)
       print(centroids)
       result1.append(centroids)
       distance=[]
       for i in range(1,len(centroids)+1):
           for j in range(i+1,len(centroids)+1):
               print(i,j)
               dvalue = []
               a=centroids[i-1]
               b=centroids[j-1]
               print(a,b)
               dvalue.append(str(i) +"-"+ str(j))
               print(dvalue)
               dist=math.sqrt(abs(((a[0]-a[1])**2)-((b[0]-b[1])**2)))
               print(dist)
               dvalue.append(dist)
               distance.append(dvalue)
       print(distance)
       result2.append(distance)
       indexdata, distance = vq(data, centroids)
       label=collections.Counter(indexdata)
       print(label)

       labels = [(k, v) for k, v in label.items()]
       result3.append(labels)
       mark = ['o']
       for i in range(0, k):
           pyplot.plot(data[indexdata == i, 0], data[indexdata == i, 1], marker=mark[0], ls='none')
       pyplot.plot(centroids[:, 0], centroids[:, 1], 'sm', markersize=8)

       pyplot.savefig('static/images/output.jpg')
       filename = os.path.join(application.config['UPLOAD_FOLDER'], 'output.jpg')
       #return render_template("result.html", user_image=filename)
       return render_template('result1.html', msg1=result1, msg2=result2, msg3=result3,user_image=filename)


if __name__ == '__main__':
    application.run()