from flask import Flask, render_template, url_for, request, redirect, jsonify # Some will be used for form processing
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow, fields
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False            # Turn off SQLAlchemy high overhead warning
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///contacts.db' # Three slashes indicates a relative path

# Order matters (per https://flask-marshmallow.readthedocs.io/)
db = SQLAlchemy(app)    # 1st
ma = Marshmallow(app)   # 2nd

class Contact(db.Model):
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

    def __repr__(self):
        return  '<Contact "firstName": "%s", "lastName": "%s" >' % (self.firstName, self.lastName)

# Marshmallow serialization
# https://github.com/marshmallow-code/flask-marshmallow
class ContactSchema(ma.ModelSchema):
    class Meta:
        # Fields to expose
        model = Contact

contact_schema  = ContactSchema()
contacts_schema = ContactSchema(many=True)


"""
Form API - Supports builtin web interface
"""

# Get all data
@app.route('/', methods=['GET'])
def get_all():
    all_data = Contact.query.order_by(Contact.lastName, Contact.firstName).all()
    return render_template('index.html', contacts=all_data)


# Get one contact by id
@app.route('/contact/<string:id>')
def get_contact(id):
    contact = Contact.query.get(id)   # Select by primary key
    return render_template('view.html', contact=contact)


# Add a contact
# TODO - Validate birthday is a valid mm/dd/yyyy or is blank. Return error message otherwise.
@app.route('/contact', methods=['GET', 'POST'])
def add():
    if request.method == 'GET':
        return render_template('add.html')
    else:
        contact = Contact()
        contact.firstName = request.form['firstName']
        contact.lastName  = request.form['lastName']
        contact.street    = request.form['street']
        contact.city      = request.form['city']
        contact.state     = request.form['state']
        contact.zip       = request.form['zip']
        contact.phone     = request.form['phone']
        contact.email     = request.form['email']
        if request.form['birthday'].strip():
            contact.birthday = datetime.fromisoformat(request.form['birthday'].strip())

        try:
            db.session.add(contact)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your contact'


# Update a contact
@app.route('/update/<string:id>', methods=['GET', 'POST'])
def update(id):
    contact = Contact.query.get_or_404(id)    # Select by primary key

    if request.method == 'GET':
        return render_template('update.html', contact=contact)
    else:
        contact.firstName = request.form['firstName']
        contact.lastName  = request.form['lastName']
        contact.street    = request.form['street']
        contact.city      = request.form['city']
        contact.state     = request.form['state']
        contact.zip       = request.form['zip']
        contact.phone     = request.form['phone']
        contact.email     = request.form['email']
        if request.form['birthday'].strip():
            contact.birthday = datetime.fromisoformat(request.form['birthday'].strip())

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your contact'


# Delete a contact - Note different URL than REST API
@app.route('/delete/<string:id>')
def delete(id):
    contact = Contact.query.get_or_404(id)    # Select by primary key
    try:
        db.session.delete(contact)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was an issue deleting that contact'


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
    all_data = Contact.query.order_by(Contact.lastName, Contact.firstName).all()
    return jsonify(contacts_schema.dump(all_data))


# Get a contact
@app.route('/api/contact/<string:id>')
def rest_get_contact(id):
    contact = Contact.query.get_or_404(id)    # Select by primary key
    return contact_schema.dump(contact)


# Add a contact
@app.route('/api/contact', methods=['POST'])
def rest_add():
    request_data = request.get_json()

    contact = Contact()
    contact.firstName = request_data['firstName']
    contact.lastName  = request_data['lastName']
    contact.street    = request_data['street']
    contact.city      = request_data['city']
    contact.state     = request_data['state']
    contact.zip       = request_data['zip']
    contact.phone     = request_data['phone']
    contact.email     = request_data['email']
    contact.birthday  = datetime.fromisoformat(request_data['birthday'])

    try:
        db.session.add(contact)
        db.session.commit()

        # id was created on commit(). It's also populated back to our contact object!
        new_id = contact.id
        added_contact = Contact.query.get_or_404(new_id)
        return contact_schema.dump(added_contact)
    except:
        return 'There was an issue adding your contact'


# Update a contact
@app.route('/api/contact', methods=['PUT'])
def rest_update():
    request_data = request.get_json()         # Get data sent to us
    id = request_data['id']
    contact = Contact.query.get_or_404(id)    # Get current data from the db by primary key

    contact.firstName = request_data['firstName']
    contact.lastName  = request_data['lastName']
    contact.street    = request_data['street']
    contact.city      = request_data['city']
    contact.state     = request_data['state']
    contact.zip       = request_data['zip']
    contact.phone     = request_data['phone']
    contact.email     = request_data['email']
    contact.birthday  = datetime.fromisoformat(request_data['birthday'])

    try:
        db.session.commit()

        updated_contact = Contact.query.get_or_404(id)
        return contact_schema.dump(updated_contact)
    except:
        return 'There was an issue adding your contact'


# Delete a contact
@app.route('/api/contact/<string:id>', methods=['DELETE'])
def rest_delete(id):
    contact = Contact.query.get_or_404(id)    # Select by primary key
    try:
        db.session.delete(contact)
        db.session.commit()
        return ('', 204)
    except:
        return 'There was an issue deleting contact ' + id


# Reload/Reinitialize data
@app.route('/api/contact/initialize', methods=['POST'])
def rest_initialize():
    try:
        # Delete all data from the 'Contact' table
        db.session.query(Contact).delete()
        db.session.commit()
        # Reset rowid for the 'Contact' table. This way we know the ids for test access to the data.
        db.engine.execute("reindex 'Contact'")
        db.session.commit()

        fred =   Contact(firstName='Fred',  lastName='Flintstone', street='345 Cave Stone Rd', city='Bedrock', state='NA', zip='123', phone='1', email='fred@bedrock.com',  birthday=datetime.fromisoformat('1970-01-01'))
        wilma =  Contact(firstName='Wilma', lastName='Flintstone', street='345 Cave Stone Rd', city='Bedrock', state='NA', zip='123', phone='1', email='wilma@bedrock.com', birthday=datetime.fromisoformat('1970-02-01'))
        barney = Contact(firstName='Barney',lastName='Rubble',     street='123 Granite St',    city='Bedrock', state='NA', zip='123', phone='2', email='barney@bedrock.com',birthday=datetime.fromisoformat('1970-03-01'))
        betty =  Contact(firstName='Betty', lastName='Rubble',     street='123 Granite St',    city='Bedrock', state='NA', zip='123', phone='2', email='betty@bedrock.com', birthday=datetime.fromisoformat('1970-04-01'))

        db.session.add(fred)
        db.session.add(wilma)
        db.session.add(barney)
        db.session.add(betty)
        db.session.commit()

        all_data = Contact.query.order_by(Contact.lastName, Contact.firstName).all()
        return jsonify(contacts_schema.dump(all_data))
    except:
        return 'There was an issue deleting contact ' + id

# When run from the commandline, launch a local server. This is for development only!
if __name__ == "__main__":
    app.run(debug=True)
