""" 
PostgreSQL testing, using:
SQLAlchemy (ORM) and psycopg2 (NON-ORM)

The purpose of this script is to roughly demonstrate the differences between the ORM and traditional SQL connector technique.
"""

import psycopg2
from sqlalchemy import create_engine, Column, Integer, BIGINT, String, SMALLINT, TIMESTAMP, MetaData, desc, and_, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine("postgresql://postgres:xys@localhost/db")
Base = declarative_base()
Session = sessionmaker(bind=engine)

class Event(Base):
    __tablename__ = "event" # Required
    id = Column(BIGINT, primary_key=True)
    message = Column(String(128))
    severity = Column(SMALLINT)
    type = Column(SMALLINT)
    time = Column(TIMESTAMP)

    def __repr__(self): # For printing, x = Event() : print(x)
        return "Event(msg={}, sev={}, type={}, time={})".format(self.message, self.severity, self.type, self.time)

def readAllManually():
    conn = psycopg2.connect("dbname=db user=postgres password=xyz")
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM event")
        for data in cur:
            print(data)
        cur.close()
    except Exception as e:
        print(str(e))
    finally:
        conn.close()

def insertManually():
    conn = psycopg2.connect("dbname=db user=postgres password=xyz")
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO event (id, message, severity, type, time) VALUES(1, 'xyz', 0, 0, '2019-05-15 14:00:00')")
        conn.commit()
        cur.close()
    except Exception as e:
        print(str(e))
    finally:
        conn.close()

def readAllORM(session):
    for data in session.query(Event):
        print(data)

def insertORM(session):
    newEvent = Event(id=2, message='xyz', severity=0, type=0, time='2019-05-15 14:00:00')
    session.add(newEvent) # Cache new row until committed.
    session.commit() # Flush + Commit change to DB.

if __name__ == "__main__":
    insertManually()
    readAllManually()    

    session = Session()
    insertORM()
    readAllORM()
    session.close()
