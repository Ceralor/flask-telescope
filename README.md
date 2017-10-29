# README #

Telescope is a small module for Flask that adds a decorator class for defining Telegram bot commands when using webhooks for the bot.

### How do I get set up? ###

Clone the repo within your project folder to have `$project/telescope`. If you don't already have Flask installed, you can use one of the following:

	pip install flask
	pip install -r telescope/requirements.txt

In your project, do the below:

	from flask import Flask
	from telescope import Bot
	app = Flask(__name__)
	TG_BOT_API = "your_telegram_bot_api_key"
	bot = Bot(app,TG_BOT_API)

That's it! You can then use the `@bot.command("command")` decorator before the function you wish for the specified command to call, just like using `@app.route("/some-path")` in Flask.

Of note, your method MUST accept one argument, the Telegram message object, and return `None` if no response is required or a string containing the response message. You can also `return None` if you are manually sending a response.