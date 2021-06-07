from marshmallow import Schema, validate, fields


class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=[validate.Length(max=250)])
    email = fields.Email(required=True, validate=[validate.Length(max=250)])
    password = fields.String(required=True, validate=[validate.Length(max=100)], load_only=True)
    auctions = fields.Nested('AuctionSchema', many=True, dump_only=True)
    bets = fields.Nested('BetSchema', many=True, dump_only=True)


class UserAuthSchema(Schema):
    access_token = fields.String(dump_only=True)
    message = fields.String(dump_only=True)


class AuctionSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(allow_none=True, validate=[validate.Length(max=100)])
    description = fields.String(required=True, validate=[validate.Length(max=250)])
    first_cost = fields.Float(required=True)
    step_cost = fields.Float(required=True)
    start_auction = fields.DateTime(allow_none=True)
    end_auction = fields.DateTime(required=True)
    is_active = fields.Boolean(allow_none=True)
    owner_id = fields.Integer(dump_only=True)
    bets = fields.Nested('BetSchema', only=('cost', 'user'), many=True, dump_only=True)
    message = fields.String(dump_only=True)


class BetSchema(Schema):
    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(dump_only=True)
    auction_id = fields.Integer(required=True)
    cost = fields.Float(required=True)
    user = fields.Nested(UserSchema(only=('name',)), dump_only=True)
    message = fields.String(dump_only=True)
