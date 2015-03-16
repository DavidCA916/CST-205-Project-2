@route('/media_popular')
def media_popular(): 
    access_token = request.session['access_token']
    content = "<h2>Popular Media</h2>"
    if not access_token:
        return 'Missing Access Token'
    try:
        api = client.InstagramAPI(access_token=access_token)
        media_search = api.media_popular()
        photos = []
        for media in media_search:
            photos.append('<img src="%s"/>' % media.get_standard_resolution_url())
        content += ''.join(photos)
    except Exception as e:
        print(e)              
    return "%s %s <br/>Remaining API Calls = %s/%s" % (get_nav(),content,api.x_ratelimit_remaining,api.x_ratelimit)