from flask import Flask, render_template
from flask_bootstrap import Bootstrap

import pymongo
from scrape_mars import scrape

import random

app = Flask(__name__)
bootstrap = Bootstrap(app)

client = pymongo.MongoClient('localhost', 27017)
collection = client.mars_db.scrapes


@app.route('/')
def index():
    mars_info = collection.find().sort('date', pymongo.DESCENDING).limit(1).next()
    print(mars_info)
    return render_template('index.html', info=mars_info)

# @app.route('/scraper')
# def scraper():
#     dict =


if __name__ == '__main__':
    app.run()
