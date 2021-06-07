import os
from passlib.hash import bcrypt
from app import db
from flask_jwt_extended import create_access_token
from datetime import timedelta, datetime, timezone


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    auctions = db.relationship('Auction')
    bets = db.relationship('Bet')

    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.email = kwargs.get('email')
        self.password = bcrypt.hash(kwargs.get('password'))

    def get_token(self, expire_time=int(os.environ.get('JWT_EXPIRE_TIME')) or 1):
        expire_delta = timedelta(expire_time)
        token = create_access_token(identity=self.id, expires_delta=expire_delta)

        return token

    @classmethod
    def authenticate(cls, email, password):
        user = cls.query.filter(cls.email == email).one()
        if not bcrypt.verify(password, user.password):
            raise Exception('No user with this password')

        return user


class Auction(db.Model):
    __tablename__ = 'auctions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(250), nullable=False)
    first_cost = db.Column(db.Float, nullable=False)
    step_cost = db.Column(db.Float, nullable=False)
    start_auction = db.Column(db.DateTime, nullable=False)
    end_auction = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    bets = db.relationship('Bet')

    def __init__(self, **kwargs):
        self.start_auction = kwargs.get('start_auction', datetime.now(timezone.utc))
        self.end_auction = kwargs.get('end_auction')

        if self.start_auction >= self.end_auction:
            raise Exception('Error - start_auction >= end_auction')

        self.name = kwargs.get('name', kwargs.get('description').split()[0])
        self.description = kwargs.get('description')
        self.first_cost = abs(kwargs.get('first_cost'))
        self.step_cost = abs(kwargs.get('step_cost'))
        self.is_active = kwargs.get('is_active', True)
        self.owner_id = kwargs.get('owner_id')


class Bet(db.Model):
    __tablename__ = 'bets'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', back_populates="bets")
    auction_id = db.Column(db.Integer, db.ForeignKey('auctions.id'))
    cost = db.Column(db.Float, nullable=False)

    def __init__(self, **kwargs):
        auction = Auction.query.filter(Auction.id == kwargs.get('auction_id')).one()
        if not auction.is_active or datetime.utcnow() > auction.end_auction:
            raise Exception('This auction is closed.')

        if auction.owner_id == kwargs.get('user_id'):
            raise Exception("You can't get a bet on this auction!")

        self.user_id = kwargs.get('user_id')
        self.auction_id = kwargs.get('auction_id')

        current_cost = sorted(auction.bets, key=self.sort_by_cost, reverse=True)[0].cost if auction.bets else auction.first_cost

        if current_cost >= kwargs.get('cost'):
            raise Exception('The current bet is higher or equal to your bet.')

        if current_cost == auction.first_cost:
            if kwargs.get('cost') % auction.step_cost != 0:
                raise Exception('Your "step_cost" is not correct.')
        else:
            if (kwargs.get('cost') - auction.first_cost) % auction.step_cost != 0:
                raise Exception('Your "step_cost" is not correct.')

        self.cost = kwargs.get('cost')

    @staticmethod
    def sort_by_cost(instance):
        return instance.cost
