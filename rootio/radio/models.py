# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy import Column, Table, types
from .fields import FileField
from .constants import PROGRAM_TYPES, PRIVACY_TYPE

from ..utils import STRING_LEN, GENDER_TYPE, get_current_time, id_generator, object_list_to_named_dict
from ..extensions import db

from ..telephony import PhoneNumber

class Location(db.Model):
    "A geographic location"
    __tablename__ = u'radio_location'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(STRING_LEN))
    municipality = db.Column(db.String(STRING_LEN))
    district = db.Column(db.String(STRING_LEN))
    modifieddate = db.Column(db.Date)
    country = db.Column(db.String(STRING_LEN))
    addressline1 = db.Column(db.String(STRING_LEN))
    addressline2 = db.Column(db.String(STRING_LEN))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    def __unicode__(self):
        return self.name


class Language(db.Model):
    __tablename__ = u'radio_language'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(STRING_LEN)) # human readable language name
    iso639_1 = db.Column(db.String(2)) # 2 digit code (eg, 'en')
    iso639_2 = db.Column(db.String(3))# 3 digit code (eg, 'eng')
    locale_code = db.Column(db.String(10)) # IETF locale (eg, 'en-US')

    #relationships
    programs = db.relationship(u'Program', backref=db.backref('language'))

    def __unicode__(self):
        return self.name


class Network(db.Model):
    "A network of radio stations"
    __tablename__ = "radio_network"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(STRING_LEN), nullable=False)
    about = db.Column(db.Text())

    admins = db.relationship(u'User', secondary=u'radio_networkadmins', backref=db.backref('networks'))
    stations = db.relationship(u'Station', backref=db.backref('network'))
    #networks can have multiple admins

    def __unicode__(self):
        return self.name


t_networkadmins = db.Table(
    u'radio_networkadmins',
    db.Column(u'user_id', db.ForeignKey('user_user.id')),
    db.Column(u'network_id', db.ForeignKey('radio_network.id'))
)


class Station(db.Model):
    "A single radio station"
    __tablename__ = 'radio_station'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(STRING_LEN), nullable=False)
    about = db.Column(db.Text())
    frequency = db.Column(db.Float)
    api_key = db.Column(db.String(STRING_LEN),nullable=False,default=id_generator(),unique=True)
    #todo, make sure this default function fires each time a new object is created

    #foreign keys
    owner_id = db.Column(db.ForeignKey('user_user.id'))
    network_id = db.Column(db.ForeignKey('radio_network.id'))
    location_id = db.Column(db.ForeignKey('radio_location.id'))
    cloud_phone_id = db.Column(db.ForeignKey('telephony_phonenumber.id'))
    transmitter_phone_id = db.Column(db.ForeignKey('telephony_phonenumber.id'))

    #relationships
    owner = db.relationship(u'User')
    location = db.relationship(u'Location')

    cloud_phone = db.relationship(u'PhoneNumber', backref=db.backref('station_cloud',uselist=False), foreign_keys=[cloud_phone_id])
    transmitter_phone = db.relationship(u'PhoneNumber', backref=db.backref('station_transmitter',uselist=False), foreign_keys=[transmitter_phone_id])

    blocks = db.relationship(u'ScheduledBlock', backref=db.backref('station'))
    scheduled_programs = db.relationship(u'ScheduledProgram', backref=db.backref('station',uselist=False))
    languages = db.relationship(u'Language', secondary=u'radio_stationlanguage', backref=db.backref('stations'))
    analytics = db.relationship(u'StationAnalytic', backref=db.backref('station',uselist=False))

    def init(self):
        #load dummy program
        #init state machine
        return "init() stub"

    def current_program(self):
        now = datetime.now()
        programs = ScheduledProgram.contains(now).filter_by(station_id=self.id)
        #TODO, how to resolve overlaps?
        return programs.first()

    def next_program(self):
        now = datetime.now()
        upcoming_programs = ScheduledProgram.after(now).filter_by(station_id=self.id)
        return upcoming_programs.first()

    def current_block(self):
        now = datetime.now()
        blocks = ScheduledBlock.contains(now).filter_by(station_id=self.id)
        #TODO, how to resolve overlaps?
        return blocks.first()

    def status(self):
        #TODO

        #random appearance for demo
        from random import random
        r = random()
        if r > 0.8:
            return "unknown"
        elif r > 0.6:
            return "off"
        else:
            return "on"

    def recent_analytics(self):
        #TODO, load from db

        #fake a week's worth for the demo
        #guess reasonable ranges
        from random import random, randint
        analytics_list = []
        for i in xrange(7):
            a = StationAnalytic()
            a.battery_level = randint(50,100)
            a.cpu_load = random()
            a.memory_utilization = randint(60,80)
            a.storage_usage = randint(20,50)
            a.gsm_connectivity = randint(0,100)
            a.headphone_plug = randint(0,1)
            analytics_list.append(a)

        #should really do something like
        # analytics_list = StationAnalytics.query.filter(station_id=self.id,
        #     created_time>datetime.now()-datetime.timedelta(days=14))

        #convert to named dict for sparkline display
        analytics_dict = object_list_to_named_dict(analytics_list)
        return analytics_dict

    def recent_telephony(self):
        #TODO, load from GOIP

        #fake a week's worth for the demo

        #do we need a db object for this?
        class TelephonyAnalytic():
            pass

        from random import random, randint
        def random_boolean(threshold):
            "returns 1 threshold percent of the time, otherwise 0"
            r = random()
            if r > threshold:
                return 0
            else:
                return 1

        telephony_list = []
        for i in xrange(7):
            a = TelephonyAnalytic()
            a.sim = random_boolean(0.9)
            a.gsm = random_boolean(0.7)
            a.voip = random_boolean(0.5)
            a.credits = randint(1000,5000)
            a.messages = randint(0,100)
            a.calls = randint(0,100)
            telephony_list.append(a)

        #convert to named dict for sparkline display
        telephony_dict = object_list_to_named_dict(telephony_list)
        return telephony_dict

    def __unicode__(self):
        return self.name


t_stationlanguage = db.Table(
    u'radio_stationlanguage',
    db.Column(u'language_id', db.ForeignKey('radio_language.id')),
    db.Column(u'station_id', db.ForeignKey('radio_station.id'))
)


class ProgramType(db.Model):
    "A flexible definition of program dynamics"
    __tablename__ = u'radio_programtype'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(STRING_LEN),nullable=False)
    description = db.Column(db.Text,nullable=False)
    definition = db.Column(db.PickleType,nullable=False)
    #TODO: more complex program definition?

    def __unicode__(self):
        return self.name


class Program(db.Model):
    "A single or recurring radio program"
    __tablename__ = 'radio_program'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(STRING_LEN),
        nullable=False)
    duration = db.Column(db.Time)
    update_recurrence = db.Column(db.Text()) #when new content updates are available

    language_id = db.Column(db.ForeignKey('radio_language.id'))
    program_type_id = db.Column(db.ForeignKey('radio_programtype.id'))

    program_type = db.relationship(u'ProgramType')
    episodes = db.relationship('Episode', backref=db.backref('program'), lazy='dynamic')
    scheduled_programs = db.relationship(u'ScheduledProgram', backref=db.backref('program',uselist=False))

    def __unicode__(self):
        return self.name


class Episode(db.Model):
    "A particular episode of a program, or other broadcast audio"
    __tablename__ = 'radio_episode'

    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.ForeignKey('radio_program.id'), nullable=False)
    recording_id = db.Column(db.ForeignKey('radio_recording.id'))
    created_time = db.Column(db.DateTime, default=get_current_time)

    recording = db.relationship(u'Recording')


class ScheduledBlock(db.Model):
    """A block of similar programs, with a recurrence rule and duration.
    Similar to advertising 'dayparts'
    """
    __tablename__ = "radio_scheduledblock"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(STRING_LEN), nullable=False)
    recurrence = db.Column(db.Text()) #iCal rrule format, RFC2445 4.8.5.4
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    station_id = db.Column(db.ForeignKey('radio_station.id'))

    @classmethod
    def after(cls,time):
        return cls.query.filter(ScheduledBlock.start_time >= time)

    @classmethod
    def before(cls,time):
        return cls.query.filter(ScheduledBlock.end_time <= time)

    @classmethod
    def between(cls,start,end):
        return cls.query.filter(ScheduledBlock.start_time > start &
                                ScheduledBlock.end_time < end)

    @classmethod
    def contains(cls,time):
        return cls.query.filter(ScheduledBlock.start_time <= time &
                                ScheduledBlock.end_time >= time)

    def __unicode__(self):
        return self.name


class ScheduledProgram(db.Model):
    """Content scheduled to air on a station at a time.
    Read these in order to determine a station's next to air."""
    __tablename__ = "radio_scheduledprogram"
    id = db.Column(db.Integer, primary_key=True)
    station_id = db.Column(db.ForeignKey('radio_station.id'))
    program_id = db.Column(db.ForeignKey('radio_program.id'))
    start = db.Column(db.DateTime)
    end = db.Column(db.DateTime)

    @classmethod
    def after(cls,date):
        return cls.query.filter(ScheduledProgram.start >= date)

    @classmethod
    def before(cls,date):
        return cls.query.filter(ScheduledProgram.end <= date)

    @classmethod
    def between(cls,start,end):
        return cls.query.filter(ScheduledProgram.start >= start) \
                        .filter(ScheduledProgram.end <= end)

    @classmethod
    def contains(cls,date):
        return cls.query.filter(ScheduledProgram.start <= date) \
                        .filter(ScheduledProgram.end >= date)


class PaddingContent(db.Model):
    """An advertisement or PSA to run on a network in a block.
    Actual air schedule to be determined by the scheduler."""
    __tablename__ = "radio_paddingcontent"
    id = db.Column(db.Integer, primary_key=True)
    recording_id = db.Column(db.ForeignKey('radio_recording.id'))
    block_id = db.Column(db.ForeignKey('radio_scheduledblock.id'))
    #sponsoring org?

    block = db.relationship(u'ScheduledBlock')
    networks = db.relationship(u'Network', secondary=u'radio_networkpadding', backref=db.backref('paddingcontents'))


t_networkpadding = db.Table(
    u'radio_networkpadding',
    db.Column(u'network_id', db.ForeignKey('radio_network.id')),
    db.Column(u'paddingcontent_id', db.ForeignKey('radio_paddingcontent.id'))
)

class Recording(db.Model):
    "A recorded sound file"
    __tablename__ = 'radio_recording'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(160))
    local_file = db.Column(FileField([]))
    created_time = db.Column(db.DateTime, default=get_current_time)


class Person(db.Model):
    "A person associated with a station or program, but not necessarily a user of Rootio system"
    __tablename__ = 'radio_person'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(8))
    firstname = db.Column(db.String(STRING_LEN))
    middlename = db.Column(db.String(STRING_LEN))
    lastname = db.Column(db.String(STRING_LEN))
    email = db.Column(db.String(STRING_LEN))
    additionalcontact = db.Column(db.String(STRING_LEN))

    phone_id = db.Column(db.ForeignKey('telephony_phonenumber.id'))

    phone = db.relationship(u'PhoneNumber', backref=db.backref('person',uselist=False))
    role = db.relationship(u'Role', backref=db.backref('person'))
    languages = db.relationship(u'Language', secondary=u'radio_personlanguage', backref=db.backref('person',uselist=False))

    gender_code = db.Column(db.Integer)
    @property
    def gender(self):
        return GENDER_TYPE.get(self.gender_code)

    privacy_code = db.Column(db.Integer)
    @property
    def privacy(self):
        return PRIVACY_TYPE.get(self.privacy_code)

    def __unicode__(self):
        return " ".join([self.title,self.firstname,self.middlename,self.lastname])
    
    #TODO: fk to user_id?


t_personlanguage = db.Table(
    u'radio_personlanguage',
    db.Column(u'language_id', db.ForeignKey('radio_language.id')),
    db.Column(u'person_id', db.ForeignKey('radio_person.id'))
)


class Role(db.Model):
    "A role for a person at a particular station"
    __tablename__ = u'radio_role'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    person_id = db.Column(db.ForeignKey('radio_person.id'))
    #TODO: add program_id
    station_id = db.Column(db.ForeignKey('radio_station.id'))


class StationAnalytic(db.Model):
    "A store for analytics from the client"
    __tablename__ = 'radio_stationanalytic'

    id = db.Column(db.Integer, primary_key=True)
    created_time = db.Column(db.DateTime, default=get_current_time)
    station_id = db.Column(db.ForeignKey('radio_station.id'))

    #TODO, decide on range with Jude
    battery_level = db.Column(db.Float) # percentage 0,100 
    cpu_load = db.Column(db.Float) # load level 0,inf (should be under 1)
    memory_utilization = db.Column(db.Float) # percentage 0,100
    storage_usage = db.Column(db.Float) # percentage 0,100
    gsm_connectivity = db.Column(db.Float) # signal strength in db?
    headphone_plug = db.Column(db.Boolean) # boolean 0,1

