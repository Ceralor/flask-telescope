## Telescope 0.1
## Telescope is a "plugin" for Flask that adds Telegram bot support via webhooks
## Commands are defined using the @bot.command("command_name") decorator
## The defined function MUST accept one parameter, which is the Telegram message object
## The defined function MUST return message text, or may return None if no response is needed

from flask import request, jsonify
from functools import wraps
import requests

class Bot(object):
	def __init__(self, flask_app, tg_api_key=None, route_root = "tgbot"):
		if tg_api_key == None:
			self.tg_api_key = flask_app.config["TG_API_KEY"]
		else:
			self.tg_api_key = tg_api_key
		self.route_root = route_root
		self.bot_commands = {}
		self._api_url = "https://api.telegram.org/bot" + self.tg_api_key + "/"
		bot_path = "/" + route_root + "/" + self.tg_api_key
		@flask_app.route(bot_path, methods=["GET","POST"])
		def handle_command_init():
			return self._handle_command()
	def _handle_command(self):
		json_data = request.get_json()
		assert json_data != {}, "Must send valid JSON."
		if "message" in json_data.keys():
			message = json_data["message"]
			chat_id = message["chat"]["id"]
		elif "callback_query" in json_data.keys():
			message = json_data["callback_query"]
			chat_id = message["from"]["id"]
			message["chat"] = message["from"]
			message["text"] = message["data"]
		if message["text"][0:1] != "/":
			response_text = self._handle_default(message)
		else:
			command_end = self._find_command_end(message["text"])
			command_name = message["text"][1:command_end]
			if command_name in self.bot_commands.keys():
				response_text = self.bot_commands[command_name](message)
			else:
				response_text = self._handle_default(message)
		if response_text is not None:
			response_data = {"method": "sendMessage",\
		    	"chat_id": chat_id, "text": response_text, "parse_mode": "Markdown" }
		else:
			response_data = {}
		return jsonify(response_data)
	def _find_command_end(self,message_text):
		command_end = message_text.find(' ')
		if command_end < 2:
			command_end = None
		return command_end
	def _handle_default(self,message):
		if "DEFAULT" in self.bot_commands.keys():
			return self.bot_commands["DEFAULT"](message)
		else:
			return None
	def command(self,command_name):
		def decorator(f):
			self.bot_commands[command_name] = f
			return f
		return decorator
	def find_params(self,message_text):
		command_end = self._find_command_end(message_text)
		if command_end == None:
			return ""
		params_start = command_end + 1
		return message_text[params_start:]
	def send_message(self,chat_id,message,**kwargs):
		payload = {"chat_id" : chat_id, "text" : message}
		if len(kwargs) > 0:
			payload.update(kwargs)
		r = requests.post(self._api_url+"sendMessage", json=payload)
		if r.status_code != 200:
			return (False,None)
		else:
			response = r.json()
			return (response["ok"],response["result"])
