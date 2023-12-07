from sqlalchemy import create_engine
from flask import Flask, request, jsonify, session, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import create_access_token
from flask_wtf import FlaskForm
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import tensorflow as tf
import tensorflow_hub as hub
from tensorflow import keras
import numpy as np
from flask_bcrypt import Bcrypt
import json
import datetime
from os import environ

#Create a Flask Instance
app = Flask(__name__)

# Initialize the Database
#db = SQLAlchemy(app)
#migrate = Migrate(app, db)
#db.init_app(app)

#Add Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://findme:findme@localhost/findme'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # silence the deprication warning
#Secret Key
app.config['SECRET_KEY'] = "findme"

# Create the SQLAlchemy engine
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

db = SQLAlchemy(app)
migrate = Migrate(app, db)
#db.init_app(app)
#Initialize Bcrypt
bcrypt = Bcrypt(app)

#Define Models
class User(db.Model):
    """User definitions"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = Column(String(128), nullable=False)
    password = Column(String(128), nullable=False)
    first_name = Column(String(128), nullable=False)
    last_name = Column(String(128), nullable=False)
    contact = Column(String(128), nullable=False)
    location = Column(String(128), nullable=False)
    places = db.relationship('Place', backref='user', cascade='all, delete, delete-orphan')
    reviews = db.relationship('Review', backref='user', cascade='all, delete, delete-orphan')

class Employer(db.Model):
    """Employer definitions"""
    __tablename__ = "employers"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = Column(String(128), nullable=False)
    password = Column(String(128), nullable=False)
    first_name = Column(String(128), nullable=False)
    contact = Column(String(128), nullable=False)

class Place(db.Model):
    """Maybe change to service ama?"""

    __tablename__ = 'places'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    comments = db.relationship('Review', backref='place', cascade='all, delete, delete-orphan')


class Service(db.Model):
    """Service class to store service information"""

    ___tablename__ = 'services'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
#    comments = db.relationship('Review', backref='service', cascade='all, delete, delete-orphan', foreign_keys='Review.place_id')

    def __repr__(self):
        return f'<Service {self.name}>'
    

class Review(db.Model):
    """ Review class to store review information """

    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    place_id = db.Column(db.Integer, db.ForeignKey('places.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    text = db.Column(String(1024), nullable=False)


    #Create A String
    def __repr__(self):
        return '<Name %r>' % self.name
    
# Create a Form Class
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    submit = SubmitField("Submit")   

# Set up MySQL connection
# mysql_connection = mysql.connector.connect(
#    host='127.0.0.1',
#    user='findme',
#    password='findme',
#    database='findme'
#)

# @app.route('/', strict_slashes=False)
# def testpage():
#    return jsonify(message='all good!')

@app.route('/', strict_slashes=False)
def home_page():
    return render_template('/index.html')

@app.route('/registration.html', strict_slashes=False)
def registration_page():
    return render_template('registration.html')

@app.route('/index.html', strict_slashes=False)
def index_page():
    return render_template('index.html')

@app.route('/services.html', strict_slashes=False)
def services_page():
    # Fetch services data from the database
    services = db.session.query(User).all()
    services_list2 = []
    for service in services:
        key_value = {"id": service.id, "name": service.first_name, "contact": service.contact, "location": service.location}
        services_list2.append(key_value)
#services_list2 = [{"id":1, "name":"Eric", "contact":7001, "location":"Kenya"}]
    #Pass the services data to the template
    return render_template('services.html', services=services_list2)

@app.route('/application.html', strict_slashes=False)
def application_page():
    return render_template('services.html')

@app.route('/registration.html', methods=['GET', 'POST'])
def add_register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        contact = request.form['contact']
        employer = Employer(first_name=username, email=email, password=password, contact=contact)
        db.session.add(employer)
        db.session.commit()
    return render_template('services.html')

@app.route('/application2.html', methods=['GET', 'POST'])
def add_applicant():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        password = request.form['password']
        contact = request.form['contact']
        location = request.form['location']
        applicant = User(first_name=firstname, last_name=lastname, email=email, password=password, contact=contact, location=location)
        db.session.add(applicant)
        db.session.commit()
    return render_template('services.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        # Logic for sending a password reset email
        flash('PAssword reset email sent successfully!', 'success')
        return redirect("/registration.html")
    
    return render_template('forgot_password.html')

@app.route("/userLogin", methods=['POST'])
def userLogin():
    if request.method == 'POST':
        cursor = mysql_connection.cursor(dictionary=True)

        email = request.json['email']
        password = request.json['password']

        #Retrieve user from MySQL
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            access_token = create_access_token(identity=email)
            user['tokens'].append({'token': str(access_token)})

            # Update user's tokens in MySQL
            cursor.execute("UPDATE users SET tokens = JSON_ARRAY_APPEND(tokens, '$', %s) WHERE email = %s",
                           (str(access_token), email))
            mysql_connection.commit()

            cursor.close()
            return jsonify(token=str(access_token)), 201
        
        cursor.close()
        return jsonify(message='Invalid Username/Password'), 401  


@app.route("/getUserData", methods=['POST'])
def getUserData():
    if request.method == 'POST':
        cursor = mysql_connection.cursor(dictionary=True)

        # Retrieve user from MySQL based on the authentication token
        cursor.execute("SELECT * FROM users WHERE tokens LIKE %s", ('%' + request.json['auth'] + '%',))
        user = cursor.fetchone()

        cursor.close()

        if user:
            return jsonify(user), 201
        
        return jsonify(message='Something went wrong'), 401
    

@app.route("/getAllServices", methods=['GET'])
def getAllServices():
    #cursor = mysql_connection.cursor(dictionary=True)

    # Retrieve all services from MySQL
    services = db.session.query(Service).all()

    # Convert the services to a list of dictionaries
#   services_list = [
#       {
#           "id": service.id,
#           "name": service.first_name,
#           "contact": service.contact,
#           "location": service.location,
#       }
#       for service in services
#    ]
    services_list2 = []
    for service in services:
        key_value = {"id": service.id, "name": service.first_name, "contact": service.contact, "location": service.location}
        services_list2.append(key_value)
    # Convert the result to JSON
    #services_json = json.dumps(services, indent=2)
    #services_list = json.loads(services_json)

    return jsonify(services_list2), 201


@app.route("/addComments", methods=['POST'])
def addComments():
    comment = request.json['comment']
    uid = request.json['uid']
    pid = request.json['pid']
    date = datetime.datetime.now()

    try:
        model = keras.models.load_model('sentimentAnalysis.h5', custom_objects={'KerasLayer': hub.KerasLayer})
        pred = model.predict([comment])[0][0]
        sentiment = 1 if pred >= 0.5 else 0

        cursor = mysql_connection.cursor(dictionary=True)

        # Retrieve username based on user ID
        cursor.execute("SELECT username FROM users WHERE _id = %s", (uid,))
        user_data = cursor.fetchone()
        username = user_data['username']

        # Insert comment into MySQL
        cursor.execute("INSERT INTO comments (uid, pid, username, comment, sentiment, date) VALUES (%s, %s, %s, %s, %s, %s)",
                       (uid, pid, username, comment, sentiment, date))
        mysql_connection.commit()

        cursor.close()
        return jsonify(message='Thank you for your Feedback!'), 201
    
    except Exception as e:
        print(e)
        return jsonify(message='Something went Wrong'), 401
    

@app.route("/logoutUser", methods=['POST'])
def logoutUser():
    if request.method =='POST':
        cursor = mysql_connection.cursor(dictionary=True)

        # Retrieve user from MySQL based on the authentication token
        cursor.execute("SELECT * FROM users WHERE token LIKE %s", ('%' + request.json['auth'] + '%',))
        user = cursor.fetchone()

        if user:
            # Clear tokens for logout
            cursor.execute("UPDATE users SET tokens = %s WHERE _id = %s", ('[]', user['_id']))
            mysql_connection.commit()

            cursor.close()

            return jsonify(message='Logout Successful!'), 201
        
        return jsonify(message='Something went wrong!'), 401
    


# Close MySQL connection when application exits
@app.teardown_appcontext
def close_db(error):
    if 'mysql_connection' in globals():
        mysql_connection.close()


if __name__ == "__main__":
    with app.app_context():
        # Create the database tables
        db.create_all()
    app.run(host='0.0.0.0', port=5000)
