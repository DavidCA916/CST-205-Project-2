import os
import time
from instagram.client import InstagramAPI
from flask import Flask, request, render_template, session, redirect, abort, flash, jsonify

app = Flask(__name__)   # create our flask app
app.secret_key = 'c\xa7\xe8\xc6\xc7.\x0cr\x00\xb4\xf2"\x89FL\xcf\x01\xbe2|P&#\x82'


# configure Instagram API
instaConfig = {
	'client_id' : 'a3010e12a8fa4f428541358d83a0716a',
	'client_secret' : 'c245cc783d4743caa9032a3c23afac6b',
	'redirect_uri' : 'https://shielded-brushlands-9106.herokuapp.com/instagram_callback'
}
api = InstagramAPI(**instaConfig)

@app.route('/')
def home():
	if 'instagram_access_token' in session:
		return render_template('home.html')

	else:

		return redirect('/connect')


@app.route('/ownphotos')
def user_photos():

	# if instagram info is in session variables, then display user photos
	if 'instagram_access_token' in session and 'instagram_user' in session:
		userAPI = InstagramAPI(access_token=session['instagram_access_token'])
		recent_media, next = userAPI.user_recent_media(user_id=session['instagram_user'].get('id'),count=25)

		templateData = {
			'size' : request.args.get('size','thumb'),
			'media' : recent_media,
			 'title' : "User\'s Photos"
		}

		return render_template('display.html', **templateData)
		

	else:

		return redirect('/connect')


@app.route('/popular')
def popular_photos():

	# if instagram info is in session variables, then display popular photos
	if 'instagram_access_token' in session:
		userAPI = InstagramAPI(access_token=session['instagram_access_token'])
		media_search = api.media_popular(count=25)

		templateData = {
			'size' : request.args.get('size','thumb'),
			'media' : media_search,
			'title' : "Popular Photos -"
		}

		return render_template('display.html', **templateData)
		
	else:
		return redirect('/connect')


@app.route('/feed')
def feed_photos():

	# if instagram info is in session variables, then display popular photos
	if 'instagram_access_token' in session:
		userAPI = InstagramAPI(access_token=session['instagram_access_token'])
		user_feed, next = userAPI.user_media_feed(count=25)

		templateData = {
			'size' : request.args.get('size','thumb'),
			'media' : user_feed,
			'title' :  "User\'s Feed -"
		}

		return render_template('display.html', **templateData)
		
	else:
		return redirect('/connect')


# Redirect users to Instagram for login
@app.route('/connect')
def main():

	url = api.get_authorize_url(scope=["likes","comments"])
	return redirect(url)

# Instagram will redirect users back to this route after successfully logging in
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
