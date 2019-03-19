""" SQLAlchemy Definitions + Session Creation (using PostgreSQL) """

import threading, time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, BIGINT, String, SMALLINT, TIMESTAMP, MetaData, desc, and_, or_
from sqlalchemy.orm import sessionmaker, scoped_session
from PyQt5.QtCore import QObject, pyqtSignal
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

STATUS_SIGNAL_RATE_LIMIT = 0.5 # Only emit every X sec.
class DBStatusSignal(QObject):
    status = pyqtSignal(tuple)
    def __init__(self):
        super().__init__()
        self.lastSignal = time.time()
    
    def dispatch(self, state, msg=""):
        """
        Notify UI that the DB has tried to execute a query.
        """        
        if (time.time() - self.lastSignal) <= STATUS_SIGNAL_RATE_LIMIT:
            return

        self.status.emit((state, msg))
        self.lastSignal = time.time()

SIGNAL = DBStatusSignal()

def onSettingsChanged(name, config): # Deals with reconnecting the engine for new db settings.
    global ADDRESS, PORT, DB, USERNAME, PASSWD, USEMYSQL, Session, engine
    ADDRESS = config.get("database", "address")
    PORT = config.get("database", "port")
    DB = config.get("database", "db")
    USERNAME = config.get("database", "user")
    PASSWD = config.get("database", "passwd")    
    with LOCK: # Update connection itself... WAIT for other queries to finish via the lock.
        USEMYSQL = (config.get("database", "type") == "mysql")
        if engine:
            engine.dispose()
            Session.remove()
            Session = scoped_session(sessionmaker())
        engine = create_engine("{}{}:{}@{}:{}/{}".format("mysql+pymysql://" if USEMYSQL else "postgresql://", USERNAME, PASSWD, ADDRESS, PORT, DB))
        Session.configure(bind=engine)

def loadDatabase():
    settings.settings.SETTINGSEVENT.addListener(onSettingsChanged, onSettingsChanged)
    onSettingsChanged(None, settings.settings.SETTINGS)          

def add(el):
    """Generic Add"""
    s = None
    with LOCK:
        try:
            s = Session()
            s.add(el)
            s.commit()
            SIGNAL.dispatch(True)
        except Exception as e:
            print(e)
            SIGNAL.dispatch(False, e)
            if s:
                s.rollback()  
        finally:
            if s:
                s.close()

def delete(el):
    """Generic Delete"""
    s = None
    with LOCK:
        try:
            s = Session()
            s.delete(el)
            s.commit()
            SIGNAL.dispatch(True)
        except Exception as e:
            print(e)
            SIGNAL.dispatch(False, e)
            if s:
                s.rollback()    
        finally:
            if s:
                s.close()

def find(id):
    """Generic Find"""
    with LOCK:
        try:
            s = Session()
            return s.query(Event).filter_by(id=id).first()
        except Exception as e:
            print(e)
            return None

class Event(Base):
    __tablename__ = "event"
    id = Column(BIGINT, primary_key=True)
    message = Column(String(128))
    severity = Column(SMALLINT)
    type = Column(SMALLINT)
    time = Column(TIMESTAMP)

    def __repr__(self):
        return "Event(msg={}, sev={}, typ={}, time={})".format(self.message, self.severity, self.type, self.time)

    def add(msg, s, t, time):
        """
        Add a new event to the DB.
        """
        add(Event(message=msg, severity=s, type=t, time=time))

    def delete(id):
        """
        Remove an event from the DB.
        """
        delete(find(id))

    def findByType(t, reverse=False):
        output = list()    
        with LOCK:
            try:
                s = Session()
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
                for d in s.query(Event).filter(Event.time >= start, Event.time <= end, Event.type == t).order_by(desc(Event.time)).all():
                    output.append(d)
            except Exception as e:
                print(e)
            finally:
                if reverse:
                    output.reverse()
                return output


def deleteDataFromDatabase():
    """Delete all data!"""
    s = None
    with LOCK:
        try:
            s = Session()                 
            
            # Delete actual table data here:
            s.query(Event).delete() # Delete all events.

            # Commit changes!
            s.commit()
            SIGNAL.dispatch(True)
        except Exception as e:
            print(e)
            SIGNAL.dispatch(False, e)
            if s:
                s.rollback()    
        finally:
            if s:
                s.close()

def createDatabase(db):
    """
    Create a fully functional MySQL or PostgreSQL DB + table(s).
    """
    global ADDRESS, PORT, DB, USERNAME, PASSWD, USEMYSQL, Session, engine

    with LOCK:
        # Dispose of old DB connection + session.
        DB = db
        if engine:
            engine.dispose()
            Session.remove()
            Session = scoped_session(sessionmaker())

        # Connect to default / public DB -> Create new DB!
        engine = create_engine("{}{}:{}@{}:{}/{}".format("mysql+pymysql://" if USEMYSQL else "postgresql://", USERNAME, PASSWD, ADDRESS, PORT,  "" if USEMYSQL else "postgres"))
        conn = engine.connect()
        conn.execute("commit")
        conn.execute("CREATE DATABASE {}".format(db))
        conn.close()       
        engine.dispose()

        # Connect to the new DB + create new tables.      
        engine = create_engine("{}{}:{}@{}:{}/{}".format("mysql+pymysql://" if USEMYSQL else "postgresql://", USERNAME, PASSWD, ADDRESS, PORT, db))
        Base.metadata.create_all(engine, tables=[Event.__table__])
        time.sleep(1)
        engine.dispose()

        # Establish new session + refresh.
        engine = create_engine("{}{}:{}@{}:{}/{}".format("mysql+pymysql://" if USEMYSQL else "postgresql://", USERNAME, PASSWD, ADDRESS, PORT, DB))
        Session.configure(bind=engine)
