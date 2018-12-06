import requests, torch
from config import config
from van import Fan

def main():
	fan = Fan(config['ckey'], config['csecret'])
	fan.xauth(config['myuser'], config['mypass'])
	tl = fan.public_timeline()



if __name__ == '__main__':
	main()