from os import getenv
from datetime import timedelta
import pickle
from flask import Flask, render_template, request
import pickle
import pandas as pd
import psycopg2
from .queries import query_db, recommended_songs
from .queries import DB_PASSWORD, DB_USER, CONNECT, MODEL


def create_app():
    APP = Flask(__name__)
    
    @APP.route("/")
    def root():
        return render_template('home.html', title='Welcome')


    @APP.route("/input")
    def input():
        return render_template('input.html', title='Input')

    
    @APP.route("/about")
    def member():
        return render_template("about.html", title="About Us")


    @APP.route("/model_info")
    def info():
        return render_template("model.html", title="Model Info")


    @APP.route("/recommend", methods=['POST'])
    def recommend():
        
        # Open a connection to the SQL Database
        conn = psycopg2.connect(CONNECT, user=DB_USER, password=DB_PASSWORD)
        cur = conn.cursor()

        # Get the index
        index = request.form["numbers"]
        
        # Use the index value to get your feature array 
        arr = query_db(index, cur)

        # Load the model and find nearest neighbors
        model = pickle.load(open(MODEL, 'rb'))
        distances, indexes = model.kneighbors(X=arr.reshape(1, -1), n_neighbors=6)
        recommendations= recommended_songs(indexes, distances, cur)
        
        # Closes out connection
        cur.close()
        conn.close()

        return render_template('predict.html', df= [recommendations.to_html(index=False, justify='center', classes='table table-striped')], title='Recommendations')

    @APP.route("/predict", methods=['POST'])
    def predict():
        
        inputs = {'artist':request.values['artist'],
            'song':request.values['song'],   
        }

        # Open a connection to the SQL Database
        conn = psycopg2.connect(CONNECT, user=DB_USER, password=DB_PASSWORD)
        cur = conn.cursor()

        # Get the artist query
        artist = inputs['artist'].lower()
        name = inputs['song'].lower()

        index_query = "SELECT index FROM target WHERE name LIKE \'%" + str(name) + "%\' AND artists LIKE \'%" + str(artist) + "%\'"

        # Execute the query
        cur.execute(index_query)
        index = cur.fetchone()

        if index == None:
            return render_template('error.html')
        else:

            # Use the index value to get your feature array 
            arr = query_db(index, cur)

            # Load the model and find nearest neighbors
            model = pickle.load(open(MODEL, 'rb'))
            distances, indexes = model.kneighbors(X=arr.reshape(1, -1), n_neighbors=6)
            recommendations= recommended_songs(indexes, distances, cur)
            
            # Closes out connection
            cur.close()
            conn.close()
            
            return render_template('predict.html', df= [recommendations.to_html(index=False, justify='center', classes='table table-striped')], title='Recommendations')

    return APP