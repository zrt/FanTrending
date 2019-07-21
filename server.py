# encoding=utf-8
import os
import io
import json
import re,random,string
import base64
import control, pickle
from threading import Thread

from flask import Flask, request, abort, render_template, send_file, send_from_directory
from flask_cors import CORS
from config import config
import traceback


webtoken = config['webtoken']
app = Flask(__name__)
# CORS(app)



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

@app.route('/show', methods=['GET'])
def gettrending():
    w = request.args.get('w', '')

    if w not in wordlist:
        abort(403)
        return

    ret = state[w]
    return json.dumps(ret)


ADD_LOCK = False

def do_update():
    global ADD_LOCK
    ADD_LOCK = True
    try:
        control.update_all()
    except Exception as e:
        traceback.print_exc()
        return
    
    global wordlist
    wordlist = get_wordlist()
    global state
    state = get_state()
    ADD_LOCK = False

@app.route('/update', methods=['GET'])
def update():
    token = request.args.get('token', '')
    if token != webtoken:
        abort(403)

    if ADD_LOCK:
        return 'locked'

    thr = Thread(target = do_update)
    thr.start()

    return 'updating...'

@app.route('/queue', methods=['GET'])
def viewnewword():
    token = request.args.get('token', '')
    if token != webtoken:
        abort(403)
        return
    return json.dumps(newwords)


def do_addword(w):
    global ADD_LOCK
    ADD_LOCK = True
    try:
        control.addword(w)
    except Exception as e:
        traceback.print_exc()
        return

    global wordlist
    wordlist = get_wordlist()
    global state
    state = get_state()
    ADD_LOCK = False

@app.route('/add', methods=['GET'])
def newword():
    w = request.args.get('w', '')
    if len(w)>10 or len(w)<2:
        abort(403)
        return 
    t = request.args.get('t', '')
    if t != webtoken:
        newwords.append(w)
        return '已记录, 待审核'
    if ADD_LOCK:
        return 'locked'
    print('+ %s %s'%(w,t))
    thr = Thread(target = do_addword, args = (w,))
    thr.start()

    return 'adding '+w


@app.route('/list', methods=['GET'])
def getlist():
    return json.dumps(wordlist)

@app.route('/', methods=['GET'])
def index():
    return send_file('./public/index.html')

@app.route('/public/<path:path>')
def send_public(path):
    return send_from_directory('public', path)


if __name__ == '__main__':
    # global wordlist
    wordlist = get_wordlist()
    # global state
    state = get_state()
    app.run('127.0.0.1', 8024)
