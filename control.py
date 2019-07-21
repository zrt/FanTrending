# encoding=utf-8

import requests, pickle
from config import config
from van import Fan
import datetime

fan = Fan(config['ckey'], config['csecret'])
fan.xauth(config['myuser'], config['mypass'])

wordlist = []
state = {}
mem = {}

t_out = (60,60)

def datetimefromstr(s):
    return datetime.datetime.strptime(s, '%a %b %d %H:%M:%S %z %Y')

def get_day_num(s):
    return int(datetimefromstr(s).timestamp())//SECONDS_PER_DAY

SECONDS_PER_DAY = 60*60*24

def get_today_num():
    return int(datetime.datetime.now().timestamp())//SECONDS_PER_DAY

def save_all():
    with open('./wordlist.pkl', 'wb') as f:
        pickle.dump(wordlist,f,True)
    with open('./state.pkl', 'wb') as f:
        pickle.dump(state,f,True)
    with open('./mem.pkl', 'wb') as f:
        pickle.dump(mem,f,True)

def load_all():
    global wordlist
    with open('./wordlist.pkl', 'rb') as f:
        wordlist = pickle.load(f)
    global state
    with open('./state.pkl', 'rb') as f:
        state = pickle.load(f)
    global mem
    with open('./mem.pkl', 'rb') as f:
        mem = pickle.load(f)

def QiRiNianHua(mp):
    today = int(datetime.datetime.now().timestamp())//SECONDS_PER_DAY
    seq = [0]*360
    for i in range(360):
        if today - i in mp:
            seq[360-i-1] = mp[today - i]
    ret = [0]*370
    for i in range(len(seq)):
        if seq[i]>0:
            for j in range(7):
                ret[i+j] += seq[i]
    for i in range(len(ret)):
        ret[i] *= 52
    return ret[:360]


def calc_state(word, result):
    cnt = {}
    for x in result:
        idx = int(datetimefromstr(x).timestamp()) // SECONDS_PER_DAY
        if idx in cnt:
            cnt[idx] += 1
        else:
            cnt[idx] = 1
    cnt = QiRiNianHua(cnt)
    return cnt

def update(word):
    if word in mem and 'lastupdate' in mem[word] and mem[word]['lastupdate'] == get_today_num():
        state[word] = calc_state(word, mem[word]['status'])
        return
    if word not in mem:
        mem[word] = {}
    if 'status' not in mem[word]:
        mem[word]['status'] = []
    if 'lastid' not in mem[word]:
        mem[word]['lastid'] = -1
    lastid = mem[word]['lastid']
    latest = fan.request('GET', 'search/public_timeline', {'q':word, 'count':60}, timeout=t_out)
    cnt = 1000
    if len(latest)>0:
        mem[word]['lastid'] = latest[0]['rawid']
    for x in latest:
        if x['rawid']> lastid:
            mem[word]['status'].append(x['created_at'])
    while cnt > 0 and len(latest)>1 and latest[-1]['rawid'] > lastid and get_today_num() - get_day_num(latest[-1]['created_at']) < 360:
        cnt -= 1
        print('get..', 1000-cnt)
        latest = fan.request('GET', 'search/public_timeline', { 'q':word, 'count':60, 'max_id':latest[-1]['id']}, timeout=t_out)[1:]
        for x in latest:
            if x['rawid']> lastid:
                mem[word]['status'].append(x['created_at'])
    
    mem[word]['lastupdate'] = get_today_num()
    state[word] = calc_state(word, mem[word]['status'])
    
def update_all():
    load_all()
#     global mem
#     mem = {}
    for w in wordlist:
        # print(w)
        update(w)
    save_all()

def addword(w):
    load_all()
    if w in wordlist:
    	return
    wordlist.append(w)
    save_all()
    update_all()

