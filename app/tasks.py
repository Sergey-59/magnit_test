from operator import and_
from datetime import datetime
from . import celery
from . import db, create_app
from .email import send_email
from .models import User, Bet, Auction
from sqlalchemy.orm import load_only
from config import Config


@celery.task()
def new_auction(auction_id, owner_id):
    try:
        app = create_app()
        with app.app_context():
            users = User.query.filter(User.id != owner_id).options(load_only('email')).all()

            send_email('New auction',
                       sender=Config.ADMINS[0],
                       recipients=[user.email for user in users],
                       text_body='We have a new action Id - {}!'.format(auction_id))

    except Exception as e:
        # TODO можно отправлять в очередь ошибок, бот, sentry и т.д.
        print('Error "new_auction" task for auction id - {}, error - {}.'.format(auction_id, e))
        return False
    return True


@celery.task()
def new_bet(auction_id, user_id, bet):
    try:
        app = create_app()
        with app.app_context():
            bets = Bet.query.filter(and_(Bet.auction_id == auction_id, Bet.user_id != user_id)).all()
            users_email = {bet.user.email for bet in bets}
            send_email('New bet',
                       sender=Config.ADMINS[0],
                       recipients=list(users_email),
                       text_body='We have a new bet - {} on action Id - {}!'.format(bet, auction_id))

    except Exception as e:
        # TODO можно отправлять в очередь ошибок, бот, sentry и т.д.
        print('Error "new_bet" task for auction id - {}, bet - {}, error - {}.'.format(auction_id, bet, e))
        return False
    return True


# runs every 1 min.
@celery.task(name='tasks.check_auction')
def check_auction():
    now_date = datetime.utcnow().strftime('%Y-%m-%d %H:%M')
    now_date = datetime.strptime(now_date, '%Y-%m-%d %H:%M')
    try:
        app = create_app()
        with app.app_context():
            auctions = Auction.query.filter(and_(Auction.is_active == True, Auction.end_auction <= now_date)).all()

            if auctions:
                for auction in auctions:
                    auction.is_active = False
                    db.session.commit()
                    if auction.bets:
                        max_bet = sorted(auction.bets, key=Bet.sort_by_cost, reverse=True)[0]
                        users_email = {bet.user.email for bet in auction.bets}

                        send_email('Winner auction Id - {}'.format(auction.id),
                                   sender=Config.ADMINS[0],
                                   recipients=list(users_email),
                                   text_body='{} is winner auction Id - {}, he have max bet - {}!'.format(max_bet.user.name,
                                                                                                          auction.id,
                                                                                                          max_bet.cost))
    except Exception as e:
        # TODO можно отправлять в очередь ошибок, бот, sentry и т.д.
        print('Error "check_auction" task for date - {}, error - {}.'.format(now_date, e))
        return False
    return True
