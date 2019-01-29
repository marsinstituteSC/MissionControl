""" Testing SQLAlchemy with PostgreSQL """

import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, BIGINT, String
from sqlalchemy.orm import sessionmaker

engine = create_engine("postgresql://postgres:booty@localhost/sensors")
Base = declarative_base()
Session = sessionmaker(bind=engine)


class Temperature(Base):
    __tablename__ = "temperature" # Required!!!
    id = Column(BIGINT, primary_key=True)
    message = Column(String)
    value = Column(Integer)

    def __repr__(self): # Used for printing!
        return "<Temperature(id={}, message={}, value={})>".format(self.id, self.message, self.value)


def testPostgreSQLManually():
    """Non-ORM way, a lot more verbose!!!"""
    conn = psycopg2.connect("dbname=sensors user=postgres password=booty")
    try:
        cur = conn.cursor()
        #cur.execute("INSERT INTO temperature (id, message, value) VALUES(3, 'woop', 25)")
        cur.execute("SELECT * FROM temperature")
        for data in cur:
            print(data)
        #conn.commit()
        cur.close()
    except Exception as e:
        print(str(e))
    finally:
        conn.close()


def printTemperatureTable(s):
    for data in s.query(Temperature):
        print(data)


def addNewItemToTemperatureTable(s, idx, msg, val):
    newTempMeasurement = Temperature(id=idx, message=msg, value=val)
    s.add(newTempMeasurement)
    s.commit()
    print("\n")


if __name__ == "__main__":
    session = Session()
    printTemperatureTable(session)
    addNewItemToTemperatureTable(session, 5, "hello world", 45)
    printTemperatureTable(session)
    session.close()
