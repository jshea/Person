from flask import Flask, render_template, url_for, request, redirect, jsonify # Some will be used for form processing
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
# from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False            # Turn off SQLAlchemy high overhead warning
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///contacts.db' # Three slashes indicates a relative path

# Order matters
db = SQLAlchemy(app)    # 1st
ma = Marshmallow(app)   # 2nd

class Contact(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name  = db.Column(db.String(100), nullable=False)
    street     = db.Column(db.String(100))
    city       = db.Column(db.String(100))
    state      = db.Column(db.String(2))
    zip        = db.Column(db.String(5))
    phone      = db.Column(db.String(10))
    email      = db.Column(db.String(100))
    birthday   = db.Column(db.String(10))

    def __repr__(self):
        return  '<Contact "first_name": "%s", "last_name": "%s" >' % (self.first_name, self.last_name)

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
    all_data = Contact.query.order_by(Contact.last_name, Contact.last_name).all()
    return render_template('index.html', contacts=all_data)


# Get one contact by id
@app.route('/contact/<string:id>')
def get_contact(id):
    contact = Contact.query.get(id)   # Select by primary key
    return contact                   # TODO - Check FreeCodeCamp example


# Add a contact - show form
@app.route('/add', methods=['GET'])
def add_form():
    return render_template('add.html')


# Add a contact
@app.route('/contact', methods=['POST'])
def add():
    contact = Contact()
    contact.first_name = request.form['first_name']
    contact.last_name  = request.form['last_name']

    try:
        db.session.add(contact)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was an issue adding your task'


# Update a contact
@app.route('/update/<string:id>', methods=['GET', 'POST'])
def update(id):
    contact = Contact.query.get_or_404(id)    # Select by primary key

    if request.method == 'POST':
        contact.first_name = request.form['first_name']
        contact.last_name  = request.form['last_name']
        contact.street     = request.form['street']
        contact.city       = request.form['city']
        contact.state      = request.form['state']
        contact.zip        = request.form['zip']
        contact.phone      = request.form['phone']
        contact.email      = request.form['email']
        contact.birthday   = request.form['birthday']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your task'
    else:
        return render_template('update.html', contact=contact)


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
    all_data = Contact.query.order_by(Contact.last_name, Contact.last_name).all()
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
    contact.first_name = request_data['first_name']
    contact.last_name  = request_data['last_name']
    contact.street     = request_data['street']
    contact.city       = request_data['city']
    contact.state      = request_data['state']
    contact.zip        = request_data['zip']
    contact.phone      = request_data['phone']
    contact.email      = request_data['email']
    contact.birthday   = request_data['birthday']

    try:
        db.session.add(contact)
        db.session.commit()

        new_id = contact.id
        added_contact = Contact.query.get_or_404(new_id)
        return contact_schema.dump(added_contact)
    except:
        return 'There was an issue adding your task'


# Delete a contact
@app.route('/api/contact/<string:id>', methods=['DELETE'])
def rest_delete(id):
    contact = Contact.query.get_or_404(id)    # Select by primary key
    try:
        db.session.delete(contact)
        db.session.commit()
        return ('', 204)
    except:
        return 'There was an issue deleting that contact'

# When run from the commandline, launch a local server. This is for development only!
if __name__ == "__main__":
    app.run(debug=True)
