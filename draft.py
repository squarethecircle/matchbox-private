from flask import render_template
from app import app

@app.route('/')
@app.route('/draft')
def index():
    return render_template('draft.html',
                            boy='Thomas Kilmer',
                            girl='Aretha Guo',
                            boypp='Tommy.jpg',
                            girlpp='Aretha.jpg'
                            )
