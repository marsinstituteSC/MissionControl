""" SQLAlchemy Definitions + Session Creation (using PostgreSQL) """

import threading
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, BIGINT, String, SMALLINT, TIMESTAMP, MetaData
from sqlalchemy.orm import sessionmaker, scoped_session

from utils import event
from settings.settings import SETTINGSEVENT, SETTINGS

ADDRESS = None
PORT = None
DB = None
USERNAME = None
PASSWD = None

engine = create_engine("postgresql://postgres:booty@localhost/rover")
Base = declarative_base()
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

LOCK = threading.Lock() # Only one thread can use a DB session at a time... SAD!

def onSettingsChanged(name, config):
    pass
    #global ADDRESS, PORT, DB, USERNAME, PASSWD
    # ADDRESS = config.get("database", "address")
    # PORT = config.get("database", "port")
    # DB = config.get("database", "db")
    # USERNAME = config.get("database", "user")
    # PASSWD = config.get("database", "passwd")


def loadDatabase():
    SETTINGSEVENT.addListener(onSettingsChanged, onSettingsChanged)
    onSettingsChanged(None, SETTINGS)    

def add(el, schema):
    """Generic Add"""
    s = None
    with LOCK:
        try:
            s = Session()
            s.execute('set search_path={}'.format(schema))
            s.add(el)
            s.commit()
        except Exception as e:
            print(e)
            if s:
                s.rollback()  
        finally:
            if s:
                s.close()

def delete(el, schema):
    """Generic Delete"""
    s = None
    with LOCK:
        try:
            s = Session()
            s.execute('set search_path={}'.format(schema))
            s.delete(el)
            s.commit()
        except Exception as e:
            print(e)
            if s:
                s.rollback()    
        finally:
            if s:
                s.close()

def find(id, schema):
    """Generic Find"""
    with LOCK:
        try:
            s = Session()
            s.execute('set search_path={}'.format(schema))
            return s.query(Event).filter_by(id=id).first()
        except Exception as e:
            print(e)
            return None

class Event(Base):
    __tablename__ = "event"
    id = Column(BIGINT, primary_key=True)
    message = Column(String)
    severity = Column(SMALLINT)
    type = Column(SMALLINT)
    time = Column(TIMESTAMP)

    def __repr__(self):
        return "Sensor.Event(msg={}, sev={}, typ={}, time={})".format(self.message, self.severity, self.type, self.time)

    def add(msg, severity, type, time):
        """
        Add a new event to the DB.
        """
        add(Event(message=msg, severity=severity, type=type, time=time), "sensor")

    def delete(id):
        """
        Remove an event from the DB.
        """
        delete(find(id, "sensor"), "sensor")

    def findByType(type):
        output = list()    
        with LOCK:
            try:
                s = Session()
                s.execute('set search_path=sensor')
                for d in s.query(Event).filter_by(type=type).all():
                    output.append(d)
            except Exception as e:
                print(e)
            finally:
                return output
