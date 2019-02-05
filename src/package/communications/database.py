""" SQLAlchemy Definitions + Session Creation (using PostgreSQL) """

import psycopg2
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, BIGINT, String, SMALLINT, TIMESTAMP, MetaData
from sqlalchemy.orm import sessionmaker

engine = create_engine("postgresql://postgres:booty@localhost/rover")
Base = declarative_base()
Session = sessionmaker(bind=engine)
SESSIONS = list()


class Event(Base):
    __tablename__ = "event"
    id = Column(BIGINT, primary_key=True)
    message = Column(String)
    severity = Column(SMALLINT)
    type = Column(SMALLINT)
    time = Column(TIMESTAMP)

    def __repr__(self):
        return "Sensor.Event(msg={}, sev={}, typ={}, time={})".format(self.message, self.severity, self.type, self.time)

    def add(session, msg, severity, type, time, autocommit=True):
        """
        Add a new event to the DB.
        """
        session.add(Event(message=msg, severity=severity, type=type, time=time))
        if autocommit:
            session.commit()

    def findByType(session, type):
        output = list()
        for e in session.query(Event).filter_by(type=type).all():
            output.append(e)
        return output


def createNewDBSession(schema=None):
    """
    Returns a new DB session, should only be used on the calling thread!
    Remember to close the session when done!!!
    """
    global SESSIONS

    s = Session()
    if schema:  # Use the right schema! Uses public otherwise.
        # TODO, this statement will be evicted during rollbacks, pitfal?
        s.execute('set search_path={}'.format(schema))

    SESSIONS.append(s)
    return s


def closeDBSession(session):
    """
    Close session gracefully.
    """
    global SESSIONS
    SESSIONS.remove(session)
    session.close()


def closeDBSessions():
    """
    Closes all dormant sessions.
    """
    global SESSIONS

    for s in SESSIONS:
        s.close()

    SESSIONS.clear()
