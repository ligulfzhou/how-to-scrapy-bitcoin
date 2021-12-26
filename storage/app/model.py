from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class PrivateKey(db.Model):
    __tablename__ = 'private_key'

    id = db.Column(db.Integer, primary_key=True)
    num = db.Column(db.String)
    private_key = db.Column(db.String)
    address = db.Column(db.String)


class Mnemonic(db.Model):
    __tablename__ = 'mnemonic_code'

    id = db.Column(db.Integer, primary_key=True)
    mnemonic = db.Column(db.String)
    mnemonic_code = db.Column(db.ARRAY(db.String))
    private_keys = db.Column(db.ARRAY(db.String))
