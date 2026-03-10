from flask import Flask
from flask_restx import Api, Resource, fields
from ..storage.sqlalchemy import SQLAlchemyStore

def create_admin_app(store: SQLAlchemyStore):
    app = Flask(__name__)
    api = Api(app, doc='/docs/')
    ns = api.namespace('zrb', description='ZRB Admin API')

    zone_model = api.model('Zone', {
        'id': fields.String, 'name': fields.String, 'parent_id': fields.String, 'description': fields.String,
    })

    @ns.route('/zones/<string:zone_id>')
    class ZoneDetail(Resource):
        def get(self, zone_id):
            z = store.get_zone(zone_id)
            if not z:
                return {'message': 'not found'}, 404
            return z.dict()

    return app
