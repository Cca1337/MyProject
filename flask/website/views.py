from flask import Blueprint, render_template, request, flash, jsonify, redirect, Response, send_file
from flask_login import login_required, current_user
from .models import Note, Obrazok
from . import db, allowed_file, cache
import json
from engine.weather_forecast_API import get_weather_api
from engine.weather_forecast import get_weather_scrape
from engine.face_detection import generate
from engine.eye_detection import generate1
from engine.stock_prediction import stock_price_prediction
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta


APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static', 'Uploads/')
views = Blueprint('views', __name__)


@views.route('/')
@cache.cached(timeout=300)
#@login_required
def home():

    return render_template("home.html", user=current_user)


@views.route('/delete-note', methods=['POST'])
@login_required
def delete_note():

    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()
            flash(f"Note: {note.data} has been deleted!", category='error')

    return jsonify({})


@views.route('/3D-prints')
@cache.cached(timeout=300)
#@login_required
def gallery():

    return render_template("3d-prints.html", user=current_user)


@views.route('/videos')
@cache.cached(timeout=300)
#@login_required
def videos():

    return render_template("videos.html", user=current_user)


@views.route('/carousel')
@cache.cached(timeout=300)
#@login_required
def carousel():

    return render_template('carousel.html', user=current_user)


@views.route('/sony')
@cache.cached(timeout=300)
#@login_required
def sony():

    return render_template('sony.html', user=current_user)


@views.route('/update/<int:id>', methods=["POST", "GET"])
@login_required
def update(id):

    note = Note.query.get_or_404(id)
    if request.method == "POST":
        note.data = request.form['content']
        db.session.commit()
        flash('Note updated!', category='success')
        return redirect('/notes')
    else:
        return render_template("update.html", note=note, user=current_user)


@views.route('/notes', methods=["POST", "GET"])
@login_required
def notes():

    if request.method == "POST":
        note = request.form.get('note')

        if len(note) < 1:
            flash("Note is tooo short!", category='error')
        else:
            time = datetime.now() + timedelta(hours=2)
            new_note = Note(data=note, date=time, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("notes.html", user=current_user)


@views.route('/weather', methods=["GET", "POST"])
#@login_required
def weather():

    if request.method == "POST":
        mesto = request.form.get('mesto')
        if len(mesto) < 1:
            flash("I bet there is no city which such a short name!", category='error')
        else:
            try:
                pocasie = get_weather_api(mesto)
                flash(f"{pocasie}", category='success')
                return render_template("weather.html", user=current_user, pocasie=pocasie)

            except KeyError as err:
                flash(f"[ERROR] Problem with city name: [{mesto}]. Try again!", category='error')
                return render_template("weather.html", user=current_user)

    return render_template("weather.html", user=current_user)


@views.route('/scrape', methods=["GET", "POST"])
#@login_required
def scrape():

    if request.method == "POST":
        mesto = request.form.get('mesto')

        if len(mesto) < 1:
            flash("I bet there is no city which such a short name!", category='error')
        else:
            try:
                pocasie = get_weather_scrape(mesto)
                flash(f"{pocasie}", category='success')
                return render_template("weather_scrape.html", user=current_user, pocasie=pocasie)

            except AttributeError as err:
                flash(f"[ERROR] Problem with city name: [{mesto}]. Try again!", category='error')
                return render_template("weather_scrape.html", user=current_user)

    return render_template("weather_scrape.html", user=current_user)


@views.route('/face_detection', methods=["POST", "GET"])
#@login_required
def face_detection():

    if request.method == "POST":
        boolean = True
        flash(f"Face detection started!", category='success')
        img = Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')
        return render_template('face_detection.html', user=current_user, boolean=boolean, img=img)

    else:

        return render_template('face_detection.html', user=current_user)


@views.route('/eye_detection', methods=["POST", "GET"])
#@login_required
def eye_detection():
    if request.method == "POST":
        boolean = True
        flash(f"EYE detection started!", category='success')
        img = Response(generate1(), mimetype='multipart/x-mixed-replace; boundary=frame')
        return render_template('eye_detection.html', user=current_user, boolean=boolean, img=img)

    else:

        return render_template('eye_detection.html', user=current_user)


@views.route('/video_feed')
#@login_required
def video_feed():
    try:
        return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

    except RuntimeError as err:
        flash(f"[ERROR]{err} face detection error!", category='error')
        return render_template('face_detection.html', user=current_user)


@views.route('/video_feed1')
#@login_required
def video_feed1():
    try:
        return Response(generate1(), mimetype='multipart/x-mixed-replace; boundary=frame')

    except RuntimeError as err:
        flash(f"[ERROR]{err} Eye detection error!", category='error')
        return render_template('eye_detection.html', user=current_user)


@views.route('/stocks_prediction', methods=["POST", "GET"])
#@login_required
def stocks_predicton():

    if request.method == "POST":

        days = request.form.get('days')
        company = request.form.get('company')
        try:
            days = int(days)

        except ValueError as err:
            flash(f"[ERROR]Cant translate {days} to Int", category='error')

        if days == 0:
            flash(f"You cant get the prediction for 0 days", category='error')

        elif len(company) > 7 or len(company) < 2:
            flash(f"You put [{company}] as a company ticker name which doesnt work", category='error')

        elif days == "":
            flash(f"You cant get the prediction for empty field", category='error')

        else:
            prediction, last_value = stock_price_prediction(days, company)
            link = f"{company}_{days}_prediction.png"
            flash(f"You asked for Stock market value prediction after {days}(day/s) for {company} company! Result is {prediction}. Last known value is {last_value}", category='success')
            return render_template('vysledok.html', user=current_user,last_value=last_value, prediction=prediction, company=company, days=days, link=link)

    return render_template('stocks_prediction.html', user=current_user)


@views.route('/vysledok')
#@login_required
def vysledok():

    return render_template('vysledok.html', user=current_user)


@views.route('/upload', methods=["POST", "GET"])
@login_required
def upload():

    if request.method == "POST":

        file = request.files['inputFile']
        picturename = secure_filename(file.filename)

        if picturename:
            mimetype = picturename.rsplit(".", 1)[1]

            if not allowed_file(picturename):
                flash(f"[{picturename}] Your file extension is not allowed. Are you trying to hack me?:)", category='error')

            else:
                picturename = str(current_user.id) + "_" + picturename
                if os.path.isfile('./website/static/Uploads/' + picturename):

                    flash(f"[{picturename}] Your file already exists in database . Remove it first then upload again?:)", category='error')

                else:

                    file.save(os.path.join(UPLOAD_FOLDER, picturename))
                    text = request.form['text']
                    time = datetime.now() + timedelta(hours=2)
                    newFile = Obrazok(name=picturename,
                                      text=text,
                                      pic_date=time,
                                      user_id=current_user.id,
                                      mimetype=mimetype)
                    db.session.add(newFile)
                    db.session.commit()

                    flash(f'Pic {newFile.name} uploaded Text: {newFile.text} ', category="success")
                    return render_template('upload.html', user=current_user)

        flash(f"[ERROR] No file selected", category='error')

    return render_template('upload.html', user=current_user)


@views.route('/obrazky_update')
@login_required
def obrazky_update():

    return render_template('obrazky_update.html', user=current_user)


@views.route('/delete-picture', methods=['POST'])
@login_required
def delete_picture():

    pic = json.loads(request.data)
    picId = pic['picId']
    pic = Obrazok.query.get(picId)
    if pic:
        if pic.user_id == current_user.id:
            db.session.delete(pic)
            db.session.commit()
            flash(f"Note: {pic.name} has been deleted!", category='error')
    return jsonify({})


@views.route('/return-files/<filename>')
@login_required
def return_files(filename):

    file_path = UPLOAD_FOLDER + filename
    return send_file(file_path, as_attachment=True)

import random

@views.route("/casovac")
@cache.cached(timeout=10)
def casovac():
    _ = random.randint(3,9)
    return str(_)
