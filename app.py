# -*- coding: utf-8 -*-
# _____________________________________________________________________________
# _____________________________________________________________________________
#
#                       Coded by: Daniel Gonzalez-Duque
#                               Last revised 2022-05-20
# _____________________________________________________________________________
# _____________________________________________________________________________
"""
______________________________________________________________________________

 DESCRIPTION:
    This script creates a plot selector embedded in Tkinter to select possible
    meander points

______________________________________________________________________________
"""
# ----------------
# Import packages
# ----------------
# Data
import sys
import os
import uuid

import psycopg2

# Data
import pandas as pd
import numpy as np
from Database import Database

# Web
from flask import Flask, render_template, request, session

try:
    from dotenv import load_dotenv
    load_dotenv()
except ModuleNotFoundError:
    print("Couldn't load the local .env file.")

# -----------------------
# Load variables
# -----------------------
db_url = os.environ['DATABASE_URL']

db = psycopg2.connect(db_url)
database = Database(db)
database.create_meander_table()
db.close()
# -----------------------
# Web App
# -----------------------
app = Flask(__name__)

app.secret_key = os.environ['SECRET_KEY']

@app.route('/')
def root():
    if "user_id" not in session:
        session["user_id"] = uuid.uuid1()
    return render_template("index.html")


@app.route('/submission', methods=['POST'])
def submission():
    print('Getting Data')
    data = request.get_json()
    data = pd.read_json(data)
    db = psycopg2.connect(db_url)
    database = Database(db)
    database.new_entry(data)
    print('submitted')
    database.close()
    db.close()
    return 'Updated'

@app.route('/submitted')
def submitted():
    return render_template('submitted.html')


if __name__ == "__main__":
    print("Serving Web App")
    app.run()