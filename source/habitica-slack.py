import requests
import json
import datetime
import time
import urllib.parse
import argparse
import appsettings


class HabiticaSlackConnector():
	_lastposttime = 0
	debugmode = False

	def request_chat_data(self): 
		"""Return json from GET request or raise an exception.""" 
		settings = appsettings.HabiticaSlackConnectorSettings()
		r = requests.get( 
		'https://habitica.com/api/v2/groups/party/chat', 
		 headers={ 
			 'x-api-user':settings.habitica_x_api_user, 
			 'x-api-key':settings.habitica_x_api_key
		 } 
		) 
		r.raise_for_status() 
		return r

	def read_last_post_time_stamp(self):
		with open('lastpost.txt', 'r') as f:
			data = f.readline()
		return int(data)
		
	def write_last_post_time(self, lastposttime):
		with open('lastpost.txt', 'w') as f:
			f.write(str(lastposttime))
		return
		
	def update_last_post_if_greater(self, lastposttime):
		if (lastposttime > self._lastposttime):
			self._lastposttime = lastposttime
		return
		
	def get_messages_from_last_hour(self, jsondata, lastposttime):
		parsed_json = json.loads(jsondata)
		for msg in reversed(parsed_json):
			self.update_last_post_if_greater(int(msg['timestamp']))
			if int(msg['timestamp']) > lastposttime:
				print (msg['text'].encode('utf8'))
				self.push_to_slack(msg['text'])
		return
		
	def push_to_slack(self, text):
		settings = appsettings.HabiticaSlackConnectorSettings()
		target_url = settings.slack_url
		payload_data =  '{"text": "' + text + '"}'
		#payload_data = urllib.parse.quote_plus(payload_data)
		print (payload_data.encode('utf8'))
		if (self.debugmode == False):
			r = requests.post(target_url, headers={"content-type":"application/json"}, data=payload_data.encode('utf-8'))
			print (r)
			print (r.text)

		
if __name__ == "__main__":
	connector = HabiticaSlackConnector()
	parser = argparse.ArgumentParser(description='Habitica-Slack')
	parser.add_argument("--debug", help="Run in debug mode, do not send email", action="store_true")
	args = parser.parse_args()
	if (args.debug):
		print ("Running in debug mode")
		connector.debugmode = True
		

	lastposttime = connector.read_last_post_time_stamp()
	connector.get_messages_from_last_hour (connector.request_chat_data().text, lastposttime)
	connector.write_last_post_time(connector._lastposttime)
