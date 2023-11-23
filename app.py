import mysql.connector
from flask import Flask, request, jsonify, session
import datetime
import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
from tensorflow import keras
from flask_jwt_extended import create_access_token
import bcrypt

app = Flask(__name__)

# Set up MySQL connection
mysql_connection = mysql.connector.connect(
    host='127.0.0.1',
    user='root',
    password='2017',
    database='findme'
)

@app.route('/testpage')
def testpage():
    return jsonify(message='all good!')

@app.route("/userRegister", methods=['POST'])
def userRegister():
    if request.method == 'POST':
        cursor = mysql_connection.cursor(dictionary=True)

        # Check if email, username, and phone already exist
        email = request.json['email']
        username = request.json['username']
        phone = request.json['phone']

        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_email = cursor.fetchone()

        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_username = cursor.fetchone()

        if existing_email:
            cursor.close()
            return jsonify(message='Email already exists'), 401
        if existing_username:
            cursor.close()
            return jsonify(message='Username already exists'), 401
        if existing_phone:
            cursor.close()
            return jsonify(message='Phone Number already exists'), 401
        
        if request.json['password'] != request.json['cpassword']:
            cursor.close()
            return jsonify(message='Password Not Matching!'), 401
        
        # Hash Passwords
        hashpw = bcrypt.hashpw(request.json['password'].encode('utf-8'), bcrypt.gensalt())
        hashCpw = bcrypt.hashpw(request.json['cpassword'].encode('utf-8'), bcrypt.gensalt())

        # Generate access token
        access_token = create_access_token(identity=email)

        # Insert user into MySQL
        cursor.execute("INSERT INTO users (email, password, cpassword, username, phone, tokens) VALUES (%s, %s, %s, %s, %s, %s)", (email, hashpw, hashCpw, username, phone, str(access_token)))
        mysql_connection.commit()

        cursor.close()

        # Set session email (if needed)
        session['email'] = email

        return jsonify(token=str(access_token)), 201
    

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
            cursor.execute("UPDATE users SET tokens = %s WHERE email = %s",
                           str(access_token), email)
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
    cursor = mysql_connection.cursor(dictionary=True)

    # Retrieve all services from MySQL
    cursor.execute("SELECT * FROM services")
    services = cursor.fetchall()

    cursor.close()

    # Convert the result to JSON
    services_json = json.dumps(services, indent=2)
    services_list = json.loads(services_json)

    return jsonify(services_list), 201

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
    app.run(debug=True)
