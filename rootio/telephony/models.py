# -*- coding: utf-8 -*-

from sqlalchemy import Column, Table
from ..extensions import db

from ..utils import STRING_LEN

class PhoneNumber(db.Model):
    "A phone number, associated with a station, person or call"
    __tablename__ = u'telephony_phonenumber'

    id = db.Column(db.Integer, primary_key=True)
    numbertype = db.Column(db.String(30)) #constrain to mobile / landline?
    carrier = db.Column(db.String(STRING_LEN))
    countrycode = db.Column(db.String(3)) #does not include + symbol
    areacode = db.Column(db.String(8)) #consistent across countries?
    number = db.Column(db.String(20))


class Call(db.Model):
    __tablename__ = u'telephony_call'

    id = db.Column(db.Integer, primary_key=True)
    call_uuid = db.Column(db.String(100))
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    from_phonenumber_id = db.Column(db.ForeignKey('telephony_phonenumber.id'))
    to_phonenumber_id = db.Column(db.ForeignKey('telephony_phonenumber.id'))

    from_phonenumber = db.relationship(u'PhoneNumber', primaryjoin='Call.from_phonenumber_id == PhoneNumber.id')
    to_phonenumber = db.relationship(u'PhoneNumber', primaryjoin='Call.to_phonenumber_id == PhoneNumber.id')


class Message(db.Model):
    __tablename__ = u'telephony_message'

    id = db.Column(db.Integer, primary_key=True)
    message_uuid = db.Column(db.String(100))
    sendtime = db.Column(db.DateTime)
    text = db.Column(db.String(200))
    from_phonenumber_id = db.Column(db.ForeignKey('telephony_phonenumber.id'))
    to_phonenumber_id = db.Column(db.ForeignKey('telephony_phonenumber.id'))

    phonenumber = db.relationship(u'PhoneNumber', primaryjoin='Message.from_phonenumber_id == PhoneNumber.id')
    phonenumber1 = db.relationship(u'PhoneNumber', primaryjoin='Message.to_phonenumber_id == PhoneNumber.id')
