# Python web service example
This is a learning example web application using Python, Flask, SQLAlchemy, Marshmallow, Jinja and other libraries.

![high level overview](./HighLevelOverview.png)

## Setup cheat sheet

### Setup a virtual environment
```bash
python -m venv env    # One time environment creation
env\Scripts\activate  # Activate the environment in a new shell
```

### Install Libs
```bash
pip install flask flask-sqlalchemy flask_marshmallow gunicorn # Not a comprehensive list of libs
```

### Freeze (and use) lib requirements
```bash
pip freeze > requirements.txt     # Write libs to a requirements.txt file. Run after adding or updating libs.
pip install -r requirements.txt   # Install libs after a git clone or pull of updated requirements.txt
```

### Initialize the sqlite database - In the shell:
```
python
>>> from app import db, Contact
>>> db.create_all()

# Optionally seed some data

fred = Contact(first_name='Fred', last_name='Flintstone', street='345 Cave Stone Rd', city='Bedrock', state='NA', zip='123', phone='1', email='fred@bedrock.com', birthday='1970-01-01')
wilma = Contact(first_name='Wilma', last_name='Flintstone', street='345 Cave Stone Rd', city='Bedrock', state='NA', zip='123', phone='1', email='wilma@bedrock.com', birthday='1970-02-01')
barney = Contact(first_name='Barney', last_name='Rubble', street='123 Granite', city='Bedrock', state='NA', zip='123', phone='2', email='barney@bedrock.com', birthday='1970-03-01')
betty = Contact(first_name='Betty', last_name='Rubble', street='123 Granite', city='Bedrock', state='NA', zip='123', phone='2', email='betty@bedrock.com', birthday='1970-04-01')

db.session.add(fred)
db.session.add(wilma)
db.session.add(barney)
db.session.add(betty)
db.session.commit()

Contact.query.all()

>>> exit()
```

## Some libs used
[Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/)

[SQLAlchemy](https://sqlalchemy.org/) which is comprised of [ORM and Core](https://docs.sqlalchemy.org/en/13/)

[Flask-Marshmallow](https://flask-marshmallow.readthedocs.io/)

[Marshmallow](https://marshmallow.readthedocs.io/)
