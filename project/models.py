from flask_login import UserMixin
from sqlalchemy.orm import relationship
from project import db




class User(db.Model, UserMixin):
    __tablename__ = "users"
    # __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=False, nullable=False)
    password = db.Column(db.String(30), unique=False, nullable=False)
    email = db.Column(db.String(60), unique=True, nullable=False)

    cafes = relationship("Cafe", back_populates="cafe_author")
    reviews = relationship("Review", back_populates="review_author")
    
    liked = db.relationship(
    'Like',
    foreign_keys='Like.user_id',
    backref='users', lazy='dynamic')

    def like_post(self, cafe):
        if not self.has_liked_post(cafe):
            like = Like(user_id=self.id, cafe_id=cafe.id)
            db.session.add(like)

    def unlike_post(self, cafe):
        if self.has_liked_post(cafe):
            Like.query.filter_by(
                user_id=self.id,
                cafe_id=cafe.id).delete()

    def has_liked_post(self, cafe):
        return Like.query.filter(
            Like.user_id == self.id,
            Like.cafe_id == cafe.id).count() > 0


class Cafe(db.Model):
    __tablename__ = "cafe"
    # __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    location = db.Column(db.String(100), unique=False, nullable=False)
    map_url = db.Column(db.String(300), unique=False, nullable=False)
    img_url = db.Column(db.String(300), unique=False, nullable=False)
    open_hours = db.Column(db.String(50), unique=False, nullable=False)
    price = db.Column(db.Integer, unique=False, nullable=False)
    seat = db.Column(db.String(60), unique=False, nullable=False)
    wifi = db.Column(db.Boolean, unique=False, nullable=False)
    plug = db.Column(db.Boolean, unique=False, nullable=False)
    toilet = db.Column(db.Boolean, unique=False, nullable=False)
    phone = db.Column(db.Boolean, unique=False, nullable=False)
    filter_class = db.Column(db.String(100), unique=False, nullable=False)
    rating = db.Column(db.Integer, unique=False, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    cafe_author = relationship("User", back_populates="cafes")
    reviews = relationship("Review", back_populates="cafe")
    likes = relationship('Like', back_populates='cafe', lazy='dynamic')
    


class Review(db.Model):
    __tablename__ = "review"
    # __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    review = db.Column(db.String(300), unique=False, nullable=False)
    date = db.Column(db.String(30), unique=False, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    cafe_id = db.Column(db.Integer, db.ForeignKey("cafe.id"))

    cafe = relationship("Cafe", back_populates="reviews")
    review_author = relationship("User", back_populates="reviews")


class Like(db.Model):
    __tablename__ = "like"
    # __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    cafe_id = db.Column(db.Integer, db.ForeignKey("cafe.id"))

    cafe = relationship('Cafe', back_populates='likes')
    # users = relationship('User', back_populates='liked', lazy='dynamic')