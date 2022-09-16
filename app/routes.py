from flask import current_app as app, request
from flask_restx import Api, Resource
from marshmallow.exceptions import ValidationError

from . import models, db
from .utils import filter_dict

api = Api(app)
movies_ns = api.namespace('movies')


@movies_ns.route('/')
class MoviesView(Resource):
    def get(self):
        filters = request.args.to_dict()
        supported_filters = ('genre_id', 'director_id')

        if filters:
            filters = filter_dict(filters, supported_filters)
            movies = models.Movie.query.filter_by(**filters).all()
        else:
            movies = models.Movie.query.all()

        return models.MovieSchema(many=True).dump(movies), 200

    def post(self):
        try:
            movie_data = models.MovieSchema().load(request.json)
        except ValidationError:
            return 'Invalid JSON', 400

        new_movie = models.Movie(**movie_data)
        with db.session.begin():
            db.session.add(new_movie)
        return '', 201


@movies_ns.route('/<int:mid>')
class MovieView(Resource):
    def get(self, mid):
        movie = models.Movie.query.get(mid)
        if not movie:
            return '', 404
        return models.MovieSchema().dump(movie), 200

    def put(self, mid):
        movie = models.Movie.query.get(mid)

        if not movie:
            return '', 404

        try:
            movie_data = models.MovieSchema().load(request.json)
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
        movie = models.Movie.query.get(mid)

        if not movie:
            return '', 404

        db.session.delete(movie)
        db.session.commit()
        return '', 204
