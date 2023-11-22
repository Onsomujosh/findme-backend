import mysql.connector
from flask import Flask, request, jsonify, session
from flask_jwt_extended import create_access_token
import bcrypt

app = Flask(__name__)

# Set up MySQL connection
mysql_connection = mysql.connector.connect(
    host='',
    user='',
    password='',
    database=''
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
            return jsonify(message='PAssword Not MAtching!'), 401
        
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
    


# Close MySQL connection when application exits
@app.teardown_appcontext
def close_db(error):
    if 'mysql_connection' in globals():
        mysql_connection.close()



if __name__ == "__main__":
    app.run(debug=True)
