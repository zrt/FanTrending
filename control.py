import requests, torch
from config import config
from van import Fan
import datetime

fan = Fan(config['ckey'], config['csecret'])
fan.xauth(config['myuser'], config['mypass'])

wordlist = {}
state = {}
mem = {}

def datetimefromstr(s):
    return datetime.datetime.strptime(s, '%a %b %d %H:%M:%S %z %Y')

def get_day_num(s):
    return int(datetimefromstr(s).strftime('%j'))

def get_today_num():
    return int(datetime.datetime.today().strftime('%j'))

def save_all():
    torch.save(wordlist,'./wordlist.pkl')
    torch.save(state,'./state.pkl')
    torch.save(mem,'./mem.pkl')

def load_all():
    global wordlist
    wordlist = torch.load('./wordlist.pkl')
    global state
    state = torch.load('./state.pkl')
    global mem
    mem = torch.load('./mem.pkl')

def QiRiNianHua(seq):
    ret = [0]*370
    for i in range(len(seq)):
        if seq[i]>0:
            for j in range(7):
                ret[i+j] += seq[i]
    for i in range(len(ret)):
        ret[i] *= 52
    return ret[:367]

def calc_state(word, result):
    cnt = [0]*367
    for x in result:
        if datetimefromstr(x).year == 2018:
            idx = get_day_num(x)
            cnt[idx] += 1
    cnt = QiRiNianHua(cnt)
    return cnt[1:get_today_num()+1]

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
    latest = fan.request('GET', 'search/public_timeline', {'q':word, 'count':60})
    cnt = 200
    while cnt > 0 and len(latest)>0 and latest[-1]['rawid'] > lastid and datetimefromstr(latest[-1]['created_at']).year >= 2018:
        cnt -= 1
        print(200-cnt)
        latest += fan.request('GET', 'search/public_timeline', {'q':word, 'count':60, 'max_id':latest[-1]['id']})[1:]
    
    for x in latest:
        if x['rawid']> lastid:
            mem[word]['status'].append(x['created_at'])
    mem[word]['lastid'] = latest[0]['rawid']
    mem[word]['lastupdate'] = get_today_num()
    
    state[word] = calc_state(word, mem[word]['status'])
    
def update_all():
    load_all()
#     global mem
#     mem = {}
    for w in wordlist:
        print(w)
        update(w)
    save_all()

def addword(w):
    load_all()
    if w in wordlist:
    	return
    wordlist.append(w)
    save_all()
    update_all()


