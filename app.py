from flask import Flask, render_template, url_for, request, redirect, jsonify # Some will be used for form processing
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow, fields
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False          # Turn off SQLAlchemy high overhead warning
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///person.db' # Three slashes indicates a relative path

# Order matters (per https://flask-marshmallow.readthedocs.io/)
db = SQLAlchemy(app)    # 1st
ma = Marshmallow(app)   # 2nd

class Person(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(100), nullable=False)
    lastName  = db.Column(db.String(100), nullable=False)
    street    = db.Column(db.String(100))
    city      = db.Column(db.String(100))
    state     = db.Column(db.String(2))
    zip       = db.Column(db.String(5))
    phone     = db.Column(db.String(10))
    email     = db.Column(db.String(100))
    birthday  = db.Column(db.DateTime)
    hobbies   = db.relationship('Hobby', backref='person', lazy=True)
    pets      = db.relationship('Pet',   backref='person', lazy=True)

    def __repr__(self):
        return  '<Person "firstName": "%s", "lastName": "%s" >' % (self.firstName, self.lastName)

class Hobby(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    name      = db.Column(db.String(100), nullable=False)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)

class Pet(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    name      = db.Column(db.String(120), nullable=False)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)


# Marshmallow serialization
# https://github.com/marshmallow-code/flask-marshmallow
class HobbySchema(ma.ModelSchema):
    class Meta:
        # Fields to expose
        model = Hobby

class PetSchema(ma.ModelSchema):
    class Meta:
        # Fields to expose
        model = Pet

class PersonSchema(ma.ModelSchema):
    hobbies = ma.Nested(HobbySchema, many=True)
    pets = ma.Nested(PetSchema, many=True)
    class Meta:
        # Fields to expose
        model = Person

person_schema  = PersonSchema()
people_schema = PersonSchema(many=True)



"""
Form API - Supports builtin web interface
"""

# Get all data
@app.route('/', methods=['GET'])
def get_all():
    all_data = Person.query.order_by(Person.lastName, Person.firstName).all()
    return render_template('index.html', person=all_data)


# Get one person by id
@app.route('/person/<string:id>')
def get_person(id):
    person = Person.query.get(id)   # Select by primary key
    return render_template('view.html', person=person)


# Add a person
# TODO - Validate birthday is a valid mm/dd/yyyy or is blank. Return error message otherwise.
@app.route('/person', methods=['GET', 'POST'])
def add():
    if request.method == 'GET':
        return render_template('add.html')
    else:
        person = Person()
        person.firstName = request.form['firstName']
        person.lastName  = request.form['lastName']
        person.street    = request.form['street']
        person.city      = request.form['city']
        person.state     = request.form['state']
        person.zip       = request.form['zip']
        person.phone     = request.form['phone']
        person.email     = request.form['email']
        if request.form['birthday'].strip():
            person.birthday = datetime.fromisoformat(request.form['birthday'].strip())

        try:
            db.session.add(person)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your person'


# Update a person
@app.route('/update/<string:id>', methods=['GET', 'POST'])
def update(id):
    person = Person.query.get_or_404(id)    # Select by primary key

    if request.method == 'GET':
        return render_template('update.html', person=person)
    else:
        person.firstName = request.form['firstName']
        person.lastName  = request.form['lastName']
        person.street    = request.form['street']
        person.city      = request.form['city']
        person.state     = request.form['state']
        person.zip       = request.form['zip']
        person.phone     = request.form['phone']
        person.email     = request.form['email']
        if request.form['birthday'].strip():
            person.birthday = datetime.fromisoformat(request.form['birthday'].strip())

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your person'


# Delete a person - Note different URL than REST API
@app.route('/delete/<string:id>')
def delete(id):
    person = Person.query.get_or_404(id)    # Select by primary key
    try:
        db.session.delete(person)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was an issue deleting that person'


# About
@app.route('/about', methods=['GET'])
def about_form():
    return render_template('about.html')


"""
REST API - Supports the generic REST interface
"""

# Get all data
@app.route('/api/all/', methods=['GET'])
def rest_get_all():
    all_data = Person.query.order_by(Person.lastName, Person.firstName).all()
    return jsonify(people_schema.dump(all_data))


# Get a person
@app.route('/api/person/<string:id>')
def rest_get_person(id):
    person = Person.query.get_or_404(id)    # Select by primary key
    return person_schema.dump(person)


# Add a person
@app.route('/api/person', methods=['POST'])
def rest_add():
    request_data = request.get_json()

    person = Person()
    person.firstName = request_data['firstName']
    person.lastName  = request_data['lastName']
    person.street    = request_data['street']
    person.city      = request_data['city']
    person.state     = request_data['state']
    person.zip       = request_data['zip']
    person.phone     = request_data['phone']
    person.email     = request_data['email']
    person.birthday  = datetime.fromisoformat(request_data['birthday'])

    try:
        db.session.add(person)
        db.session.commit()

        # id was created on commit(). It's also populated back to our person object!
        new_id = person.id
        added_person = Person.query.get_or_404(new_id)
        return person_schema.dump(added_person)
    except:
        return 'There was an issue adding your person'


# Update a person
@app.route('/api/person', methods=['PUT'])
def rest_update():
    request_data = request.get_json()         # Get data sent to us
    id = request_data['id']
    person = Person.query.get_or_404(id)    # Get current data from the db by primary key

    person.firstName = request_data['firstName']
    person.lastName  = request_data['lastName']
    person.street    = request_data['street']
    person.city      = request_data['city']
    person.state     = request_data['state']
    person.zip       = request_data['zip']
    person.phone     = request_data['phone']
    person.email     = request_data['email']
    person.birthday  = datetime.fromisoformat(request_data['birthday'])

    try:
        db.session.commit()

        updated_person = Person.query.get_or_404(id)
        return person_schema.dump(updated_person)
    except:
        return 'There was an issue adding your person'


# Delete a person
@app.route('/api/person/<string:id>', methods=['DELETE'])
def rest_delete(id):
    person = Person.query.get_or_404(id)    # Select by primary key
    try:
        db.session.delete(person)
        db.session.commit()
        return ('', 204)
    except:
        return 'There was an issue deleting person ' + id


# Reload/Reinitialize data
@app.route('/api/person/initialize', methods=['POST'])
def rest_initialize():
    try:
        # Delete all data from the 'Person' table
        db.session.query(Person).delete()
        db.session.query(Hobby).delete()
        db.session.query(Pet).delete()
        db.session.commit()
        # Reset rowid for the tables. This way we know the ids for test access to the data.
        db.engine.execute("reindex 'Person'")
        db.engine.execute("reindex 'Hobby'")
        db.engine.execute("reindex 'Pet'")
        db.session.commit()

        fred = Person(firstName='Fred', lastName='Flintstone', street='345 Cave Stone Rd', city='Bedrock', state='NA', zip='123', phone='1', email='fred@bedrock.com', birthday=datetime.fromisoformat('1970-01-01'))
        fred.hobbies.append(Hobby(name='Duct Tape Art'))
        fred.hobbies.append(Hobby(name='Handcuff Collecting'))
        fred.hobbies.append(Hobby(name='Beetle Fighting'))
        fred.pets.append(Pet(name='Droolius Caesar'))
        fred.pets.append(Pet(name='Catabunga'))

        wilma = Person(firstName='Wilma', lastName='Flintstone', street='345 Cave Stone Rd', city='Bedrock', state='NA', zip='123', phone='1', email='wilma@bedrock.com', birthday=datetime.fromisoformat('1970-02-01'))
        wilma.hobbies.append(Hobby(name='Javelin Catching'))
        wilma.hobbies.append(Hobby(name='Competitive Rock Paper Scissors'))
        wilma.pets.append(Pet(name='Sarah Jessica Barker'))
        wilma.pets.append(Pet(name='Winnie the Poodle'))

        barney = Person(firstName='Barney',lastName='Rubble', street='123 Granite St', city='Bedrock', state='NA', zip='123', phone='2', email='barney@bedrock.com', birthday=datetime.fromisoformat('1970-03-01'))
        barney.hobbies.append(Hobby(name='Time travel'))
        barney.hobbies.append(Hobby(name='Snake skin collecting'))
        barney.hobbies.append(Hobby(name='Arguing with people online'))
        barney.pets.append(Pet(name='Salvador Dogi'))
        barney.pets.append(Pet(name='Schrodinger'))

        betty = Person(firstName='Betty', lastName='Rubble', street='123 Granite St', city='Bedrock', state='NA', zip='123', phone='2', email='betty@bedrock.com', birthday=datetime.fromisoformat('1970-04-01'))
        betty.hobbies.append(Hobby(name='Stalking celebrities'))
        betty.hobbies.append(Hobby(name='Ferret racing'))
        betty.pets.append(Pet(name='Sir Barks-a-Lot'))
        betty.pets.append(Pet(name='Thundercat'))


        db.session.add(fred)
        db.session.add(wilma)
        db.session.add(barney)
        db.session.add(betty)
        db.session.commit()

        all_data = Person.query.order_by(Person.lastName, Person.firstName).all()
        return jsonify(people_schema.dump(all_data))
    except Exception as e:
        return 'There was an issue initializing the data store - ' + str(e)

# When run from the commandline, launch a local server. When functions are
# imported into another program this file doesn't run.
if __name__ == "__main__":
    app.run(debug=True)
