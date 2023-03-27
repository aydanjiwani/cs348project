# cs348project

Running instructions:
1. modify the app.config variables to match your database setup
2. `pip install -r requirements.txt`
3. while inside the directory, `python cs348main.py`
4. navigate to localhost:8000/init, the app will be running there

To preprocess data (inside `data` directory):
```
python3 cleaner.py
```

To seed the database (inside `data` directory):
```
python3 seed_basics.py "mysql+mysqldb://<username>:<password>@localhost"
python3 seed_flights.py "mysql+mysqldb://<username>:<password>@localhost"
```
