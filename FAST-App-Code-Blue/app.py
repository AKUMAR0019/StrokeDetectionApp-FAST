from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.utils import redirect
from wtforms import form 
from strokedetectapp.forms import SignupForm
from flask import Flask, render_template, Response, jsonify, url_for, redirect, request
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.preprocessing import image
import numpy as np
import cv2
import pickle
import os
from flask import Flask, flash
from werkzeug.utils import secure_filename
import time
from flask_wtf import FlaskForm
from wtforms import StringField,TextAreaField,SubmitField,PasswordField,DateField,SelectField
from wtforms import validators
from wtforms.validators import DataRequired,Email,EqualTo,Length
from flask import Flask, render_template, Response, jsonify, url_for
from tensorflow.keras.preprocessing import image
from flask import Flask, flash, request, redirect, url_for
from flask import session
from flask import Flask
from flask import url_for
from flask import redirect
from flask import request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask_login import current_user, login_user
from flask_login import login_required, current_user, login_user, logout_user


class LoginForm(FlaskForm):
    email = StringField("Enter your email", validators=[DataRequired(),Email()])
    password = PasswordField("Password", validators=[DataRequired(),Length(min=6,max=16)])
    submit = SubmitField("Log In")

class SignupForm(FlaskForm):
    email = StringField("Enter your email", validators=[DataRequired(),Email()])
    password = PasswordField("Password", validators=[DataRequired(),Length(min=6,max=16)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(),EqualTo(password)])
    emergency_contact = SelectField('Choose your preferred method of emergency contact when facial paralysis is detected', validators=[DataRequired()], choices=[('Call 911', 'Text Emergency Contact')] )
    submit = SubmitField("Sign Up")

gpus = tf.config.list_physical_devices("GPU")
try:
    for gpu in gpus:
        tf.config.experimental.set_memory_growth(gpu, True)
except:
    pass

# Connect camera to the application
camera = cv2.VideoCapture(0)

app = Flask(__name__)
app.config['SECRET_KEY']='thisisfirstflaskapp'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
UPLOAD_FOLDER = '/tmp'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user-table.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy()
 
class UserModel(UserMixin, db.Model):
    __tablename__ = 'users'
 
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True)
    username = db.Column(db.String(100))
    password_hash = db.Column(db.String())
    emergency_contact = db.Column(db.String(80), unique=False)
 
    def set_password(self,password):
        self.password_hash = generate_password_hash(password)
     
    def check_password(self,password):
        return check_password_hash(self.password_hash,password)

#Create form class
from flask_login import LoginManager
login = LoginManager()
 
@login.user_loader
def load_user(id):
    return UserModel.query.get(int(id))

db.init_app(app)
@app.before_first_request
def create_table():
    db.create_all()
login.init_app(app)
login.login_view = 'login'

def gen_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield(b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
app.config['SECRET_KEY']='thisisfirstflaskapp'

#routing

@app.route('/')
def index():
    return render_template('homepage.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/predict')
def predict_asymmetry():
    """ Face detection section """
    # Load stroke detection model
    classifier = load_model("StrokeDetectionModel.h5")

    # Set the facial detection algorithm
    casc_path_face = "haarcascade_frontalface_default.xml"
    face_cascade = cv2.CascadeClassifier(casc_path_face)
    #data = pickle.loads(open("face_enc", "rb").read())

    # Preprocess the face
    ret, frame = camera.read()
    labels = []
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    faces = face_cascade.detectMultiScale(img,1.3,5)
    
    # Classify the picture
    class_labels = ['Normal','Asymmetrical']
    for (x,y,w,h) in faces:
        cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
        roi_color = img[y:y+h,x:x+w]
        roi_color = cv2.resize(roi_color,(100,100),interpolation=cv2.INTER_AREA)

        if np.sum([roi_color])!=0:
            roi = roi_color.astype('float')/255.0
            roi = img_to_array(roi)
            roi = np.expand_dims(roi,axis=0)

            preds = classifier.predict(roi)[0]
            label = class_labels[preds.argmax()]
            label_position = (x,y)
            cv2.putText(frame,label,label_position,cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,0),3)
            time.sleep(5)
            if "Asymmetrical" in label:
                return render_template("buttons.html")
            elif "Normal" in label:
                return render_template("normal.html")
        else:
            cv2.putText(frame,'No Face Found',(20,20),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,0),3)

@app.route('/upload')
def upload_file():
   return render_template('homepage.html')

@app.route('/resources')
def resources():
   return render_template('resources.html')
	
@app.route('/uploader', methods = ['POST'])
def upload_image():
	if 'file' not in request.files:
		flash('No file part')
		return redirect(request.url)
	file = request.files['file']
	if file.filename == '':
		flash('No image selected for uploading')
		return redirect(request.url)
	if file and allowed_file(file.filename):
		filename = secure_filename(file.filename)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		#print('upload_image filename: ' + filename)
		flash('Image successfully uploaded and displayed below')
		return render_template('upload.html', filename=filename)
	else:
		flash('Allowed image types are -> png, jpg, jpeg, gif')
		return redirect(request.url)

@app.route('/display/<filename>')
def display_image(filename):
	#print('display_image filename: ' + filename)
	return redirect(url_for('static', filename='uploads/' + filename), code=301)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
    filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

@app.route('/signup', methods = ['POST', 'GET' ] )
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        return redirect(url_for('login'))
    return render_template('signup.html', form = form)

@app.route('/logout')
def logout():
    return render_template('logout.html')

#Log in and sign up

@app.route('/login', methods = ['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect('/upload')
     
    if request.method == 'POST':
        email = request.form['email']
        user = UserModel.query.filter_by(email = email).first()
        if user is not None and user.check_password(request.form['password']):
            login_user(user)
            return redirect('/login')
     
    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect('/login')
     
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        emergency_contact = request.form['emergency_contact']
             
        user = UserModel(email=email, username=username, emergency_contact=emergency_contact)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html')


@app.route('/buttons', methods = ['POST', 'GET'])
def buttons():
    sent = ' '
    called = ' '
    if request.method == 'POST':
        exec(open("send_sms.py").read())
        sent = "Sent"
    if request.method == 'POST':
       exec(open("make_call.py").read())
       called = 'Called'
    return render_template('buttons.html')

if __name__ == "__main__":
    app.run(debug = True)

