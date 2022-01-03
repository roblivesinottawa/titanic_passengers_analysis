from io import BytesIO
from flask import Flask, render_template, send_file, make_response, json
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import numpy as np
import pandas as pd
import pymysql
# import mysql.connector
# from mysql.connector import Error
import matplotlib.pyplot as plt
plt.style.use('ggplot')

app = Flask(__name__)   # create the Flask app

# def connect():
#     global connection
#     try:
#         connection = mysql.connector.connect(host='localhost',
#                                             database='tested_db',
#                                             user='root',
#                                             password='mysqlpassmacrob')

#         if connection.is_connected():
#             db_Info = connection.get_server_info()
#             print("Connected to MySQL Server version ", db_Info)
#             cursor = connection.cursor()
#             cursor.execute("select database();")
#             record = cursor.fetchone()
#             print("You're connected to database: ", record)
#     except Error as e:
#         print("Error while connecting to MySQL", e)
#     # finally:
#     #     if  connection.is_connected():
#     #         cursor.close()
#     #         connection.close()
#     #         print("MySQL connection is closed")

# connect()

c = pymysql.connect(host='localhost',
                    user='root',
                    password='mysqlpassmacrob',
                    db='titanic_info')



@app.route('/')
def index():
    """this function renders the index.html file"""
    df = pd.read_sql("SELECT * FROM passengers", con=c)
    return render_template('index.html', data=df.head(10).to_html())


@app.route('/analysis')
def passenger_class():
    df = pd.read_sql("SELECT * FROM passengers", con=c)
    gender_results = df.groupby('Sex').size()
    gender_new_df = pd.DataFrame(gender_results)
    class_results = df.groupby(['Pclass'])['Pclass'].count()
    class_new_df = pd.DataFrame(class_results)
    pass_class_gender_group_df = df.groupby(['Pclass'])['Sex'].count()
    unstacked_df = pass_class_gender_group_df.unstack('Pclass').T   #unstack results then tranpose
    pass_class_gender_new_df = pd.DataFrame(unstacked_df, columns=['female', 'male'])
    return render_template('analysis.html', gender_df = gender_new_df.to_html(), 
                                            passengers_df=class_new_df.to_html(), 
                                            passengers_gender_df=pass_class_gender_new_df.to_html())


@app.route('/gender_pie_chart/')
def gender_pie_chart():
    df = pd.read_sql("SELECT * FROM passengers", con=c)
    data=df.groupby(['Sex'])['Sex'].count()
    gender_labels=['Female','Male']
    fig,ax=plt.subplots()
    gender_color = ['r','g']
    ax.pie(data, labels=gender_labels, colors=gender_color,autopct='%1.1f%%', startangle=90, shadow= False)
    plt.axis('equal')
    canvas = FigureCanvas(fig)
    img = BytesIO()
    fig.savefig(img)
    img.seek(0)
    return send_file(img, mimetype='image/png')


@app.route('/class_bar_graph/')
def class_bar_graph():
    df = pd.read_sql("SELECT * FROM passengers", con=c)
    new_df=df.groupby(['Pclass'])['Pclass'].count()
    pclass=new_df[0:]
    new_df=df.groupby(['Pclass'])['Pclass'].count()
    fig, ax = plt.subplots()
    ax = pclass.plot(kind='bar', color = ['r','g','y'], fontsize=12)
    ax.set_xlabel("Passenger Class (Pclass)", fontsize=12)
    ax.set_ylabel("Population", fontsize=12)
    canvas = FigureCanvas(fig)
    img = BytesIO()
    fig.savefig(img)
    img.seek(0)
    return send_file(img, mimetype='image/png')
 

@app.route('/class_gender_bar_graph/')
def class_gender_bar_graph():
    df = pd.read_sql("SELECT * FROM passengers", con=c)
    group_df=df.groupby(['Pclass','Sex'])['Sex'].count()
    unstacked_df=group_df.unstack('Pclass').T 
    new_df=pd.DataFrame(unstacked_df,columns=['female','male']) 
    fig, ax = plt.subplots()
    ax = new_df[['female','male']].plot(kind='bar',color = ['r','g'], legend=True, fontsize=12)
    ax.set_xlabel("Passenger Class (Pclass)", fontsize=12)
    ax.set_ylabel("Population", fontsize=12)
    canvas = FigureCanvas(fig)
    img = BytesIO()
    fig.savefig(img)
    img.seek(0)
    return send_file(img, mimetype='image/png')
     
@app.route('/visualization')
def visualization():
    return render_template('visualization.html')
 

if __name__=='__main__':
    app.run(debug=True)