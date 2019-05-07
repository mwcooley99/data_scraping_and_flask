from flask import Flask, render_template
from flask_bootstrap import Bootstrap

import random

app = Flask(__name__)
bootstrap = Bootstrap(app)

from scrape_mars import scrape

@app.route('/')
def index():
    l = list('ABCDEF')
    choice = random.choice(l)
    return render_template('index.html', choice=choice)

# @app.route('/scraper')
# def scraper():
#     dict =


if __name__ == '__main__':
    app.run()
