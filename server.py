# -*- coding: utf-8 -*-

import os
import io
import json
import re,random,string
import base64
import control,pickle

from flask import Flask, request, abort, render_template, send_file
from flask_cors import CORS
from config import config
webtoken = config['webtoken']
app = Flask(__name__)
CORS(app)

wordlist = []
state = {}
newwords = []

def get_wordlist():
    with open('./wordlist.pkl', 'rb') as f:
        w = pickle.load(f)
    return w

def get_state():
    with open('./state.pkl', 'rb') as f:
        s = pickle.load(f)
    return s

@app.route('/gettrending', methods=['GET'])
def gettrending():
    w = request.args.get('w', '')
    print(w)

    if w not in wordlist:
        abort(403)
        return

    ret = state[w]
    return json.dumps(ret)

@app.route('/update', methods=['GET'])
def update():
    token = request.args.get('token', '')
    if token != webtoken:
        abort(403)
    control.update()
    global wordlist
    wordlist = get_wordlist()
    global state
    state = get_state()
    return 'ok'

@app.route('/viewnewword', methods=['GET'])
def viewnewword():
    token = request.args.get('token', '')
    if token != webtoken:
        abort(403)
        return
    return json.dumps(newwords)

@app.route('/newword', methods=['GET'])
def newword():
    w = request.args.get('w', '')
    if len(w)>10 or len(w)<2:
        abort(403)
        return 
    t = request.args.get('t', '')
    print('+',w)
    if t != webtoken:
        newwords.append(w)
        return '已记录,待审核'
    control.addword(w)
    global wordlist
    wordlist = get_wordlist()
    global state
    state = get_state()
    return 'add '+w


@app.route('/getlist', methods=['GET'])
def getlist():
    return json.dumps(wordlist)


if __name__ == '__main__':
    # global wordlist
    wordlist = get_wordlist()
    # global state
    state = get_state()
    app.run('127.0.0.1', 12233)
