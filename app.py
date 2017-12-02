from flask import Flask, session, render_template, redirect, request, g, jsonify
import os 
import sys
from scrape import *

app = Flask(__name__)

name = 'index'

#index page 
@app.route('/')
def index():
    return render_template('index.html', name=name)

@app.route('/getinfo', methods=['POST'])
def getinfo():
    strUser = request.form['user']
    strPass = request.form['pass']
    strDate = request.form['date']

    jsondata = get_detsch(strUser, strPass, strDate)
    if(jsondata != None):
        return jsondata
    else:
        return "Login failed, check userid and password"

#get schedule details
@app.route('/api-sch')
def api_sch():
    user = request.args.get('user')
    passw = request.args.get('pass') 
    date = request.args.get('date')

    jsondata = get_detsch(user, passw, date)
    if(jsondata != None):
        return jsondata
    else:
        return "Login failed, check userid and password"
    

#404
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0')