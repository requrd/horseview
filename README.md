# JRDB-Model
ORM for JRDB with flask-sqlalchemy.  
You can store jrdb dataset to your database.  
This repository does not have fetching scripts.

## Setup
set your environmental variable below.  
e.g.  
`DB="sqlite:///tmp/jrdb.db"`  
https://flask-sqlalchemy.palletsprojects.com/en/2.x/config/

## Usage
### Install
```
pip install jrdb_model
```

### Load dataset
```
from jrdb_model import KaisaiData, create_app

app = create_app()
with app.app_context():
    kaisais = KaisaiData.query.filter_by(ymd='20181118').all()
```

### Engine options
`create_app()` enables `pool_pre_ping` by default, so connections closed by the
server (e.g. `wait_timeout` or a DB restart) are replaced instead of raising
"MySQL server has gone away". Pass `engine_options` to override it or to add
other `create_engine` options.
```
app = create_app(engine_options={"pool_recycle": 3600})
```