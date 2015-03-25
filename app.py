import os
import time
from instagram.client import InstagramAPI
from flask import Flask, request, render_template, session, redirect, abort, flash, jsonify

app = Flask(__name__)   # Creates the Flask app
app.secret_key = os.environ['FLASK_SECRET']


# Sets the API keys and callback URL. API keys are stored on the Heroku servers
# and accessed via the variables ID and SECRET
instaConfig = {
	'client_id' : os.environ['ID'],
	'client_secret' : os.environ['SECRET'],
	'redirect_uri' : 'https://cst205project2.herokuapp.com/instagram_callback'
}
api = InstagramAPI(**instaConfig)
num_photos = 12 # Sets the number of photos output per page to 12

@app.route('/') # App homepage
def home():
	if 'instagram_access_token' in session and 'instagram_user' in session: # Checks if user logged in
		userAPI = InstagramAPI(access_token=session['instagram_access_token']) # Sets the token to the API
		user_info = userAPI.user(user_id=session['instagram_user'].get('id')) # Sets the user ID to the API

		templateData = {
			'media' : user_info # Loads user's info (username, picture, etc.)
		}

		return render_template('home.html', **templateData) # Renders the home.html page using the templateData

	else: # Makes user login, if not logged in
		return redirect('/connect')


@app.route('/ownphotos') # Page that display's the user's photos
def user_photos():
	if 'instagram_access_token' in session and 'instagram_user' in session: # Checks if user is logged in
		userAPI = InstagramAPI(access_token=session['instagram_access_token']) # Sets the token to the API
		recent_media, next = userAPI.user_recent_media(user_id=session['instagram_user'].get('id'),count=num_photos) # Sets the user ID and count of photos (to 12 from variable)

		templateData = {
			'size' : request.args.get('size','thumb'),
			'media' : recent_media, # Loads user's pictures
			'title' : "User\'s Photos - " # Sets title of HTML page via variable
		}

		return render_template('display.html', **templateData) # Renders the display.html page using templateData
		

	else: # Makes user login, if not logged in
		return redirect('/connect')


@app.route('/popular')
def popular_photos():
	if 'instagram_access_token' in session: # Checks if user logged in
		userAPI = InstagramAPI(access_token=session['instagram_access_token']) # Sets the token to the API
		media_search = api.media_popular(count=num_photos) # Gets popular media in count 12

		templateData = {
			'size' : request.args.get('size','thumb'),
			'media' : media_search, # Loads popular photos
			'title' : "Popular Photos -" # Sets title of HTML page via variable
		}

		return render_template('display.html', **templateData) # Renders display.html page using templateData
		
	else: # Makes user login, if not logged in
		return redirect('/connect')


@app.route('/feed')
def feed_photos():
	if 'instagram_access_token' in session: # Checks if user logged in
		userAPI = InstagramAPI(access_token=session['instagram_access_token']) # Sets the token to the API
		user_feed, next = userAPI.user_media_feed(count=num_photos) # Gets user's feed in count 12

		templateData = {
			'size' : request.args.get('size','thumb'),
			'media' : user_feed, # Loads user's feed
			'title' :  "User\'s Feed -" # Sets title of HTML page via variable
		}

		return render_template('display.html', **templateData) # Renders display.html page using templateData
		
	else: # Makes user login, if not logged in
		return redirect('/connect')


# Redirects users to Instagram to login
@app.route('/connect')
def main():

	url = api.get_authorize_url(scope=["likes","comments"])
	return redirect(url)

# Takes you back to the app once you're logged in to Instagram
@app.route('/instagram_callback')
def instagram_callback():

	code = request.args.get('code')

	if code:

		access_token, user = api.exchange_code_for_access_token(code)
		if not access_token:
			return 'Could not get access token'

		app.logger.debug('got an access token')
		app.logger.debug(access_token)

		# Sessions are used to keep this data 
		session['instagram_access_token'] = access_token
		session['instagram_user'] = user

		return redirect('/') # redirect back to main page
		
	else:
		return "Uhoh no code provided"
	
@app.errorhandler(404)
def page_not_found(error):
	return render_template('404.html'), 404


# This is a jinja custom filter
@app.template_filter('strftime')
def _jinja2_filter_datetime(date, fmt=None):
	pyDate = time.strptime(date,'%a %b %d %H:%M:%S +0000 %Y') # convert instagram date string into python date/time
	return time.strftime('%Y-%m-%d %h:%M:%S', pyDate) # return the formatted date.
	
# --------- Server On ----------
# start the webserver
if __name__ == "__main__":
	app.debug = True
	
	port = int(os.environ.get('PORT', 5000)) # locally PORT 5000, Heroku will assign its own port
	app.run(host='0.0.0.0', port=port)
