##################################################################
#        MESURE DU TAUX D'OCCUPATION DE PARKINGS A L'AIDE        #
#                       DE CAMERAS VIDEOS                        #
# -------------------------------------------------------------- #
#              Rémi Jacquemard - TB 2018 - HEIG-VD               #
#                   remi.jacquemard@heig-vd.ch                   #
#               https://github.com/remij1/TB_2018                #
#                           July 2018                            #
# -------------------------------------------------------------- #
# Main app exposing a REST API. A user can request the root      #
# endpoint to get the current parking state.                     #
# A JSON is sent back to the client:                             # 
# {                                                              #
#     'date':'2018-07-12 12:12:14',                              #
#     'num_cars': 4,                                             #
#     'free_place': 18,                                          #
#     'occupied_rate': 0.432                                     #
# }                                                              #
##################################################################

from flask import Flask, jsonify
from time import strftime, gmtime
import pymongo
import datetime

MAX_NUM_CARS = 23

VALUES_LENGTH = 4

# Database
uri = "mongodb://heig-park:rl5N71ZE5Lvid9MA1lA4O03e7TKDIgA47cuwrcjsN08PAgBrQBrYBOAdPvCqGlHTqbrxHofatBvNoAF0hb9tDQ==@heig-park.documents.azure.com:10255/?ssl=true&replicaSet=globaldb"
client = pymongo.MongoClient(uri)
stats = client['heig-park']['stats']

# values = []

"""
def add_db_value(value):
    obj = {
        "date": datetime.datetime.utcnow(),
        "nb_cars": value
    }

    obj_id = stats.insert_one(obj).inserted_id
    print("{} cars, stored within database with id {}".format(obj["nb_cars"], obj_id))

def add_value(value):
    values.insert(0, value)
    if len(values) > VALUES_LENGTH:
        values.pop()

    # adding to db
    add_db_value(value)
"""

def current_num():
    # getting last 4 values from db
    values = stats.find().sort("date",pymongo.DESCENDING).limit(4)

    if len(values) == 0:
        return 0

    return round(sum(map(lambda val : val['nb_cars'], values)) / len(values))


app = Flask(__name__)

@app.route("/")
def root():
    cur_num = current_num()

    free_place = MAX_NUM_CARS - cur_num
    if free_place < 0:
        free_place = 0
    
    occupied_rate = (MAX_NUM_CARS - free_place) / MAX_NUM_CARS

    obj = {
        'date':strftime("%Y-%m-%d %H:%M:%S", gmtime()),
        'num_cars': cur_num, 
        'free_place': free_place,
        'occupied_rate': occupied_rate
    }
    return jsonify(obj)

if __name__ == '__main__':
    app.run(debug=False, port=80, host='0.0.0.0')
