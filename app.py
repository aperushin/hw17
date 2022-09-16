from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields
from marshmallow.exceptions import ValidationError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['RESTX_JSON'] = {'ensure_ascii': False, 'indent': 2}
db = SQLAlchemy(app)

api = Api(app)
movies_ns = api.namespace('movies')


def filter_dict(dictionary: dict, allowed_keys: list | tuple) -> dict:
    """
    Remove key from a dictionary if it is not in the list of allowed keys.
    """
    return {k: v for k, v in dictionary.items() if k in allowed_keys}


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class MovieSchema(Schema):
    id = fields.Integer(dump_only=True)
    title = fields.String()
    description = fields.String()
    trailer = fields.String()
    year = fields.Integer()
    rating = fields.Float()
    genre_id = fields.Integer()
    director_id = fields.Integer()


@movies_ns.route('/')
class MoviesView(Resource):
    def get(self):
        filters = request.args.to_dict()
        supported_filters = ('genre_id', 'director_id')

        if filters:
            filters = filter_dict(filters, supported_filters)
            movies = Movie.query.filter_by(**filters).all()
        else:
            movies = Movie.query.all()

        return MovieSchema(many=True).dump(movies), 200

    def post(self):
        try:
            movie_data = MovieSchema().load(request.json)
        except ValidationError:
            return 'Invalid JSON', 400

        new_movie = Movie(**movie_data)
        with db.session.begin():
            db.session.add(new_movie)
        return '', 201


@movies_ns.route('/<int:mid>')
class MovieView(Resource):
    def get(self, mid):
        movie = Movie.query.get(mid)
        if not movie:
            return '', 404
        return MovieSchema().dump(movie), 200

    def put(self, mid):
        movie = Movie.query.get(mid)

        if not movie:
            return '', 404

        try:
            movie_data = MovieSchema().load(request.json)
        except ValidationError:
            return 'Invalid JSON', 400

        movie.title = movie_data['title']
        movie.description = movie_data['description']
        movie.trailer = movie_data['trailer']
        movie.year = movie_data['year']
        movie.rating = movie_data['rating']
        movie.genre_id = movie_data['genre_id']
        movie.director_id = movie_data['director_id']

        db.session.add(movie)
        db.session.commit()
        return '', 204

    def delete(self, mid):
        movie: Movie = Movie.query.get(mid)

        if not movie:
            return '', 404

        db.session.delete(movie)
        db.session.commit()
        return '', 204


if __name__ == '__main__':
    app.run(debug=True)
