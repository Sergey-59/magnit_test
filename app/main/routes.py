import datetime

from flask import jsonify, redirect, url_for, current_app
from app import db, docs
from app.email import send_email
from app.main import bp
from app.models import User, Auction, Bet
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.schemas import UserSchema, UserAuthSchema, AuctionSchema, BetSchema
from flask_apispec import use_kwargs, marshal_with
from app.base_view import BaseView
from app.tasks import new_auction
from marshmallow import fields


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    return redirect(url_for('flask-apispec.swagger-ui'))


class RegistrationView(BaseView):
    @use_kwargs(UserSchema)
    @marshal_with(UserAuthSchema)
    def post(self, **kwargs):
        try:
            user = User(**kwargs)
            db.session.add(user)
            db.session.commit()
            token = user.get_token()
            return {'access_token': token}
        except Exception as e:
            return {'message': "{}".format(e)}, 400


class LoginView(BaseView):
    @use_kwargs(UserSchema(only=('email', 'password')))
    @marshal_with(UserAuthSchema)
    def post(self, **kwargs):
        try:
            user = User.authenticate(**kwargs)
            token = user.get_token()
            return {'access_token': token}
        except Exception as e:
            return {'message': "{}".format(e)}, 400


class AuctionView(BaseView):
    @jwt_required()
    @use_kwargs(AuctionSchema)
    @marshal_with(AuctionSchema)
    def post(self, **kwargs):
        try:
            kwargs['owner_id'] = get_jwt_identity()
            auction = Auction(**kwargs)
            db.session.add(auction)
            db.session.commit()
            new_auction.delay(auction.id, auction.owner_id)
            return auction
        except Exception as e:
            return {'message': "{}".format(e)}, 400


class AuctionDetailView(BaseView):
    @jwt_required()
    @marshal_with(AuctionSchema)
    def get(self, id):
        try:
            auction = Auction.query.filter(Auction.id == id).one()
            return auction
        except Exception as e:
            return {'message': "{}".format(e)}, 400


class AuctionListView(BaseView):
    @jwt_required()
    @marshal_with(AuctionSchema(many=True))
    def get(self):
        try:
            auctions = Auction.query.all()
            return auctions
        except Exception as e:
            return {'message': "{}".format(e)}, 400

    @jwt_required()
    @use_kwargs({'is_active': fields.Boolean()})
    @marshal_with(AuctionSchema(many=True))
    def post(self, is_active):
        try:
            auctions = Auction.query.filter(Auction.is_active == is_active).all()
            return auctions
        except Exception as e:
            return {'message': "{}".format(e)}, 400


class BetView(BaseView):
    @jwt_required()
    @use_kwargs(BetSchema)
    @marshal_with(BetSchema)
    def post(self, **kwargs):
        try:
            kwargs['user_id'] = get_jwt_identity()
            bet = Bet(**kwargs)
            db.session.add(bet)
            db.session.commit()
            return bet
        except Exception as e:
            return {'message': "{}".format(e)}, 400


RegistrationView.register(bp, docs, '/registration', 'registrationview')
LoginView.register(bp, docs, '/login', 'loginview')
AuctionListView.register(bp, docs, '/auctions', 'auctionlistview')
AuctionView.register(bp, docs, '/auctions/auction', 'auctionview')
AuctionDetailView.register(bp, docs, '/auctions/auction/<int:id>', 'auctiondetailview')
BetView.register(bp, docs, '/bet', 'betview')
