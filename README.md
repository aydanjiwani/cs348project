## Flights Application

The Flights Application is a database-driven web application that allows users to search for and manage flight information.

### Getting Started

These instructions will help you set up the Flights Application on your local machine for development and testing purposes.

#### Prerequisites

Create a new MySQL database and user for the application. Note the database name, username, and password for use in the next step.

#### Data preprocessing

To preprocess data (inside `data` directory):

```
python3 cleaner.py
```

To seed the database (inside `data` directory):

```
python3 seed_basics.py "mysql+mysqldb://<username>:<password>@localhost/<database>"
python3 seed_flights.py "mysql+mysqldb://<username>:<password>@localhost/<database>"
```

#### Dependencies

Modify the enviornment variable to your database credentials:

```
DB_NAME = 'dbname'
DB_USER = 'dbuser'
DB_PWD = 'dbpassword'
```

Run the following:

```
pip install -r requirements.txt
python cs348main.py
```

Access the application in your web browser at localhost:8000/init
