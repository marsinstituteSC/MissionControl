
# MissionControl
Mission Control Center Application for MISC's Mars Rover, Viking III

## Prerequisites
* pip install pyqt5 (for PyQt itself)
* pip install pyqt5-tools (for Qt Designer)
* pip install opencv-python (for camera streaming)
* pip install opencv-contrib-python (for camera streaming)
* pip install roslibpy (uncertain if we need this yet)
* pip install pygame (for gamepad)
* pip install matplotlib (for plots/graphs, should already be installed in the Anaconda distribution by default, however other dependencies might be needed https://matplotlib.org/users/installing.html)
* pip install qdarkstyle (for darkmode)
* pip install psycopg2 (for PostgreSQL connector)
* pip install SQLAlchemy (ORM for PostgreSQL)
* PostgreSQL Server 64-bit https://www.postgresql.org/download/ OR 32-bit https://www.postgresql.org/ftp/binary/v8.3.20/win32/
* OpenCV Disclaimer: If you get import errors for cv2 module, fetch opencv_python-4.0.1-cp36-cp36m-win32 (or 64-bit version) from https://www.lfd.uci.edu/~gohlke/pythonlibs/
* Qt Disclaimer: If you get Qt issues try to install Qt Core (Open-Source) via https://www.qt.io/download