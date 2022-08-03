#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from unicodedata import name
import dateutil.parser
import babel
from flask import render_template, request, flash, redirect, url_for

from Model import *
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from datetime import datetime


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
 
  donnees = Venue.query.all()
  data =[]
  data_id = []
  for element in donnees:
    liste = {
      "city": element.city,
      "state": element.state,
      "venues": Venue.query.filter(Venue.city==element.city and Venue.state == element.state)
    }
    
    data.append(liste)




  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  response = {'data' : Venue.query.filter(Venue.name.ilike('%' + request.form['search_term'] + '%')).all(),
  'count': Venue.query.filter(Venue.name.ilike('%' + request.form['search_term'] + '%')).count()}
 
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  venue = Venue.query.filter_by(id= venue_id).first()
  element = { #formatting the important dictionary data
    "id": venue.id,
    "name": venue.name, 
    "city":venue.city, 
    "state": venue.state, 
    "genres": venue.genres,
    "address": venue.address,
    "phone": venue.phone, 
    "website_link": venue.website_link, 
    "image_link" : venue.image_link,
    "looking_talent" : venue.looking_talent,
    "seeking_description": venue.seeking_description,
    "facebook_link": venue.facebook_link,
    "show": venue.show
  }
  data = []

  element["past_show"]=[]
  element["upcoming_show"]=[]
  start_time = Show.query.order_by('start_time').first().start_time
  past_shows_query = db.session.query(Show).join(Venue).filter(Show.venue_id==venue_id).filter(datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")<datetime.now()).all()
  upcoming_shows_query = db.session.query(Show).join(Venue).filter(Show.venue_id==venue_id).filter(datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")>datetime.now()).all()


  element["past_shows_count"]=len(past_shows_query)
  element["past_shows"]=past_shows_query
  element["upcoming_shows"]=upcoming_shows_query
  element["upcoming_shows_count"]=len(upcoming_shows_query)
  data.append(element)


  
  data = list(filter(lambda d: d['id'] == venue_id, data))[0]
  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    
  # TODO: insert form data as a new Venue record in the db, instead
    looking_talent = True if request.form.get('looking_talent') == 'y' else False
    venue = Venue(name=request.form.get('name'), city=request.form.get('city'), state=request.form.get('state'), address=request.form.get('address'), phone=request.form.get('phone'), genres=request.form.get('genres'), image_link=request.form.get('image_link'), facebook_link=request.form.get('facebook_link'), website_link=request.form.get('website_link'), looking_talent=looking_talent, seeking_description=request.form.get('seeking_description'))
    try : 
      db.session.add(venue)
      db.session.commit()
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
  # TODO: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
      db.session.rollback()
    finally:
      db.session.close()
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:    
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
   
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
    return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
 
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response = {'data' : Artist.query.filter(Artist.name.ilike('%' + request.form['search_term'] + '%')).all(),
  'count': Artist.query.filter(Artist.name.ilike('%' + request.form['search_term'] + '%')).count()}
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.filter_by(id= artist_id).first()
  element = {
    "id": artist.id,
    "name": artist.name, 
    "city":artist.city, 
    "state": artist.state, 
    "phone": artist.phone, 
    "genres": artist.genres,
    "website": artist.website_link, 
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.looking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "show": artist.show
  }
  data = []

  element["past_shows"]=[]
  element["upcoming_shows"]=[]
  sd=[]
  ups =[]
  for e in element["show"]:
    if(datetime.strptime(e.start_time, "%Y-%m-%d %H:%M:%S")<datetime.now()):
      sd.append({"venue_id": e.venue_id,
      "venue_name": e.venue.name,
      "venue_image_link": e.venue.image_link,
      "start_time": e.start_time})
    else:
        ups.append({"venue_id": e.venue_id,
        "venue_name": e.venue.name,
        "venue_image_link": e.venue.image_link,
        "start_time": e.start_time})
  if(len(sd)>0):
      element["past_shows"]=sd
  if(len(ups)>0):
      element["upcoming_shows"] = ups
    
  element["past_shows_count"]=len(sd)
  element["upcoming_shows_count"]=len(ups)
  
  data.append(element)


  data = list(filter(lambda d: d['id'] == artist_id, data))[0]
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()

  # TODO: populate form with fields from artist with ID <artist_id>
  artist = Artist.query.filter_by(id = artist_id).first()
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist = Artist.query.filter_by(id = artist_id).first()
  artist.name = request.form.get('name')
  artist.city = request.form.get('city')
  artist.state = request.form.get('state')
  artist.phone = request.form.get('phone')
  artist.genres = request.form.get('genres')
  artist.facebook_link = request.form.get('facebook_link')
  artist.image_link = request.form.get('image_link')
  artist.website_link = request.form.get('website')
  artist.seeking_description = request.form.get("seeking_description")
  artist.looking_venue = True if request.form.get('seeking_venue') == 'y' else False
  db.session.commit()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  
  venue = Venue.query.filter_by(id = venue_id).first()
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.filter_by(id = venue_id).first()
  venue.name = request.form.get('name')
  venue.city = request.form.get('city')
  venue.state = request.form.get('state')
  venue.phone = request.form.get('phone')
  venue.genres = request.form.getlist('genres')
  venue.facebook_link = request.form.get('facebook_link')
  venue.image_link = request.form.get('image_link')
  venue.website_link = request.form.get('website_link')
  venue.looking_talent = True if request.form.get('seeking_talent') == 'y' else False
  venue.seeking_description = request.form.get('seeking_description')
  db.session.commit()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    looking_venue = True if request.form.get('seeking_venue') == 'y' else False
    artist = Artist(name=request.form.get('name'), city=request.form.get('city'), state=request.form.get('state'), phone=request.form.get('phone'), genres=request.form.get('genres'), facebook_link=request.form.get('facebook_link'), image_link=request.form.get('image_link'), website_link=request.form.get('website_link'), looking_venue=looking_venue, seeking_description=request.form.get('seeking_description'))
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name']+ ' could not be listed.')
  finally:
    db.session.close()
  # on successful db insert, flash success
   
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return redirect(url_for('index'))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
 
  data = Show.query.all()
  donnees = []

  for element in data:
    d = {
      "venue_id": element.venue_id,
      "venue_name": element.venue.name, 
      "artist_id": element.artist_id, 
      "artist_name": element.artist.name,
      "artist_image_link":element.artist.image_link,
      "start_time": element.start_time
    }
    donnees.append(d)
  return render_template('pages/shows.html', shows=donnees)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
    
    try:   
        show = Show(venue_id=request.form.get('venue_id'), artist_id=request.form.get('artist_id'), start_time=request.form.get('start_time'))
        db.session.add(show)
        db.session.commit()  
  # on successful db insert, flash success
        flash('Show was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. Show could not be listed.'+request.form.get('venue_id')+request.form.get('artist_id')+request.form.get('start_time'))
    finally:
        db.session.close()
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html', shows=show)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.debug = True
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
