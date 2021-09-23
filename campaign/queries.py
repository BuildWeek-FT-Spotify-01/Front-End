from os import getenv
import pickle
import pandas as pd
import numpy as np
import psycopg2


# Create a connection to the SQL Database

DB_PASSWORD = getenv('PASSWORD')
DB_USER = getenv('DB_USER')
CONNECT = getenv('CONNECT')
MODEL = getenv('MODEL')

# def query_artist(name, artist):

#     """This will call the name and artist that is input from the webpage
#     and return an array of information about the song"""
    
#     # Query the database and return an index
#     index_query = "SELECT index FROM target WHERE name = \'" + str(name) + "\' AND artists = \'" + str(artist) + "\'"  
#     # cur.execute(index_query)
#     # results = cur.fetchone()

#     return str(index_query)

def query_db(index, cur):

    """This function will take an index input and then return an array of information based on the index""" 

    query_db = "SELECT danceability, energy, key, loudness, mode, speechiness, acousticness, instrumentalness, liveness, valence, tempo, duration_ms from features WHERE index = \'" + str(index[0]) + "\'"
    cur.execute(query_db)
    results = cur.fetchone()
    results_list = list(results)
    results_list[-1] = results_list[-1] / 6061090
    results_list[2] = results_list[2] / 11
    results_list[3] = (results_list[3] - (-60.0)) / (7.234 - (-60.0))
    results_list[10] = results_list[10] / 248.934
    arr = np.array(results_list)
    
    return arr

def recommended_songs(indexes, distances, cur):

    """ This function will take in index values and then return 
        a list of song and artist names"""

    # Queries the database 
    query = "SELECT name, artists FROM target WHERE index IN ("
    first = True
    for index in indexes[0][1:]:
      if first == False:
        query = query + ', ' + str(index)
      else:
        first = False
        query = query + str(index)
    query = query + ")"

    # Creates the dataframe
    data = {'name':[], 'artists':[], 'distances': distances[0][1:]}
    cur.execute(query)
    records = cur.fetchall()
    for record in records:
      data['name'].append(record[0])
      data['artists'].append(record[1])
    
    recommendations = pd.DataFrame(data)

    return recommendations