""" SQLAlchemy Definitions + Session Creation (using PostgreSQL) """

import threading
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, BIGINT, String, SMALLINT, TIMESTAMP, MetaData, desc, and_, or_
from sqlalchemy.orm import sessionmaker, scoped_session

import settings
from utils import event

ADDRESS = None
PORT = None
DB = None
USERNAME = None
PASSWD = None
USEMYSQL = False

engine = None
Base = declarative_base()
Session = scoped_session(sessionmaker())

LOCK = threading.Lock() # Only one thread can use a DB session at a time... SAD!

def onSettingsChanged(name, config): # Deals with reconnecting the engine for new db settings.
    global ADDRESS, PORT, DB, USERNAME, PASSWD, USEMYSQL, Session, engine
    ADDRESS = config.get("database", "address")
    PORT = config.get("database", "port")
    DB = config.get("database", "db")
    USERNAME = config.get("database", "user")
    PASSWD = config.get("database", "passwd")    
    with LOCK: # Update connection itself... WAIT for other queries to finish via the lock.
        USEMYSQL = (config.get("database", "type") == "mysql") # Must not be changed while other queries run, since postgres needs to set the schema!
        if engine:
            engine.dispose()
            Session.remove()
            Session = scoped_session(sessionmaker())
        engine = create_engine("{}{}:{}@{}:{}/{}".format("mysql+pymysql://" if USEMYSQL else "postgresql://", USERNAME, PASSWD, ADDRESS, PORT, DB))
        Session.configure(bind=engine)

def loadDatabase():
    settings.settings.SETTINGSEVENT.addListener(onSettingsChanged, onSettingsChanged)
    onSettingsChanged(None, settings.settings.SETTINGS)    

def add(el, schema):
    """Generic Add"""
    s = None
    with LOCK:
        try:
            s = Session()
            if not USEMYSQL:
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
            if not USEMYSQL:
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
            if not USEMYSQL:
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

    def add(msg, s, t, time):
        """
        Add a new event to the DB.
        """
        add(Event(message=msg, severity=s, type=t, time=time), "sensor")

    def delete(id):
        """
        Remove an event from the DB.
        """
        delete(find(id, "sensor"), "sensor")

    def findByType(t, reverse=False):
        output = list()    
        with LOCK:
            try:
                s = Session()
                if not USEMYSQL:
                    s.execute('set search_path=sensor')
                for d in s.query(Event).filter_by(type=t).order_by(desc(Event.time)).all():
                    output.append(d)
            except Exception as e:
                print(e)
            finally:
                if reverse:
                    output.reverse()
                return output

    def findTypeWithin(t, start, end, reverse=False):
        output = list()    
        with LOCK:
            try:
                s = Session()
                if not USEMYSQL:
                    s.execute('set search_path=sensor')
                for d in s.query(Event).filter(Event.time >= start, Event.time <= end, Event.type == t).order_by(desc(Event.time)).all():
                    output.append(d)
            except Exception as e:
                print(e)
            finally:
                if reverse:
                    output.reverse()
                return output


def deleteDataFromDatabase(schema):
    """Delete all data!"""
    s = None
    with LOCK:
        try:
            s = Session()
            if not USEMYSQL:
                s.execute('set search_path={}'.format(schema))                    
            
            # Delete actual table data here:
            s.query(Event).delete() # Delete all events.

            # Commit changes!
            s.commit()
        except Exception as e:
            print(e)
            if s:
                s.rollback()    
        finally:
            if s:
                s.close()