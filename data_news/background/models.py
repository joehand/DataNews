from data_news import db

class Twitter(db.Model):
    """ Keep track of a few max id's for fetching via Twitter ID.
        Should only be one row in this table
    """
    id = db.Column(db.Integer, primary_key = True)
    mention_id = db.Column(db.BigInteger)
    fav_id = db.Column(db.BigInteger)

