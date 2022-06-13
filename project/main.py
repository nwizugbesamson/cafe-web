import os
from flask import Blueprint, flash, render_template, redirect, request, url_for, abort
from project import db
from project.models import User, Cafe, Review, Like
from project.forms import AddForm, ConfirmForm, ReviewForm
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime
import time
import requests


key = os.getenv('API_KEY')


def form_details(user_input):
    url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?"
    
    payload = {
        "fields": "formatted_address,name,opening_hours,photos,place_id",
        "input": user_input,
        "inputtype": "textquery",
        "key": key,
    
    }
    headers = {
    
    }
    try:
        response = requests.get(url, headers=headers, params=payload)

    except IndexError:
        return False
    data = response.json()["candidates"][0]
    address = data["formatted_address"]
    name = data["name"]

    try:
        photo_ref = data["photos"][0]['photo_reference']
        p = requests.get(f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photo_reference={photo_ref}&key={key}")
        img_url = p.url
    except KeyError:
        img_url = False
    place_id = data["place_id"]
    
    d = requests.get(f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&key={key}")
    new_data = d.json()["result"]
    open_hours = new_data["opening_hours"]["weekday_text"][0][8:]
    map_url = new_data["url"]
    info = {
        "name": name,
        "location": address,
        "open_hours": open_hours,
        "map_url": map_url,
    }
    if img_url:
        info["img_url"] = img_url
    return info
    
# ADMIN REQUIRED FUNCTION
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function

main = Blueprint(name="main", import_name=__name__, static_folder="static", template_folder="templates")


@main.route("/")
@main.route("/home")
def home_page():
    page = request.args.get("page", default=1, type=int)
    cafes = Cafe.query.order_by(Cafe.rating).paginate(per_page=10, page=page)
    return render_template("index.html", cafes=cafes)


@main.route('/cafe/<int:_id>', methods=["GET", "POST"])
@login_required
def cafe_page(_id):
    form = ReviewForm()
    
    cafe = Cafe.query.get(_id)
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash('you need to sign in to comment')
            return redirect(url_for('auth.register_page'))
        review = Review(
            review=form.review.data,
            cafe_id=cafe.id,
            user_id=current_user.id,
            date=datetime.now().strftime("%Y %m, %d"),
        )
        db.session.add(review)
        db.session.commit()
    return render_template("cafe.html", cafe=cafe, form=form)


@main.route("/add_cafe", methods=["GET", "POST"])
@login_required
def add_page():
    form = AddForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash('you need to sign in to suggest')
            return redirect(url_for('auth.login_page'))
        name = form.name.data
        return redirect(url_for('main.confirm_page', location=name))
    return render_template("add.html", form=form)


@main.route("/confirm_cafe/<location>", methods=["GET", "POST"])
@login_required
def confirm_page(location):
    info = form_details(user_input=location)
    form = ConfirmForm()
    if info:
        form.name.data = info["name"]
        form.location.data = info["location"]
        form.open_hours.data = info["open_hours"]
        form.img_url.data = info["img_url"]
        form.map_url.data = info["map_url"]
    else:
        flash("cafe cannot be found", category="error")
        return redirect(url_for("main.add_page"))
    cafe = Cafe()
    data_filt = ""
    if form.validate_on_submit():
        setattr(cafe, "user_id", current_user.id)
        form_bools = ["wifi", "phone", "plug", "toilet"]
        for key, value in form.data.items():
            if key in form_bools:
                if value == "True":
                    data_filt += f" {key}"
                    value = bool(value)
                    
                else:
                    value = False
            if key in Cafe.__table__.columns:
                setattr(cafe, key, value)
        setattr(cafe, "filter_class", data_filt)
        setattr(cafe, "rating", 0)
        db.session.add(cafe)
        db.session.commit()
        flash("Cafe added", category="info")
        return redirect(url_for('main.home_page'))
    
    return render_template("confirm.html", form=form)


@main.route('/like/<int:cafe_id>/<action>')
@login_required
def like_page(cafe_id, action):
    cafe = Cafe.query.get(cafe_id)
    if action == "like":
        current_user.like_post(cafe)
        cafe.rating += 1
        db.session.commit()
    if action == "unlike":
        current_user.unlike_post(cafe)
        cafe.rating -= 1
        db.session.commit()
    
    return redirect(request.referrer)


@main.route('/<int:cafe_id>')
@login_required
@admin_required
def delete_page(cafe_id):
    cafe = Cafe.query.get(cafe_id)
    db.session.delete(cafe)
    db.session.commit()

    return redirect(request.referrer)


@main.route("/edit_cafe/<int:_id>", methods=["GET", "POST"])
@login_required
def edit_page(_id):
    cafe = Cafe.query.get(_id)
    form = ConfirmForm()
    
    form.name.data = cafe.name
    form.location.data = cafe.location
    form.open_hours.data = cafe.open_hours
    form.img_url.data = cafe.img_url
    form.map_url.data = cafe.map_url
    
    data_filt = ""
    if form.validate_on_submit():
        form_bools = ["wifi", "phone", "plug", "toilet"]
        for key, value in form.data.items():
            if key in form_bools:
                if value == "True":
                    data_filt += f" {key}"
                    value = bool(value)
                    
                else:
                    value = False
            if key in Cafe.__table__.columns:
                setattr(cafe, key, value)
        setattr(cafe, "filter_class", data_filt)
        db.session.add(cafe)
        db.session.commit()
        flash("Cafe edited", category="info")
        return redirect(url_for('main.home_page'))
    
    return render_template("edit.html", form=form)


@main.route('/my_posts')
@login_required
def my_post_page():
    page = request.args.get("page", default=1, type=int)
    cafes = Cafe.query.paginate(per_page=10, page=page)
    my_cafes = []
    for page in cafes.iter_pages():
        for cafe in cafes:
            if current_user.has_liked_post:
                my_cafes.append(cafe)
    return render_template("index.html", cafes=my_cafes)