from flask import Flask, render_template, redirect, url_for
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
    mars_info = collection.find().sort('date', pymongo.DESCENDING).limit(
        1).next()
    return render_template('index.html', info=mars_info)


@app.route('/scraper')
def scraper():
    scrape()
    collection.insert_one(scrape())
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
