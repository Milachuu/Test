from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_socketio import SocketIO, join_room, emit, disconnect
from otp_backup import generate_2fa_backup_codes, verify_and_consume_backup_code
from Forms import CreateUserForm,CreateUserInfo,Login,Wishlist,Reporting
import User,hashlib, pyotp, qrcode, base64, io, os, uuid, json
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from datetime import datetime, date, timedelta
from time import time
import stripe
import secrets
from validation import sanitisation
from otp_utils import (
    POINTS_PER_VOUCHER,
    user_points, update_user_points,
    upsert_otp, can_resend, get_active_otp,
    send_voucher_otp_email,
    send_voucher_success_email
)

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY") 

app = Flask(__name__)
app.config['SECRET_KEY'] = 'asdsdasd dasdasd'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")


app.config.update(
    SMTP_HOST=os.getenv("SMTP_HOST"),
    SMTP_PORT=int(os.getenv("SMTP_PORT", 465)),
    SMTP_USERNAME=os.getenv("SMTP_USERNAME"),
    SMTP_PASSWORD=os.getenv("SMTP_PASSWORD"),
    SMTP_SENDER=os.getenv("SMTP_SENDER"),
    APP_NAME=os.getenv("APP_NAME", "NeighbourlyNest"),
    OTP_TTL_MINUTES=int(os.getenv("OTP_TTL_MINUTES", 30)),
    OTP_RESEND_COOLDOWN_SECONDS=int(os.getenv("OTP_RESEND_COOLDOWN_SECONDS", 60)),
)


import Database
from db_utils import db, mycursor, init_app as init_db, ensure_schema

init_db(app)
ensure_schema()

ACTIVE_BOOKING_STATUSES = ("Pending", "Confirmed", "Approved", "Reserved")
# Listings with inactive bookings are allowed to reappear in browse results.
INACTIVE_BOOKING_STATUSES = ("Cancelled", "Expired", "Completed", "Rejected")




UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure the uploads directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


AVAILABILITY_MIN_DATE = date(2025, 2, 5)
SLOT_MINUTES = 30


def _format_time_value(time_value):
    if time_value is None:
        return ""
    if isinstance(time_value, str):
        return time_value[:5]
    return time_value.strftime("%H:%M")


def _format_time_label(time_value):
    if time_value is None:
        return ""
    time_str = _format_time_value(time_value)
    for fmt in ("%H:%M", "%H:%M:%S", "%I:%M %p", "%I:%M%p"):
        try:
            parsed = datetime.strptime(time_str, fmt)
            return parsed.strftime("%I:%M %p").lstrip("0")
        except ValueError:
            continue
    return time_str


def _parse_time_value(time_value):
    if time_value is None:
        return None
    if isinstance(time_value, time):
        return time_value
    if isinstance(time_value, str):
        return datetime.strptime(time_value[:5], "%H:%M").time()
    return time_value


def _time_to_minutes(time_value):
    parsed = _parse_time_value(time_value)
    return parsed.hour * 60 + parsed.minute


def _generate_time_slots(start_time, end_time, step_minutes=SLOT_MINUTES):
    start_minutes = _time_to_minutes(start_time)
    end_minutes = _time_to_minutes(end_time)
    slots = []
    current = start_minutes
    while current + step_minutes <= end_minutes:
        hours = current // 60
        minutes = current % 60
        slots.append(f"{hours:02d}:{minutes:02d}")
        current += step_minutes
    return slots


def _get_next_availability(listing_id):
    mycursor.execute(
        """
        SELECT availability_date, start_time, end_time
        FROM ListingAvailability
        WHERE listing_id = %s
        ORDER BY availability_date ASC, start_time ASC
        LIMIT 1
        """,
        [listing_id],
    )
    row = mycursor.fetchone()
    if not row:
        return None, None
    date_str = str(row[0])
    start_value = _format_time_value(row[1])
    end_value = _format_time_value(row[2])
    return date_str, f"{_format_time_label(start_value)} – {_format_time_label(end_value)}"


def fetch_available_listings(listing_type, viewer_email):
    query = f"""
        SELECT
            l.listing_id,
            l.listing_username,
            l.title,
            l.description,
            l.category,
            l.type,
            l.availability_date,
            l.availability_time,
            l.photo_path,
            l.listing_email
        FROM Listing AS l
        WHERE LOWER(l.type) = %s
          AND EXISTS (
            SELECT 1
            FROM ListingAvailability AS la
            WHERE la.listing_id = l.listing_id
          )
    """
    params = [
        listing_type.lower(),
    ]
    mycursor.execute(query, params)
    return mycursor.fetchall()



"""Web App Routing"""



# Before Login Homepage
@app.route('/')
def before_login():
  
    return render_template('index.html')

@app.route('/aboutUs')
def aboutUs():

    return render_template('aboutUs.html')

@app.route('/mission')
def mission():

    return render_template('mission.html')

@app.route('/feedbackb4',methods=["GET", "POST"])
def feedbackb4():
    
    recaptcha_response = request.form.get('g-recaptcha-response')

    data = {
        'secret': os.getenv('RECAPTCHA_SECRET_KEY'),  # from .env
        'response': recaptcha_response
    }
    


    if request.method == "POST":
        if not request.form.get('g-recaptcha-response'):
            flash("CAPTCHA verification failed", "error")
            return redirect(url_for('feedbackb4'))
        
        # Process form data
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        message = request.form.get('message', '').strip()
        
        # Insert to database
        Database.Create_Feedback(name, email, message)
        db.commit()
        flash("Feedback submitted!", "success")
        return redirect(url_for('before_login'))


    return render_template('feedback before.html', site_key=os.getenv('RECAPTCHA_SITE_KEY'))


@app.route('/donate', methods=["GET", "POST"])
def donate():

    if request.method == "POST":
        session["donation_amount"] = request.form.get("donation_amount")
        session["other_amount_value"] = request.form.get("other_amount_value")

        return redirect(url_for("create_checkout_session"))

    return render_template("donate.html")


@app.route("/payment", methods=["GET", "POST"])
def payment():
    
    donate_amount = session["donation_amount"]
    other_amount_value = session["other_amount_value"]

    if request.method == "POST":

        return render_template('confirmation.html')

    # Store form data in session
    session["first_name"] = request.form.get("first-name")
    session["last_name"] = request.form.get("last-name")
    session["email"] = request.form.get("email")
    session["donation_amount"] = request.form.get("donation_amount")
    session["other_amount_value"] = request.form.get("other_amount_value")

    

    print(donate_amount)
    print(other_amount_value)

    return render_template(
        'payment.html',
        donate_amount= donate_amount,
        other_amount_value=other_amount_value,
    )


# Login
@app.route('/login',methods=['GET','POST'])
def login():
    login_form = Login(request.form)

    current_time = time()

    today = str(date.today())
    print(today)

    session["get_date"] = today

    current_time_of_log = datetime.now().strftime("%H:%M:%S")
    print(current_time_of_log)
    
    # progressive_failure = session.get("progress_fail")

    if "Failed_login" in session:
        Failed_login = session["Failed_login"]
    
    # Rate Limiting time
    else:
        session["Failed_login"] = 0
    

    lock_until = session.get("lock_until")

    if lock_until and current_time < lock_until:
        remaining_time = int(lock_until - current_time)
        message2 = f"Your account is temporarily locked. Try again in {remaining_time} seconds."
        return render_template('login.html', form=login_form, message="", message2=message2)


     
    if request.method == "POST" and login_form.validate():




        Failed_login = session["Failed_login"]


        email = login_form.email.data
        password = login_form.password.data




        mycursor.execute("Select ps.email, ps.password,ps.salt from Password_Storage As ps Inner Join User As u On ps.email = u.login_email  Where ps.email = %s AND u.role = 'Normal'",[email])

        find_email = mycursor.fetchone()


        if find_email:
            
            retrieve_email = find_email[0]
            stored_password = find_email[1]
            stored_salt = find_email[2]

            # salting the password
            password_salt = password + stored_salt            
            # hash the password input by the user during login
            hash = hashlib.new("SHA256")
            hash.update(password_salt.encode())
            login_password = hash.hexdigest()

            print(email)
            print(login_password)

            print("Normal user role")
        
            if login_password != stored_password:
                message2 = "The email or password you entered is incorrect"


                Failed_login = Failed_login + 1

                session["Failed_login"] = Failed_login

                print("Counter of failed login: {}".format(Failed_login))

                if Failed_login >= 3:
                    session["lock_until"] = current_time + ( Failed_login * 120 )

                    message2 = "Your account has temporary been locked."
                    
                    # Log Monitoring
                    status = "Failed"
                    Database.Create_Log(email,Failed_login,today,current_time_of_log,status)
                    db.commit()

                    return render_template('login.html',form=login_form,message ="",message2 = message2)

                return render_template('login.html',form=login_form,message ="",message2 = message2)
            
            else:

                session["user_email"] = email

                mycursor.execute("Select username from User Where login_email = %s",[email])

                get_username = mycursor.fetchone()[0]

                if get_username != "Block":

                    session["username"] = get_username  
                    session["role"] = "Normal"

                    # Log Monitoring
                    status = "Success"
                    Database.Create_Log(email,Failed_login,today,current_time_of_log,status)
                    db.commit()

                    session.pop("Failed_login",None)
                    session.pop("lock_until",None)

                    return redirect(url_for('verify_otp',action="Login"))
                
                else:
                    message = "🚫 Your account is temporarily suspended. Please contact support for assistance."
                    return render_template('login.html',form=login_form,message = message,message2="")
            
        elif not find_email:

            mycursor.execute("Select ps.email, ps.password,ps.salt from Password_Storage As ps Inner Join User As u On ps.email = u.login_email  Where ps.email = %s AND u.role = 'Admin'",[email])


            find_admin = mycursor.fetchone()
            if find_admin:
          

                print("Normal Admin role")
                retrieve_admin_email = find_admin[0]
                stored_password = find_admin[1]
                stored_salt = find_admin[2]

                 # salting the password
                password_salt = password + stored_salt            
                # hash the password input by the user during login
                hash = hashlib.new("SHA256")
                hash.update(password_salt.encode())
                login_password = hash.hexdigest()


                print(email)
                print(login_password)

                if login_password != stored_password:
                    message2 = "The email or password you entered is incorrect"
      
                    Failed_login = Failed_login + 1

                    session["Failed_login"] = Failed_login

                    print("Counter of failed login: {}".format(Failed_login))

                    if Failed_login >= 3:
                        session["lock_until"] = current_time + ( Failed_login * 120 )

                        message2 = "Your account has temporary been locked."
                    
                        # Log Monitoring
                        status = "Failed"
                        Database.Create_Log(email,Failed_login,today,current_time_of_log,status)
                        db.commit()

                        return render_template('login.html',form=login_form,message ="",message2 = message2)



                    return render_template('login.html',form=login_form,message ="",message2 = message2)
                




                else:
                    session["user_email"] = email

                    session["role"] = "Admin"
                    mycursor.execute("Select username from User Where login_email = %s",[email])

                    get_username = mycursor.fetchone()
                    session["username"] = get_username[0]

                    # Log
                    status = "Success"
                    Database.Create_Log(email,Failed_login,today,current_time_of_log,status)
                    db.commit()

                    session.pop("Failed_login",None)
                    session.pop("lock_until",None)
                    


                    return redirect(url_for('verify_otp'))
                
            else:

                message2 = "The email or password you entered is incorrect"

                Failed_login = Failed_login + 1

                session["Failed_login"] = Failed_login

                print("Counter of failed login: {}".format(Failed_login))


                if Failed_login >= 3:
                    session["lock_until"] = current_time + ( Failed_login * 120 )

                    message2 = "Your account has temporary been locked."
                    return render_template('login.html',form=login_form,message ="",message2 = message2)

                
                return render_template('login.html',form=login_form,message ="",message2 = message2)
        else:

           
            message2 = "The email or password you entered is incorrect"

            Failed_login = Failed_login + 1

            session["Failed_login"] = Failed_login

            print("Counter of failed login: {}".format(Failed_login))


            if Failed_login >= 3:
                    session["lock_until"] = current_time + ( Failed_login * 120 )

                    message2 = "Your account has temporary been locked."
                    return render_template('login.html',form=login_form,message ="",message2 = message2)


            return render_template('login.html',form=login_form,message ="",message2 = message2)

    return render_template('login.html',form=login_form,message2="")


# Sign Up 
@app.route('/sign_up', methods=['GET', 'POST']) 
def sign_up():

    # Change this since it is in wtform



    create_user_form = CreateUserForm(request.form) 
    
      

    if request.method == 'POST' and create_user_form.validate(): 
        
        email = create_user_form.email.data
        mycursor.execute("Select * from User Where login_email = %s ",[email])

        check_email = mycursor.fetchone()

        if check_email:
            message = "Email has been taken."
            return render_template('sign_up.html', form=create_user_form,message=message)


      


        password = create_user_form.password1.data

        check_password = create_user_form.password2.data

        if password != check_password:
            message="Passwords does not match"
            return render_template('sign_up.html', form=create_user_form,message=message)

        # salting the password
        secret_salt = secrets.token_hex(16)
        print(f"hash: {secret_salt}")
        password = password + secret_salt
        
        # hashing the password to store it in db

        hash = hashlib.new("SHA256")
        
        hash.update(password.encode())
        password_hash = hash.hexdigest()
        print(password_hash)

        # end of hashing

        session["user_email"] = email
        
        user_id = str(uuid.uuid4())
        print("UUID Here")
        print(user_id)
        
        
        
        first_name = sanitisation(create_user_form.first_name.data)
        last_name = sanitisation(create_user_form.last_name.data)
        
        user = User.User( user_id,first_name, last_name,create_user_form.email.data ,password_hash,password_hash) 
        session["user_email"] = email
        Database.Create_User(user.get_user_id(),user.get_first_name(),user.get_last_name(),user.get_email())

        Database.Create_Password(user.get_email(), password_hash,secret_salt)

        # log monitoring for New User

        today = str(date.today())
        print(today)

        session["get_date"] = today

        current_time_of_log = datetime.now().strftime("%H:%M:%S")
        print(current_time_of_log)

        status = "New"

        
        
        Database.Create_Log(email,0,today,current_time_of_log,status)
        db.commit()

        return redirect(url_for('user_info')) 
    return render_template('sign_up.html', form=create_user_form,message="") 










# User Info 
@app.route('/user_info', methods=['GET', 'POST']) 
def user_info(): 

    if "user_email" not in session:
        return redirect(url_for('before_login'))  
    
    
      
# username, postal code, email ,phone


    # Change this since it is in wtform
    create_user_info_form = CreateUserInfo(request.form) 


    if request.method == 'POST' and create_user_info_form.validate(): 

        username = create_user_info_form.username.data

        mycursor.execute("Select username From User Where username = %s",[username])
        check_username = mycursor.fetchall()

        if not check_username:
            print(create_user_info_form.username.data)
            session["username"] = sanitisation(create_user_info_form.username.data) 


            
            postal_code = create_user_info_form.postal_code.data
            print(postal_code)

            try:
                postal_code = int(postal_code)
            
        
            except ValueError:
                message1 = "This is not a valid postal code"
                return render_template('user_info.html', form=create_user_info_form,message1=message1,message = "",message_username="",message_email="")
        
            
            mailing_email = create_user_info_form.email.data

            mycursor.execute("Select email From User Where email = %s",[mailing_email])
            check_mailing_email = mycursor.fetchall()

            if not check_mailing_email:

                telephone = create_user_info_form.phone_number.data
                print(telephone)
                try:
                    phone_num = int(telephone)
                except ValueError:
                    message = "This is not a valid number"
                    return render_template('user_info.html', form=create_user_info_form,message=message,message_username="",message_email="")
        
        

                if len(telephone) != 8:
                    message = "This is not a valid number"
                    return render_template('user_info.html', form=create_user_info_form,message=message,message_username="",message_email="")
        
                if telephone.startswith('8') or telephone.startswith('9'):

                    mycursor.execute("Select phone_num From User Where phone_num = %s",[telephone])
                    check_telephone = mycursor.fetchall()

                    if not check_telephone:

                        if "user_email" in session:
                            get_email = session["user_email"]
                                    
                        # validate input
                        username = sanitisation(username)
                        bio = create_user_info_form.bio.data
                        bio = sanitisation(bio)
                        Database.Create_User_p2(username,create_user_info_form.gender.data,create_user_info_form.postal_code.data,create_user_info_form.email.data,create_user_info_form.phone_number.data,bio,0, get_email)

      
                        return redirect(url_for('totp_setup')) 

                    
                    else:
                        message = "This phone number has been taken, please try a different one."
                        return render_template('user_info.html', form=create_user_info_form,message=message,message_username = "",message_email="")

                
                else:
                    message = "This is not a valid number"
                    return render_template('user_info.html', form=create_user_info_form,message=message,message_username ="",message_email="")
    

            



            else:
                message_email = "Email has been taken."
                return render_template('user_info.html', form=create_user_info_form,message="",message_username = "",message_email=message_email)
                        



        else:


            message_username = "This username has been taken, please try a different one."
            return render_template('user_info.html', form=create_user_info_form,message="",message_username = message_username,message_email="")
            





    return render_template('user_info.html', form=create_user_info_form,message ="",message_username = "",message_email="") 

@app.route('/2fa_setup', methods=['GET', 'POST'])
def totp_setup():
    if "user_email" not in session:
        return redirect(url_for('before_login'))

    get_email = session["user_email"]
    get_username = session.get("username", "User")

    mycursor.execute("SELECT totp FROM Password_Storage WHERE email = %s", [get_email])
    
    row = mycursor.fetchone()

    if row and row[0]:
        totp_secret = decrypt_secret(row[0])
        try:
            totp_secret = decrypt_secret(row[0])
        except Exception:
            return redirect(url_for('before_login'))
    else:
        totp_secret = pyotp.random_base32()
        enc = encrypt_secret(totp_secret)
        Database.Create_Password_p2(enc, get_email)
        db.commit()

    session["totp_secret"] = totp_secret

    provisioning_uri = pyotp.TOTP(totp_secret).provisioning_uri(
        name="NeighbourlyNest",
        issuer_name=get_email
    )

    qr = qrcode.QRCode(version=1, box_size=4, border=5)
    qr.add_data(provisioning_uri)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    qr_code_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

    # --- NEW: prepare backup codes (only first-time show) ---
    # If user has no UNUSED codes yet, generate a fresh set and show them once.
    mycursor.execute(
        "SELECT COUNT(*) FROM twofa_backup_codes WHERE user_email = %s AND used_at IS NULL",
        (get_email,)
    )
    count_unused = mycursor.fetchone()[0]
    backup_codes_to_show = None
    if count_unused == 0:
        # First-time generation; return plaintext list to display ONCE
        backup_codes_to_show = generate_2fa_backup_codes(get_email, count=10, length=10)
        # NOTE: We do not store plaintext anywhere else. Only pass to template once.

    if request.method == "POST":
        user_otp = request.form.get('codeInput')
        totp = pyotp.TOTP(totp_secret)

        if totp.verify(user_otp):
            session["verify"] = "Valid"
            
            # Set Default values for preference
            Database.Create_Preferences(get_email)
            
            return redirect(url_for('login_home'))
        else:
            flash("Invalid OTP. Please try again.", "error")
            return redirect(url_for('totp_setup'))

    return render_template(
        "2fa_setup.html",
        qr_code_base64=qr_code_base64,
        totp_secret=totp_secret,
        backup_codes=backup_codes_to_show  # NEW: pass to template
    )


   


# Forget Password 
@app.route('/update_user',methods =["GET","POST"])
def update_user():

 
  

    
    

    update_user_form = Login(request.form)
    if request.method == "POST" and update_user_form.validate():

      
        email = update_user_form.email.data
        mycursor.execute("SELECT email,salt From Password_Storage Where email = %s ",[email])

        check_email = mycursor.fetchone()
        print(check_email)

        if check_email:

    

            new_password = update_user_form.password.data

            stored_salt = check_email[1]

            # salting the password
            password_salt = new_password + stored_salt     

        # hashing the password to store it in db


            hash = hashlib.new("SHA256")

            hash.update(password_salt.encode())
            password_hash = hash.hexdigest()
            print(password_hash)

        # end of hashing

    

     
            session["user_email"] = email
            session["new_password"] = password_hash
        

            return redirect(url_for('verify_otp'))


        message1 = "If an account with that email exists, a reset link has been sent"
        return render_template('update_user.html',form = update_user_form,message1=message1)



        

    return render_template('update_user.html',form = update_user_form,message1="")


# Login Verify 6 Pin OTP

@app.route('/verify-otp', methods=["GET", "POST"])
def verify_otp():
    if "user_email" not in session:
        return redirect(url_for('before_login'))

    # initialize / read rate-limit counters
    if "Failed_login" in session:
        Failed_login = session["Failed_login"]
    else:
        session["Failed_login"] = 0
        Failed_login = 0

    current_time = time()
    otp_lock_until = session.get("otp_lock_until")

    if otp_lock_until and current_time < otp_lock_until:
        remaining_time = int(otp_lock_until - current_time)
        message = f"Your account is temporarily locked. Try again in {remaining_time} seconds."
        return render_template("verify_2fa.html", message=message)

    get_email = session.get("user_email")
    get_password = session.get("new_password")

    lang_code = get_user_lang_code()     
    t = make_t(lang_code) 

    if not get_email:
        return redirect(url_for("login"))

    mycursor.execute("SELECT totp FROM Password_Storage WHERE email = %s", [get_email])
    result = mycursor.fetchone()
    if not result:
        return redirect(url_for("login"))
    
    try:
        totp_secret = decrypt_secret(result[0])   # decrypt for use
    except Exception:
        return render_template("verify_2fa.html")

    if request.method == "POST":
        action = request.form.get("action", "otp")  # "otp" (default) or "backup"

        # ----- Method 1: 6-digit TOTP from authenticator app -----
        if action == "otp":
            user_otp = request.form.get("otpInput", "").strip()
            totp = pyotp.TOTP(totp_secret)

            if totp.verify(user_otp):
                # Password reset flow
                if get_password:
                    Database.Update_Password(get_password, get_email)
                    db.commit()
                    session.pop("new_password", None)
                    session.clear()
                    return redirect(url_for("logout"))

                # success path (normal/admin)
                session.pop("Failed_login", None)
                session.pop("otp_lock_until", None)
                session["verify"] = "Valid"

                role = session.get("role", "Normal")
                if role == "Admin":
                    return redirect(url_for("login_home"))
                return redirect(url_for("login_home"))

            # failed TOTP -> increment & maybe lock
            Failed_login += 1
            session["Failed_login"] = Failed_login
            if Failed_login >= 3:
                session["otp_lock_until"] = current_time + (Failed_login * 120)
                return render_template("verify_2fa.html", message="Your account has temporary been locked.", t=t)
            return render_template("verify_2fa.html", message="Invalid OTP. Please try again.", t=t)

        # ----- Method 2: Backup Recovery Code (single-use) -----
        elif action == "backup":
            backup_code = request.form.get("backup_code", "").strip().upper()
            # Verify & consume (marks used_at so it cannot be reused)
            if backup_code and verify_and_consume_backup_code(get_email, backup_code):
                # Password reset flow
                if get_password:
                    Database.Update_Password(get_password, get_email)
                    db.commit()
                    session.pop("new_password", None)
                    session.clear()
                    return redirect(url_for("logout"))

                # success path (normal/admin)
                session.pop("Failed_login", None)
                session.pop("otp_lock_until", None)
                session["verify"] = "Valid"

                role = session.get("role", "Normal")
                if role == "Admin":
                    return redirect(url_for("login_home"))
                return redirect(url_for("login_home"))

            # failed backup -> increment & maybe lock
            Failed_login += 1
            session["Failed_login"] = Failed_login
            if Failed_login >= 3:
                session["otp_lock_until"] = current_time + (Failed_login * 120)
                return render_template("verify_2fa.html", message="Your account has temporary been locked.", t=t)
            return render_template("verify_2fa.html", message="Invalid backup code. Please try again.", t=t)

    return render_template("verify_2fa.html", message="", t=t)




@app.route('/search', methods=['GET'])
def search():
    if "user_email" not in session:
        return redirect(url_for('before_login'))  
    
    if "verify" not in session:
        return redirect(url_for('before_login'))

    query = request.args.get('query')
    return f"Search results for: {query}"


def validate_input(data, field, max_length=255):
    if "user_email" not in session:
        return redirect(url_for('before_login'))  
    
    if "verify" not in session:
        return redirect(url_for('before_login'))
    
    if not data or len(data) > max_length:
        return f"Invalid input for {field}. Ensure it's filled and does not exceed {max_length} characters."
    return None





# Create Listing
@app.route('/create_listing', methods=['GET', 'POST'])
def create_listing():
    if "user_email" not in session:
        return redirect(url_for('before_login'))  

    if "verify" not in session:
        return redirect(url_for('before_login'))
     

    get_email = session["user_email"]
    get_username = session["username"]

    lang_code = get_user_lang_code()     
    t = make_t(lang_code)


    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        listing_type = request.form.get('type')
        availability_payload = request.form.get('availability_payload')

        errors = []
        for field, value in {'Title': title, 'Description': description, 'Category': category, 'Type': listing_type}.items():
            error = validate_input(value, field)
            if error:
                errors.append(error)

        availability_blocks = []
        if availability_payload:
            try:
                availability_blocks = json.loads(availability_payload)
            except json.JSONDecodeError:
                errors.append(t("create_newlisting.availability_block_required"))

        if not isinstance(availability_blocks, list):
            availability_blocks = []
            errors.append(t("create_newlisting.availability_block_required"))

        if not availability_blocks:
            errors.append(t("create_newlisting.availability_block_required"))

        availability_rows = []
        for block in availability_blocks:
            block_date = (block or {}).get("date")
            slots = (block or {}).get("slots") or []
            if not block_date:
                errors.append(t("create_newlisting.availability_date_required"))
                continue
            try:
                parsed_date = datetime.strptime(block_date, "%Y-%m-%d").date()
                if parsed_date < AVAILABILITY_MIN_DATE:
                    errors.append(t("create_newlisting.date_error"))
            except ValueError:
                errors.append(t("create_newlisting.availability_date_required"))
                continue

            if not slots:
                errors.append(t("create_newlisting.availability_slot_required"))
                continue

            parsed_slots = []
            for slot in slots:
                start_time = slot.get("start")
                end_time = slot.get("end")
                if not start_time or not end_time:
                    errors.append(t("create_newlisting.availability_slot_incomplete"))
                    continue
                try:
                    parsed_start = datetime.strptime(start_time, "%H:%M").time()
                    parsed_end = datetime.strptime(end_time, "%H:%M").time()
                except ValueError:
                    errors.append(t("create_newlisting.availability_slot_incomplete"))
                    continue
                if parsed_start >= parsed_end:
                    errors.append(t("create_newlisting.availability_slot_invalid"))
                    continue
                if (_time_to_minutes(parsed_end) - _time_to_minutes(parsed_start)) < SLOT_MINUTES:
                    errors.append(t("create_newlisting.availability_slot_duration"))
                    continue
                parsed_slots.append({"start": parsed_start, "end": parsed_end})

            parsed_slots.sort(key=lambda slot: slot["start"])
            previous_end = None
            for slot in parsed_slots:
                if previous_end and slot["start"] < previous_end:
                    errors.append(t("create_newlisting.availability_slot_overlap"))
                    break
                previous_end = slot["end"]

            for slot in parsed_slots:
                availability_rows.append(
                    {
                        "date": block_date,
                        "start": slot["start"],
                        "end": slot["end"],
                    }
                )

        if errors:
            display_blocks = availability_blocks or [{"date": "", "slots": [{"start": "", "end": ""}]}]
            return render_template(
                'new_listing.html',
                errors=errors,
                username=get_username,
                availability_blocks=display_blocks,
                t=t,
            )

        # File Upload Validation
        photo = request.files.get('photo')
        photo_path = None
        if photo and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            photo_path = f"uploads/{filename}"
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))


         # validate input
        title = sanitisation(title)
        description = sanitisation(description)

        # Changes are made here, Insert details into db
        try:
            listing_id = Database.Create_Listing(
                get_username,
                title,
                description,
                category,
                listing_type,
                None,
                None,
                photo_path,
                get_email,
                commit=False,
            )
            Database.Create_Listing_Availability(
                listing_id,
                get_email,
                availability_rows,
                commit=False,
            )
            db.commit()
        except Exception:
            db.rollback()
            errors.append(t("create_newlisting.availability_save_error"))
            display_blocks = availability_blocks or [{"date": "", "slots": [{"start": "", "end": ""}]}]
            return render_template(
                'new_listing.html',
                errors=errors,
                username=get_username,
                availability_blocks=display_blocks,
                t=t,
            )

       
        return redirect(url_for('login_home'))

    

    return render_template(
        'new_listing.html',
        username=get_username,
        availability_blocks=[{"date": "", "slots": [{"start": "", "end": ""}]}],
        t=t,
    )



# Update Listing
@app.route('/update_listing/<int:listing_id>', methods=['GET', 'POST'])
def update_listing(listing_id):
    if "user_email" not in session:
        return redirect(url_for('before_login'))  

    if "verify" not in session:
        return redirect(url_for('before_login'))



    print(listing_id)


    
    
     

    get_email = session["user_email"]

    mycursor.execute("Select listing_email from Listing where listing_id = %s",[listing_id])

    check_list_email = mycursor.fetchone()

    if get_email != check_list_email[0]:

        # if they try to broken access control someone else's listing, deny their action
        return redirect(url_for('login_home'))

        
    
    get_username = session["username"]

    lang_code = get_user_lang_code()     
    t = make_t(lang_code)




    mycursor.execute("Select * from Listing where listing_id = %s ",[listing_id])

    check_listing = mycursor.fetchone()


    if not check_listing:

        return "Listing not found!",404


 

    if request.method == "POST":

        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        listing_type = request.form.get('type')
        availability_date = request.form.get('availability_date')
        availability_time = request.form.get('availability_time')

        
        # Handle new photo upload
        photo = request.files.get('photo')
        if photo and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            photo_path = f"uploads/{filename}"  # Store only relative path
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
        # validate input
        title = sanitisation(title)
        description = sanitisation(description)

        Database.Update_Listing(title,description,category,listing_type,availability_date,availability_time,photo_path,get_email,listing_id)
        db.commit()

        return redirect(url_for('login_home'))


    mycursor.execute("Select * from Listing where listing_id = %s  ",[listing_id])

    listing = mycursor.fetchone()


    return render_template('update_listing.html', listing=listing, listing_id=listing_id,username=get_username, t=t)


# Delete Listing
@app.route('/delete_listing/<int:listing_id>', methods=['POST'])
def delete_listing(listing_id):
    if "user_email" not in session:
        return redirect(url_for('before_login'))  


    if "verify" not in session:
        return redirect(url_for('before_login'))

    get_email = session["user_email"]
    get_username = session["username"]

    print(listing_id)

    Database.Delete_Listing(get_email,listing_id)
    db.commit()

    return redirect(url_for('login_home'))


@app.route('/login_home')
def login_home():
    if "user_email" not in session:
        return redirect(url_for('before_login'))  


    if "verify" not in session:
        return redirect(url_for('before_login'))

    get_email = session["user_email"]
    get_username = session["username"]

    lang_code = get_user_lang_code()     
    t = make_t(lang_code)                 


    borrow_listings = fetch_available_listings("borrow", get_email)
    free_listings = fetch_available_listings("free", get_email)

    mycursor.execute("Select wishlist_listing_id From Wishlist Where wishlist_email =%s",[get_email] )
    favourited_rows = mycursor.fetchall()
    favourited_listings = [row[0] for row in favourited_rows]
    print(favourited_listings)
    
    

    return render_template(
        'login_home.html',
        borrow_listings=borrow_listings,
        free_listings=free_listings,
        favourited_listings=favourited_listings,
        username=get_username,
        email=get_email,
        CHATGPT_SECRET_KEY= os.getenv("CHATGPT_SECRET_KEY"),
        t=t
    )




""" Favourite Handling"""

def Update_Wishlist(listing_id,action,login_email):
    if "user_email" not in session:
        return redirect(url_for('before_login'))  
    
    if "verify" not in session:
        return redirect(url_for('before_login'))
    
    if action == "add":

        Database.Create_Wishlist(login_email,listing_id)
    
    elif action == "remove":
        mycursor.execute("SELECT * FROM Wishlist WHERE wishlist_email = %s AND wishlist_listing_id = %s ", (login_email,listing_id))

        result = mycursor.fetchone()

        if result:
            print("Found: {}".format(result))

            mycursor.execute("DELETE FROM Wishlist WHERE wishlist_email = %s AND wishlist_listing_id = %s ", (login_email,listing_id))
            db.commit()


@app.route("/favorite/<int:listing_id>", methods=["POST"])
def favorite_item(listing_id):
    if "user_email" not in session:
        return redirect(url_for('before_login'))  
    
    if "verify" not in session:
        return redirect(url_for('before_login'))

    """ Handle AJAX requests for favoriting/unfavoriting items """
    print(f"Received request for listing ID: {listing_id}")   # Debugging log
    action = request.json.get("action")
    print(f"Action: {action}")  # Debugging log

    if action not in ["add", "remove"]:
        return jsonify({"error": "Invalid action"}), 400



    # Retrieve logged-in user's details

    get_email = session["user_email"]


    Update_Wishlist(listing_id, action, get_email)
    db.commit()
    return jsonify({"success": True})


def ensure_chat_for_booking(listing_id, borrower_email, giver_email, listing_title, selected_date, selected_time):
    mycursor.execute(
        "SELECT chat_id FROM Chat WHERE listing_id = %s AND borrower_email = %s AND giver_email = %s",
        (listing_id, borrower_email, giver_email),
    )
    row = mycursor.fetchone()
    if row:
        chat_id = row[0]
    else:
        mycursor.execute(
            "INSERT INTO Chat (listing_id, borrower_email, giver_email) VALUES (%s,%s,%s)",
            (listing_id, borrower_email, giver_email),
        )
        db.commit()
        chat_id = mycursor.lastrowid

    system_message = (
        f"Booking created for {listing_title} on {selected_date} at {selected_time}."
    )
    mycursor.execute(
        "INSERT INTO ChatMessage (chat_id, sender_email, message_text, message_type) VALUES (%s,%s,%s,%s)",
        (chat_id, None, system_message, "system"),
    )
    db.commit()
    _emit_chat_message(
        chat_id,
        {
            "chat_id": chat_id,
            "message_id": mycursor.lastrowid,
            "sender_email": None,
            "message_text": system_message,
            "message_type": "system",
        },
    )
    return chat_id


def fetch_user_chats(user_email):
    mycursor.execute(
        """
        SELECT
            c.chat_id,
            c.listing_id,
            c.borrower_email,
            c.giver_email,
            l.title,
            l.photo_path,
            l.category,
            l.type,
            borrower.username,
            giver.username,
            (
                SELECT m.message_text
                FROM ChatMessage m
                WHERE m.chat_id = c.chat_id
                ORDER BY m.created_at DESC, m.message_id DESC
                LIMIT 1
            ) AS last_message
        FROM Chat c
        JOIN Listing l ON l.listing_id = c.listing_id
        JOIN User borrower ON borrower.login_email = c.borrower_email
        JOIN User giver ON giver.login_email = c.giver_email
        WHERE c.borrower_email = %s OR c.giver_email = %s
        ORDER BY c.created_at DESC
        """,
        (user_email, user_email),
    )
    rows = mycursor.fetchall()
    chats = []
    for row in rows:
        other_username = row[9] if user_email == row[2] else row[8]
        chats.append(
            {
                "chat_id": row[0],
                "listing_id": row[1],
                "borrower_email": row[2],
                "giver_email": row[3],
                "listing_title": row[4],
                "listing_photo": row[5] or "uploads/placeholder.png",
                "listing_category": row[6],
                "listing_type": row[7],
                "other_username": other_username,
                "last_message": row[10],
            }
        )
    return chats


def fetch_chat_details(chat_id, user_email):
    mycursor.execute(
        """
        SELECT
            c.chat_id,
            c.listing_id,
            c.borrower_email,
            c.giver_email,
            l.title,
            l.description,
            l.category,
            l.type,
            l.photo_path,
            borrower.username,
            giver.username
        FROM Chat c
        JOIN Listing l ON l.listing_id = c.listing_id
        JOIN User borrower ON borrower.login_email = c.borrower_email
        JOIN User giver ON giver.login_email = c.giver_email
        WHERE c.chat_id = %s
        """,
        (chat_id,),
    )
    row = mycursor.fetchone()
    if not row:
        return None

    borrower_email = row[2]
    giver_email = row[3]
    if user_email not in (borrower_email, giver_email):
        return None

    availability_date, availability_time = _get_next_availability(row[1])
    other_username = row[10] if user_email == borrower_email else row[9]
    return {
        "chat_id": row[0],
        "listing_id": row[1],
        "borrower_email": borrower_email,
        "giver_email": giver_email,
        "listing_title": row[4],
        "listing_description": row[5],
        "listing_category": row[6],
        "listing_type": row[7],
        "listing_photo": row[8] or "uploads/placeholder.png",
        "availability_date": availability_date,
        "availability_time": availability_time,
        "other_username": other_username,
    }


def fetch_chat_messages(chat_id):
    mycursor.execute(
        """
        SELECT message_id, sender_email, message_text, message_type, created_at
        FROM ChatMessage
        WHERE chat_id = %s
        ORDER BY created_at ASC, message_id ASC
        """,
        (chat_id,),
    )
    rows = mycursor.fetchall()
    messages = []
    for row in rows:
        messages.append(
            {
                "message_id": row[0],
                "sender_email": row[1],
                "message_text": row[2],
                "message_type": row[3],
                "created_at": row[4],
            }
        )
    return messages


def _get_authenticated_email():
    if "user_email" not in session:
        return None
    if "verify" not in session:
        return None
    return session.get("user_email")


def _chat_room(chat_id):
    return f"chat_{chat_id}"


def _emit_chat_message(chat_id, payload):
    socketio.emit("chat_message", payload, room=_chat_room(chat_id))


@socketio.on("connect")
def handle_socket_connect():
    if not _get_authenticated_email():
        return False


@socketio.on("join_thread")
def handle_join_thread(data):
    email = _get_authenticated_email()
    if not email:
        emit("socket_error", {"message": "Not authenticated."})
        disconnect()
        return

    chat_id = data.get("chat_id") if isinstance(data, dict) else None
    try:
        chat_id = int(chat_id)
    except (TypeError, ValueError):
        emit("socket_error", {"message": "Invalid chat thread."})
        return

    if not fetch_chat_details(chat_id, email):
        emit("socket_error", {"message": "Not authorized for this chat thread."})
        return

    join_room(_chat_room(chat_id))
    emit("joined_thread", {"chat_id": chat_id})


@socketio.on("send_message")
def handle_send_message(data):
    email = _get_authenticated_email()
    if not email:
        return {"ok": False, "message": "Not authenticated."}

    if not isinstance(data, dict):
        return {"ok": False, "message": "Invalid payload."}

    chat_id = data.get("chat_id")
    message_text = (data.get("message") or "").strip()
    try:
        chat_id = int(chat_id)
    except (TypeError, ValueError):
        return {"ok": False, "message": "Invalid chat thread."}

    if not message_text:
        return {"ok": False, "message": "Message cannot be empty."}

    if not fetch_chat_details(chat_id, email):
        return {"ok": False, "message": "Not authorized for this chat thread."}

    mycursor.execute(
        "INSERT INTO ChatMessage (chat_id, sender_email, message_text, message_type) VALUES (%s,%s,%s,%s)",
        (chat_id, email, message_text, "user"),
    )
    db.commit()

    payload = {
        "chat_id": chat_id,
        "message_id": mycursor.lastrowid,
        "sender_email": email,
        "message_text": message_text,
        "message_type": "user",
    }
    _emit_chat_message(chat_id, payload)
    return {"ok": True, "message_id": mycursor.lastrowid}


@app.route('/booking/<int:listing_id>', methods=['GET', 'POST'])
def booking(listing_id):
    if "user_email" not in session:
        return redirect(url_for('before_login'))  

    if "verify" not in session:
        return redirect(url_for('before_login'))
    
    get_email = session["user_email"]
    get_username = session["username"]

    today = date.today()


    




    if "booking_limit" in session:

        booking_limit = session["booking_limit"]
    
    else:
        session["booking_limit"] = 1


    # Fetch listing details
    mycursor.execute("SELECT listing_id, listing_username, title, description, category, type, availability_date, availability_time, photo_path, listing_email FROM Listing WHERE listing_id = %s", [listing_id])
    listings = mycursor.fetchone()

    if not listings:
        return "Listing not found", 404

    owner_email = listings[9]
    mycursor.execute(
        """
        SELECT availability_date, start_time, end_time
        FROM ListingAvailability
        WHERE listing_id = %s AND owner_email = %s
        ORDER BY availability_date ASC, start_time ASC
        """,
        [listing_id, owner_email],
    )
    availability_rows = mycursor.fetchall()

    availability_by_date = {}
    for availability_date, start_time, end_time in availability_rows:
        if not availability_date or not start_time or not end_time:
            continue
        date_str = str(availability_date)
        for slot in _generate_time_slots(start_time, end_time):
            availability_by_date.setdefault(date_str, set()).add(slot)

    for date_key, time_slots in list(availability_by_date.items()):
        sorted_slots = sorted(time_slots)
        availability_by_date[date_key] = [
            {"value": slot, "label": _format_time_label(slot)} for slot in sorted_slots
        ]

    status_placeholders = ", ".join(["%s"] * len(ACTIVE_BOOKING_STATUSES))
    mycursor.execute(
        f"""
            SELECT booking_email, selected_date, selected_time
            FROM Booking
            WHERE book_listing_id = %s
              AND status IN ({status_placeholders})
        """,
        [listing_id, *ACTIVE_BOOKING_STATUSES],
    )
    active_bookings = mycursor.fetchall()
    booked_slots = {
        (str(selected_date), str(selected_time))
        for _, selected_date, selected_time in active_bookings
        if selected_date and selected_time
    }
    if booked_slots:
        for date_key, time_slots in list(availability_by_date.items()):
            remaining_slots = [
                slot
                for slot in time_slots
                if (date_key, slot["value"]) not in booked_slots
            ]
            if remaining_slots:
                availability_by_date[date_key] = remaining_slots
            else:
                availability_by_date.pop(date_key, None)

   
    # row = mycursor.fetchone()

    # if not row:
    #     return "Listing not found", 404

    # listings = {
    #     "id": row[0],
    #     "username": row[1],
    #     "title": row[2],
    #     "description": row[3],
    #     "category": row[4],
    #      "type": row[5]
    #     "availability_date": row[5],
    #     "availability_time": row[6],
    #     "photo": row[7] if row[7] else 'uploads/placeholder.png'
    # }

    lang_code = get_user_lang_code()     
    t = make_t(lang_code)

    # Setting a limit for the amount of booking a user can make
    booking_lock_until = session.get("booking_lock_until")


    print(booking_lock_until)

    if booking_lock_until and str(today) < booking_lock_until:

        message = f"You have reached the maximum booking for today."
        return render_template(
            'booking.html',
            listings=listings,
            username=get_username,
            message=message,
            availability_by_date=availability_by_date,
            t=t,
        )



    if request.method == 'POST':
        selected_date = request.form.get('selectedDate')
        selected_time = request.form.get('selectedTime')

        if selected_date and selected_time:
            mycursor.execute(
                f"""
                    SELECT 1
                    FROM Booking
                    WHERE book_listing_id = %s
                      AND status IN ({status_placeholders})
                      AND selected_date = %s
                      AND selected_time = %s
                    LIMIT 1
                """,
                [listing_id, *ACTIVE_BOOKING_STATUSES, selected_date, selected_time],
            )
            if mycursor.fetchone():
                message = "Selected time is no longer available."
                return render_template(
                    'booking.html',
                    listings=listings,
                    username=get_username,
                    message=message,
                    availability_by_date=availability_by_date,
                    t=t,
                )

            available_times = [slot["value"] for slot in availability_by_date.get(selected_date, [])]
            if selected_time not in available_times:
                message = "Selected time is no longer available."
                return render_template(
                    'booking.html',
                    listings=listings,
                    username=get_username,
                    message=message,
                    availability_by_date=availability_by_date,
                    t=t,
                )

      
            booking_limit = session["booking_limit"]

            session["booking_limit"] = booking_limit + 1

            print(booking_limit)

            if booking_limit >= 3:

                tomorrow = today + timedelta(days=1)

                print(tomorrow)
                session["booking_lock_until"] = tomorrow
                session["booking_limit"] = 0
            
            
            print(selected_date)
            print(selected_time)

            Database.Create_Booking(get_email, listings[0], selected_date, selected_time, "Pending")
            db.commit()

            giver_email = listings[9]
            if giver_email:
                chat_id = ensure_chat_for_booking(
                    listing_id=listings[0],
                    borrower_email=get_email,
                    giver_email=giver_email,
                    listing_title=listings[2],
                    selected_date=selected_date,
                    selected_time=selected_time,
                )
                db.commit()

            mycursor.execute("Select points From User Where username = %s",[listings[1]])
            get_point = mycursor.fetchone()
            print(get_point)

            if listings[5] == "Borrow":
                points = get_point[0] + 20
            
            else:
                points = get_point[0] + 40
            


            mycursor.execute("Update User Set points = %s Where username = %s",[points,listings[1]])
            db.commit()


            # Adding the point system for the lender


            flash('Your booking has been successfully created!', 'success')
            return redirect(url_for('show_bookings'))
    
        else:
            
            if not selected_date and not selected_time:
                message = "Date and Time was Not Selected"
            
            elif not selected_date:
                message = "Date was Not Selected"
            
            else:
                message = "Time was Not Selected"
            

            return render_template(
                'booking.html',
                listings=listings,
                username=get_username,
                message=message,
                availability_by_date=availability_by_date,
                t=t,
            )
    
    return render_template(
        'booking.html',
        listings=listings,
        username=get_username,
        message="",
        availability_by_date=availability_by_date,
        t=t,
    )



@app.route('/bookings')
def show_bookings():

    if "user_email" not in session:
        return redirect(url_for('before_login'))  
    
    if "verify" not in session:
        return redirect(url_for('before_login'))
        
    get_email = session["user_email"]
    get_username = session["username"]

    # Fetch all bookings 
    mycursor.execute("SELECT * FROM Booking WHERE booking_email = %s", [get_email])
    bookings = mycursor.fetchall()

    # Fetch joined listing info
    mycursor.execute("""
        SELECT l.title, l.photo_path, l.listing_username, b.selected_date, b.selected_time 
        FROM Listing AS l 
        INNER JOIN Booking AS b 
        ON b.book_listing_id = l.listing_id 
        WHERE b.booking_email = %s
    """, [get_email])
    raw_book_list = mycursor.fetchall()

    lang_code = get_user_lang_code()     
    t = make_t(lang_code)

    # Compute badge
    today = date.today()
    book_list = []

    for row in raw_book_list:
        title, photo_path, from_user, selected_date, selected_time = row

        # Handle missing/empty dates
        if not selected_date:
            status = "No Date"
            booking_date = None
        else:
            # If it's already a date object, no need to parse
            if isinstance(selected_date, date):
                booking_date = selected_date
            else:
                booking_date = datetime.strptime(str(selected_date), "%Y-%m-%d").date()

            if booking_date > today:
                status = "Upcoming"
            elif booking_date == today:
                status = "Today"
            else:
                status = "Past"

        book_list.append((title, photo_path, from_user, selected_date, selected_time, status))

    # Pass username and email to template
    return render_template("viewbooking.html", book_list=book_list, username=get_username, email=get_email, t=t)


# Borrow
@app.route('/borrow')
def borrow():
    
    if "user_email" not in session:
        return redirect(url_for('before_login'))  
    
    if "verify" not in session:
        return redirect(url_for('before_login'))
    
    lang_code = get_user_lang_code()     
    t = make_t(lang_code)
    

    get_email = session.get("user_email")
    get_username = session.get("username")

   

  

     

    # Fetch all borrow listings excluding actively booked ones for other users
    rows = fetch_available_listings("borrow", get_email)


    

    # Convert to list of dicts
    borrow_listings = [
        {
            "id": row[0],
            "username": row[1],
            "title": row[2],
            "description": row[3],
            "category": row[4],
            "availability_date": row[6],
            "availability_time": row[7],
            "photo": row[8] if row[8] else 'uploads/placeholder.png'
        }
        for row in rows
    ]

    # Retrieve favorited listings


    mycursor.execute("Select wishlist_listing_id From Wishlist Where wishlist_email =%s",[get_email] )
    favourited_rows = mycursor.fetchall()
    favourited_listings = [row[0] for row in favourited_rows]
    print(favourited_listings)
    

    return render_template(
        "borrow.html",
        borrow_listings=borrow_listings,
        favourited_listings=favourited_listings,
        username=get_username, t=t
    )




# Free
@app.route('/free')
def free():

    if "user_email" not in session:
        return redirect(url_for('before_login'))  
    
    if "verify" not in session:
        return redirect(url_for('before_login'))
    
    lang_code = get_user_lang_code()     
    t = make_t(lang_code) 
        
    get_email = session.get("user_email")
    get_username = session.get("username")

 

    # Fetch all free listings excluding actively booked ones for other users
    rows = fetch_available_listings("free", get_email)



    # Convert to list of dicts
    free_listings = [
        {
            "id": row[0],
            "username": row[1],
            "title": row[2],
            "description": row[3],
            "category": row[4],
            "availability_date": row[6],
            "availability_time": row[7],
            "photo": row[8] if row[8] else 'uploads/placeholder.png'
        }
        for row in rows
    ]

    # Retrieve favorited listings
    mycursor.execute("Select wishlist_listing_id From Wishlist Where wishlist_email =%s",[get_email] )
    favourited_rows = mycursor.fetchall()
    favourited_listings = [row[0] for row in favourited_rows]
    print(favourited_listings)
    

    return render_template(
        "free.html",
        free_listings=free_listings,
        favourited_listings=favourited_listings,
        username=get_username,
        t=t
    )


# Wishlist 
@app.route('/wishlist')
def wishlist():

    if "user_email" not in session:
        return redirect(url_for('before_login'))  
    
    if "verify" not in session:
        return redirect(url_for('before_login'))

    get_email = session["user_email"]
    get_username = session["username"]

    lang_code = get_user_lang_code()     
    t = make_t(lang_code)

    # Inner join wishlist and listing table to get the listing details ( id, username, title, description, photo_path )
    mycursor.execute("Select ls.listing_id, ls.listing_username, ls.title, ls.description,  ls.photo_path From Listing As ls Inner Join Wishlist As ws On ws.wishlist_listing_id = ls.listing_id Where ws.wishlist_email = %s  ",[get_email])

    favourited_listings = mycursor.fetchall()

    for x in favourited_listings:
        print(x[0])

    
     

    return render_template('wishlist.html', user_info=user_info, username= get_username, favourited_listings = favourited_listings, t=t)





# Setting (Edit Profile)

@app.route('/settings/editprofile', methods=['GET', 'POST'])
def setting():

    if "user_email" not in session:
        return redirect(url_for('before_login'))  
    
    if "verify" not in session:
        return redirect(url_for('before_login'))
        
    get_email = session.get("user_email")
    get_username = session.get("username")

    lang_code = get_user_lang_code()     
    t = make_t(lang_code)


    if request.method == 'POST':
        new_bio = request.form.get("profile_bio").strip()
        new_gender = request.form.get("profile_gender")
        new_postal = request.form.get("profile_postal").strip()
        new_mobile = request.form.get("profile_mobile").strip()

        if len(new_mobile) != 8 or not new_mobile.isdigit():
            flash("Mobile number must be 8 digits.", "error")
            return redirect(url_for('setting'))

        if len(new_postal) != 6 or not new_postal.isdigit():
            flash("Postal code must be 6 digits.", "error")
            return redirect(url_for('setting'))
        
        
       
        new_bio = sanitisation(new_bio)

        Database.Update_Profile(
            get_username,
            new_gender,
            new_bio,
            get_email
        )
        db.commit()
        return redirect(url_for('setting'))

    
    mycursor.execute("SELECT * FROM User WHERE login_email = %s", [get_email])
    details = mycursor.fetchone()

  


    return render_template('setting_editprofile.html', username=get_username, email=get_email, details=details, t=t)


   
@app.post("/settings/editprofile/phone")
def api_update_phone():
    if "user_email" not in session:
        return jsonify({"ok": False, "message": "Not authenticated."}), 401
    if "verify" not in session:
        return jsonify({"ok": False, "message": "Not authenticated."}), 401

    email = session["user_email"]
    data = request.get_json(silent=True) or {}
    value = (data.get("value") or "").strip()

    # Server-side validation (Singapore numbers: 8 digits, starts with 8/9)
    if not value.isdigit() or len(value) != 8:
        return jsonify({"ok": False, "message": "Mobile number must be exactly 8 digits."}), 400
    if value[0] not in ("8", "9"):
        return jsonify({"ok": False, "message": "Mobile number must start with 8 or 9."}), 400

    try:
        Database.Update_Phone_Number(value, email)
        db.commit()
        masked = f"{value[:2]}****{value[-2:]}"
        return jsonify({"ok": True, "masked": masked})
    except Exception as e:
        return jsonify({"ok": False, "message": "Failed to update phone number."}), 500


@app.post("/settings/editprofile/postal")
def api_update_postal():
    if "user_email" not in session:
        return jsonify({"ok": False, "message": "Not authenticated."}), 401
    if "verify" not in session:
        return jsonify({"ok": False, "message": "Not authenticated."}), 401

    email = session["user_email"]
    data = request.get_json(silent=True) or {}
    value = (data.get("value") or "").strip()

    # Server-side validation (SG postal: exactly 6 digits)
    if not value.isdigit() or len(value) != 6:
        return jsonify({"ok": False, "message": "Postal code must be exactly 6 digits."}), 400

    try:
        Database.Update_Postal(value, email)
        db.commit()
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "message": "Failed to update postal code."}), 500




# Setting (Preference)

@app.route('/settings/preference',methods=['GET', 'POST'])
def preference():
    
    if "user_email" not in session:
        return redirect(url_for('before_login'))  
    
    if "verify" not in session:
        return redirect(url_for('before_login'))

    get_email = session.get("user_email")
    get_username = session.get("username")

    
    lang_code = get_user_lang_code()     
    t = make_t(lang_code)



    
      
    if request.method == 'POST':
        pass

    return render_template('preference.html', username = get_username,email = get_email, t=t)







# Setting (Change Password)

@app.route('/setting/security/change_password', methods=['GET', 'POST'])
def change_password():

    if "user_email" not in session:
        return redirect(url_for('before_login'))  
    
    if "verify" not in session:
        return redirect(url_for('before_login'))

    get_email = session.get("user_email")
    get_username = session.get("username")

    lang_code = get_user_lang_code()     
    t = make_t(lang_code)

    
     


    if request.method == 'POST':

        

        current_password = request.form.get("current_password")


        

      

        mycursor.execute("SELECT password,salt FROM Password_Storage WHERE email =%s ",[get_email])

        check_password = mycursor.fetchone()

        stored_salt = check_password[1]

            # salting the password
        current_password = current_password + stored_salt     


        hash = hashlib.new("SHA256")

        hash.update(current_password.encode())
        password_hash = hash.hexdigest()
        print(password_hash)

        # end of hashing



        if password_hash != check_password[0]:

            print("Something wrong part 1")

            message = "Current Password is Incorrect"
            return render_template('security_changepassword_light.html',username = get_username,email = get_email,message=message)

        
        changed_password = request.form.get("changed_password")
        confirm_password = request.form.get("confirm_new_password")

        if changed_password != confirm_password:

            print("Something wrong part 2")

            message = "New Password does not Match.Please Try Again and Remember Well"
            return render_template('security_changepassword_light.html',username = get_username,email = get_email,message=message)
        
        else:

            print("Changed success")

            # salting the new password

            confirm_password = confirm_password + stored_salt

            hash = hashlib.new("SHA256")
            hash.update(confirm_password.encode())
            new_password_hash = hash.hexdigest()
            print(new_password_hash)



            session["new_password"] = new_password_hash


            return redirect(url_for('verify_otp'))

 

    return render_template('security_changepassword_light.html',username = get_username,email = get_email,message="", t=t)




# Setting (2FA)

@app.route('/setting/security/2fa',methods=['GET', 'POST'])
def setting_2fa():
    
    if "user_email" not in session:
        return redirect(url_for('before_login'))  
    
    if "verify" not in session:
        return redirect(url_for('before_login'))
        
    get_email = session.get("user_email")
    get_username = session.get("username")

    lang_code = get_user_lang_code()     
    t = make_t(lang_code)
    
 

    
      

    return render_template('security_2fa_light.html', username = get_username,email = get_email, t=t)


# homepage, borrow, free


# Retrieve info
# points, username, listings photo_path, listings description, can click on the listing or have an edit profile button
# 

# View Profile
@app.route('/user_retrieve_info')
def user_retrieve_info():

    if "user_email" not in session:
        return redirect(url_for('before_login'))  
    
    if "verify" not in session:
        return redirect(url_for('before_login'))

    # Retrieve username and email from temp db
    get_email = session.get("user_email")
    get_username = session.get("username")
    
    lang_code = get_user_lang_code()     
    t = make_t(lang_code)

    mycursor.execute("SELECT points From User Where login_email = %s",[get_email])
    points = mycursor.fetchone()

    mycursor.execute("SELECT listing_id, listing_username, title, description, photo_path From Listing Where listing_email  =%s And listing_username = %s",[get_email,get_username])
    details = mycursor.fetchall()

    # Fetch Created wishlist or desire
    mycursor.execute("Select desire_id,desire_item, desire_description From Desire Where desire_email = %s",[get_email])
    desires = mycursor.fetchall()


   
    return render_template('user_retrieve_info.html',details = details ,points=points,username=get_username,desires = desires, t=t)




# this is when they want to create a new wishlist
@app.route('/create_wantlist',methods =["GET","POST"])
def create_wantlist():

    if "user_email" not in session:
        return redirect(url_for('before_login'))  
    
    if "verify" not in session:
        return redirect(url_for('before_login'))

    get_email = session.get("user_email")
    get_username = session.get("username")

    lang_code = get_user_lang_code()     
    t = make_t(lang_code)
    

    create_wishlist_form = Wishlist(request.form)
    if request.method == "POST" and create_wishlist_form.validate():

   
        Database.Create_Desire(get_email,create_wishlist_form.item.data,create_wishlist_form.description.data)
        db.commit()

        return redirect(url_for('user_retrieve_info'))
        

    
    return render_template('create_wishlist.html',form=create_wishlist_form, username = get_username, t=t)





# Update wishlist 
@app.route('/update_wantlist/<int:desire_id>',methods =["GET","POST"])
def update_wantlist(desire_id):
    
    if "user_email" not in session:
        return redirect(url_for('before_login'))  
    
    if "verify" not in session:
        return redirect(url_for('before_login'))

    
      




    update_wishlist_form = Wishlist(request.form)



    get_email = session.get("user_email")
    get_username = session.get("username")

    lang_code = get_user_lang_code()     
    t = make_t(lang_code)


    if request.method == "POST" and update_wishlist_form.validate():


        Database.Update_Desire(update_wishlist_form.item.data,update_wishlist_form.description.data,get_email,desire_id)
        db.commit()

        return redirect(url_for('user_retrieve_info'))  
    
    else:
        
        mycursor.execute("SELECT desire_item, desire_description From Desire Where desire_email = %s And desire_id =%s",[get_email,desire_id])
        get_desire = mycursor.fetchone()
        update_wishlist_form.item.data = get_desire[0]
        update_wishlist_form.description.data = get_desire[1]

        return render_template('update_wishlist.html',form=update_wishlist_form, username = get_username, t=t)



# Delete Wishlist

@app.route('/delete_wantlist/<int:desire_id>',methods =["GET","POST"])
def delete_wishlist(desire_id):

    if "user_email" not in session:
        return redirect(url_for('before_login'))  
    
    if "verify" not in session:
        return redirect(url_for('before_login'))


    get_email = session.get("user_email")
    get_username = session.get("username")

    mycursor.execute("SELECT desire_id from Desire Where desire_email = %s And desire_id = %s",[get_email,desire_id])

    check_desire = mycursor.fetchone()

    if not check_desire:

        
        return redirect(url_for('user_retrieve_info'))  
        

    if request.method == "POST":

        Database.Delete_Desire(get_email,desire_id)
        db.commit()

        return redirect(url_for('user_retrieve_info'))  




# Report User (Non-Admin)
@app.route('/report_user',methods = ["GET","POST"])
def report_user():

    if "user_email" not in session:
        return redirect(url_for('before_login'))  
    
    if "verify" not in session:
        return redirect(url_for('before_login'))

    get_email = session.get("user_email")
    get_username = session.get("username")

    lang_code = get_user_lang_code()     
    t = make_t(lang_code)
      


    report_form = Reporting(request.form)
    if request.method == "POST" and report_form.validate():
        email = report_form.report_email.data
        reason = report_form.report_option.data
        other_reason = report_form.report_other.data
        description = report_form.report_description.data


        mycursor.execute("Select login_email From User Where login_email = %s",[email])
        check_email = mycursor.fetchone()

        if check_email:

            Database.Create_Report(email,get_email,reason,other_reason,description)
            db.commit()


        return redirect(url_for('login_home'))
    
   
       
    
    return render_template('/report.html',form=report_form, username = get_username, t=t)

# Locate Bin
@app.route('/locate')
def locate():

    if "user_email" not in session:
        return redirect(url_for('before_login'))  
    
    if "verify" not in session:
        return redirect(url_for('before_login'))
    
    lang_code = get_user_lang_code()     
    t = make_t(lang_code) 

    get_email = session.get("user_email")
    get_username = session.get("username")

    

    mycursor.execute("SELECT bin_id, name, address, region, type, latitude, longitude FROM bins")
    bins_data = mycursor.fetchall()

  

    bins = {}

    for bin_row in bins_data:
        bin_id, name, address, region, bin_type, latitude, longitude = bin_row
        bins[str(bin_id)] = {
            "name": name,
            "address": address,
            "region": region,
            "type": bin_type,
            "latitude": latitude,
            "longitude": longitude
        }

    return render_template('locate.html', username=get_username, bins=bins, t=t)


# Admin Dashboard
@app.route('/dashboard')
def dashboard():

    if "user_email" not in session or "verify" not in session:
        return redirect(url_for('before_login')) 
    
    if session.get("role") != "Admin":
        return redirect(url_for('login_home'))

    role = session["role"] 

    if role == "Normal":
        return redirect(url_for(('login_home')))

    get_email = session.get("user_email")
    get_username = session.get("username")

    lang_code = get_user_lang_code()     
    t = make_t(lang_code)

    # reported user
    # total user
    # total listing
    # Total bookings
    mycursor.execute("Select * FROM User")
    users = mycursor.fetchall()

    mycursor.execute("SELECT * FROM Listing ")
    listings = mycursor.fetchall()

    mycursor.execute("SELECT * FROM Booking")
    bookings = mycursor.fetchall()

    mycursor.execute("SELECT * FROM Report")
    reports = mycursor.fetchall()


    mycursor.execute("SELECT Count(*) FROM User")
    num_of_users = mycursor.fetchone()[0]

    # if for example booking was empty or nothing, count(*) would return 0 

    mycursor.execute("Select Count(*) From Listing ")
    num_of_listings = mycursor.fetchone()[0]

    mycursor.execute("Select Count(*) From Booking")
    num_of_bookings = mycursor.fetchone()[0]

    mycursor.execute("Select Count(*) From Report")
    num_of_reports = mycursor.fetchone()[0]

    return render_template('dashboard.html', username = get_username, user_info = users, count = num_of_users, listing_count = num_of_listings, count_report = num_of_reports, t=t )



# Change this part
##############################################


# Delete User Account 
@app.route('/delete_user_info',methods =["GET","POST"])
def delete_user_info():
    
    if "user_email" not in session:
        return redirect(url_for('before_login'))  
    
    if "verify" not in session:
        return redirect(url_for('before_login'))

    if request.method == "POST":

        

        email = request.form.get('email')
        print(email)

        Database.Temp_Ban_User(email)
        db.commit()





    return redirect(url_for('dashboard')) 
   

# Admin View Report
@app.route('/view_report')
def view_report():
    
    if "user_email" not in session:
        return redirect(url_for('before_login')) 
    
    if "verify" not in session:
        return redirect(url_for('before_login'))

    role = session["role"] 

    if role == "Normal":
        return redirect(url_for(('login_home')))

    get_email = session.get("user_email")
    get_username = session.get("username")

    lang_code = get_user_lang_code()     
    t = make_t(lang_code)

    mycursor.execute("Select * From Report")
    report_list = mycursor.fetchall()


    mycursor.execute("Select Count(*) From Report")
    num_of_reports = mycursor.fetchone()[0]

# added
    mycursor.execute("SELECT * From Log")
    log_list = mycursor.fetchall()

    mycursor.execute("Select Count(*) From Log")
    num_of_log = mycursor.fetchone()[0]


    return render_template('/view_report.html',count= num_of_reports, report_list=report_list,log_list=log_list,num_of_log=num_of_log, username = get_username, t=t)





# Dashboard Feedback
@app.route('/dashboard_feedback')
def dashboard_feedback():

    if "user_email" not in session:
        return redirect(url_for('before_login')) 
    
    if "verify" not in session:
        return redirect(url_for('before_login'))

    role = session["role"] 

    if role == "Normal":
        return redirect(url_for(('login_home')))

    get_email = session.get("user_email")
    get_username = session.get("username")

    lang_code = get_user_lang_code()     
    t = make_t(lang_code)
        
    mycursor.execute("Select * From Feedback")
    feedbacklist = mycursor.fetchall()

    mycursor.execute("Select Count(*) From Feedback")
    num_of_feedback = mycursor.fetchone()[0]


    return render_template('dashboard_feedback.html', username = get_username, count = num_of_feedback, feedbacklist = feedbacklist, t=t)

  



# Start of Part 2 of NeighbourlyNest 

# Reward Redemption
@app.route('/reward')
def reward():

    if "user_email" not in session:
        return redirect(url_for('before_login'))  
    
    if "verify" not in session:
        return redirect(url_for('before_login'))


    get_email = session.get("user_email")
    get_username = session.get("username")

 

    mycursor.execute("SELECT points From User Where login_email = %s",[get_email])
    points = mycursor.fetchone()

    lang_code = get_user_lang_code()     
    t = make_t(lang_code) 
      

    return render_template('reward.html', username = get_username, points = points, t=t)



@app.route('/reward/e-voucher-uniqgift')
def uniqgift():
    
    if "user_email" not in session:
        return redirect(url_for('before_login'))  
    
    if "verify" not in session:
        return redirect(url_for('before_login'))

    get_email = session.get("user_email")
    get_username = session.get("username")
   
    
    mycursor.execute("SELECT points From User Where login_email = %s",[get_email])
    points = mycursor.fetchone()

    lang_code = get_user_lang_code()     
    t = make_t(lang_code)

    
      

    return render_template('e-voucher-uniqgift.html', username = get_username, points = points, t=t)

@app.route('/reward/10-ntuc-fairprice-e-voucher')
def ntuc():

    if "user_email" not in session:
        return redirect(url_for('before_login'))  
    
    if "verify" not in session:
        return redirect(url_for('before_login'))

    get_email = session.get("user_email")
    get_username = session.get("username")

    lang_code = get_user_lang_code()     
    t = make_t(lang_code)

    mycursor.execute("SELECT points From User Where login_email = %s",[get_email])
    points = mycursor.fetchone()

    
        

    return render_template('10-ntuc-fairprice-e-voucher.html', username = get_username, points = points, t=t)


@app.route('/reward/10-koufu-e-voucher')
def koufu():

    if "user_email" not in session:
        return redirect(url_for('before_login'))  
    
    if "verify" not in session:
        return redirect(url_for('before_login'))
    
    get_email = session.get("user_email")
    get_username = session.get("username")

    lang_code = get_user_lang_code()     
    t = make_t(lang_code)

    mycursor.execute("SELECT points From User Where login_email = %s",[get_email])
    points = mycursor.fetchone()

    
    return render_template('10-koufu-e-voucher.html', username = get_username, points = points, t=t)



# Loading JSON File 
def load_translations(lang: str) -> dict:
    path = os.path.join(app.root_path, "translations", f"{lang}.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[i18n] missing file: {path}")
        return {}
    except json.JSONDecodeError as e:
        print(f"[i18n] bad JSON in {path}: {e}")
        return {}

def make_translator(lang):
    translations = load_translations(lang)
    fallback = load_translations("en")

    def t(key, **kwargs):
        # nested keys: "pref.title"
        val = translations
        for part in key.split("."):
            if isinstance(val, dict) and part in val:
                val = val[part]
            else:
                val = None
                break

        if val is None:  # fallback
            val = fallback
            for part in key.split("."):
                if isinstance(val, dict) and part in val:
                    val = val[part]
                else:
                    val = key
                    break

        try:
            return str(val).format(**kwargs)
        except Exception:
            return str(val)

    return t


def obfuscate_email(email):
    try:
        user, domain = email.split('@')
        if len(user) <= 2:
            return '*' * len(user) + '@' + domain
        return user[:2] + '*' * (len(user) - 2) + '@' + domain
    except Exception:
        return email

app.jinja_env.filters['obfuscate_email'] = obfuscate_email



# Logout

@app.route('/logout')
def logout():

    if "get_date" in session:
        get_date = session["get_date"]

        get_email = session.get("user_email")

        today = str(date.today())
        print(today)

        current_time_of_log = datetime.now().strftime("%H:%M:%S")
        print(current_time_of_log)

        Database.Update_Log(today,current_time_of_log,get_email,get_date)
        db.commit()
        
    session.clear()

    

    return redirect(url_for('before_login'))





@app.route("/create-checkout-session", methods=["GET"])
def create_checkout_session():
    try:
        donation_type = session.get("donation_type", "Individual")
        frequency = session.get("donation_frequency", "One Time")
        amount = session.get("donation_amount")

        if amount == "other":
            amount = session.get("other_amount_value")

        if not amount:
            return "Please enter a valid donation amount.", 400

        amount_cents = int(float(amount) * 100)

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                'price_data': {
                    'currency': 'sgd',
                    'product_data': {
                        'name': f"{frequency} {donation_type} Donation",
                    },
                    'unit_amount': amount_cents,
                },
                'quantity': 1,
            }],
            mode='payment',
            customer_email=session.get("email"),
            metadata={
                "Donor Name": f"{session.get('first_name', '')} {session.get('last_name', '')}",
                "Donation Type": donation_type,
                "Frequency": frequency,
            },
            success_url=url_for('confirmation', _external=True),
            cancel_url=url_for('donate', _external=True),
        )

        return redirect(checkout_session.url, code=303)

    except ValueError:
        return "Invalid donation amount. Please enter a number.", 400
    except Exception as e:
        return f"Error creating Stripe session: {str(e)}", 500


@app.route('/confirmation')
def confirmation():
    return render_template('confirmation.html')

@app.route("/ask_chatbot", methods=["POST"])
def ask_chatbot():
    return render_template('/includes/chatbot.html', CHATGPT_SECRET_KEY = os.getenv("CHATGPT_SECRET_KEY"))



# from events import get_all_events

# Community Events
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

@app.route('/events')
def events():
    if "user_email" not in session:
        return redirect(url_for('before_login'))
    
    if "verify" not in session:
        return redirect(url_for('before_login'))

    get_email = session.get("user_email")
    get_username = session.get("username")

    lang_code = get_user_lang_code()     
    t = make_t(lang_code) 

    # Fetch user's postal code
    mycursor.execute("SELECT postal_code FROM User WHERE login_email = %s", [get_email])
    postal_code_row = mycursor.fetchone()
    postal_code = postal_code_row[0] if postal_code_row else None

    # Geocode postal code to get coordinates
    geolocator = Nominatim(user_agent="NeighbourlyNest")
    user_location = None
    try:
        location = geolocator.geocode(f"{postal_code}, Singapore")
        if location:
            user_location = (location.latitude, location.longitude)
    except Exception as e:
        print(f"[Geocoding Error] {e}")

    # Fetch all events
    mycursor.execute("""
        SELECT event_id, title, organiser, ref_code, start_date, end_date,
               time, location, price, region, latitude, longitude
        FROM events
    """)
    events_data = mycursor.fetchall()

    events = {}
    nearest_events = []

    for row in events_data:
        event_id, title, organiser, ref_code, start_date, end_date, time, location, price, region, latitude, longitude = row
        event = {
            "title": title,
            "organiser": organiser,
            "ref_code": ref_code,
            "start_date": start_date,
            "end_date": end_date,
            "time": time,
            "location": location,
            "price": price,
            "region": region,
            "latitude": latitude,
            "longitude": longitude
        }
        events[str(event_id)] = event

        # Distance-based filtering
        if user_location and latitude and longitude:
            event_coords = (latitude, longitude)
            distance_km = geodesic(user_location, event_coords).km
            if distance_km <= 5:
                nearest_events.append(event)

    return render_template(
        "events.html",
        username=get_username,
        postal_code=postal_code,
        events=events,
        nearest_events=nearest_events, 
        t=t
    )

# Reward OTP


@app.route("/voucher/send-otp", methods=["POST"])
def voucher_send_otp():
    if "user_email" not in session:
        return jsonify({"ok": False, "message": "Not authenticated."}), 401

    email = session["user_email"]
    body = request.get_json(silent=True) or {}
    qty = max(1, int(body.get("quantity", 1)))
    total_points = qty * POINTS_PER_VOUCHER

    if user_points(mycursor, email) < total_points:
        return jsonify({"ok": False, "message": "Insufficient points."}), 400

    if not can_resend(mycursor, email):
        return jsonify({"ok": False, "message": "Please wait before requesting another OTP."}), 429

    code = upsert_otp(db, mycursor, email, qty, total_points)
    try:
        send_voucher_otp_email(email, code, qty, total_points)
        return jsonify({"ok": True, "message": "OTP sent."})
    except Exception as e:
        # TEMPORARY: show the concrete error to debug
        return jsonify({"ok": False, "message": f"Email error: {e}"}), 500


@app.route("/voucher/resend-otp", methods=["POST"])
def voucher_resend_otp():
    if "user_email" not in session:
        return jsonify({"ok": False, "message": "Not authenticated."}), 401

    email = session["user_email"]

    if not can_resend(mycursor, email):
        return jsonify({"ok": False, "message": "Please wait before requesting another OTP."}), 429

    row = get_active_otp(mycursor, email)
    if not row:
        return jsonify({"ok": False, "message": "No pending verification."}), 400

    otp_id, code_hash_db, expires_at, attempts, qty, total_points = row

    code = upsert_otp(db, mycursor, email, qty, total_points)
    try:
        send_voucher_otp_email(email, code, qty, total_points)
        return jsonify({"ok": True, "message": "OTP resent."})
    except Exception as e:
        # print(e)
        return jsonify({"ok": False, "message": "Failed to send email."}), 500

@app.route("/voucher/verify-otp", methods=["POST"])
def voucher_verify_otp():
    if "user_email" not in session:
        return jsonify({"ok": False, "message": "Not authenticated."}), 401

    email = session["user_email"]
    data = request.get_json(silent=True) or {}
    code = (data.get("code") or "").strip()
    qty_client = max(1, int(data.get("quantity", 1))) 

    row = get_active_otp(mycursor, email)
    if not row:
        return jsonify({"ok": False, "message": "No pending verification."}), 400

    rewardotp_id, code_hash_db, expires_at, attempts, qty_db, total_points_db = row

    if attempts >= 6:
        return jsonify({"ok": False, "message": "Too many attempts. Request a new code."}), 429

    # expiry / code check
    from otp_utils import _now_utc_naive, _sha256_bytes
    if expires_at < _now_utc_naive():
        return jsonify({"ok": False, "message": "Code expired. Request a new code."}), 400

    if _sha256_bytes(code) != code_hash_db:
        mycursor.execute("UPDATE otp_verifications SET attempts=attempts+1 WHERE rewardotp_id=%s", (rewardotp_id,))
        db.commit()
        return jsonify({"ok": False, "message": "Incorrect code."}), 400

    mycursor.execute("DELETE FROM otp_verifications WHERE rewardotp_id=%s", (rewardotp_id,))
    db.commit()


    current_points = user_points(mycursor, email)
    if current_points < total_points_db:
        return jsonify({"ok": False, "message": "Insufficient points at verification."}), 400

    new_points = current_points - total_points_db
    update_user_points(db, mycursor, email, new_points)


    try:
        send_voucher_success_email(
            to_email=email,
            user_name=session.get("username", "Valued User")
        )
        return jsonify({
            "ok": True,
            "message": "OTP verified. Voucher sent to your email.",
            "remaining_points": new_points
        })
    except Exception as e:

        return jsonify({
            "ok": True,
            "message": f"OTP verified. (Email send failed: {e})",
            "remaining_points": new_points
        })


@app.route('/setting/security/2fa/backup-codes', methods=['POST'])
def setting_issue_backup_codes():
    if "user_email" not in session:
        return jsonify({"ok": False, "error": "unauthorized"}), 401
    if "verify" not in session:
        return jsonify({"ok": False, "error": "unauthorized"}), 401

    get_email = session.get("user_email")
    try:

        codes = generate_2fa_backup_codes(get_email, count=10, length=10)
        return jsonify({"ok": True, "codes": codes})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.context_processor
def inject_prefs():
    """
    Expose theme, font_size and language to all templates.
    Falls back to sane defaults when not logged in / missing rows.
    """
    theme = "system"
    font_size = 100
    language = "English"

    if "user_email" in session:
        mycursor.execute(
            "SELECT language, font_size, theme FROM Preference WHERE login_email=%s",
            (session["user_email"],)
        )
        row = mycursor.fetchone()
        if row:
            language = row[0] or language
            try:
                font_size = int(row[1] or font_size)
            except (TypeError, ValueError):
                font_size = 100
            theme = (row[2] or theme).lower()

    return {
        "current_theme": theme,
        "current_font_size": font_size,
        "current_language": language
    }


@app.post("/api/preferences")
def api_update_preferences():
    if "user_email" not in session:
        return jsonify({"ok": False, "error": "not_authenticated"}), 401

    data = request.get_json(silent=True) or {}
    lang = data.get("language")
    font = data.get("font_size")

    if lang is None and font is None:
        return jsonify({"ok": False, "error": "no_fields"}), 400

    if font is not None:
        try:
            font = int(font)
            if font < 50 or font > 200:
                return jsonify({"ok": False, "error": "bad_font"}), 400
        except (TypeError, ValueError):
            return jsonify({"ok": False, "error": "bad_font"}), 400

    email = session["user_email"]

    mycursor.execute(
        "SELECT preference_id, language, font_size, theme FROM Preference WHERE login_email=%s",
        (email,)
    )
    row = mycursor.fetchone()

    if row:
        cur_lang, cur_font = row[1], row[2]
        new_lang = lang if lang is not None else cur_lang
        new_font = font if font is not None else cur_font
        mycursor.execute(
            "UPDATE Preference SET language=%s, font_size=%s WHERE login_email=%s",
            (new_lang, new_font, email)
        )
        db.commit()
        lang, font = new_lang, new_font
    else:
        mycursor.execute(
            "INSERT INTO Preference (login_email, language, font_size) VALUES (%s,%s,%s)",
            (email, lang or "English", font or 100)
        )
        db.commit()
        if lang is None:
            lang = "English"
        if font is None:
            font = 100

    return jsonify({"ok": True, "language": lang, "font_size": font})



@app.post("/api/preferences/theme")
def api_update_theme():
    if "user_email" not in session:
        return jsonify({"ok": False, "error": "not_authenticated"}), 401

    data = request.get_json(silent=True) or {}
    theme = (data.get("theme") or "").lower()
    if theme not in ("system", "light", "dark"):
        return jsonify({"ok": False, "error": "bad_theme"}), 400

    email = session["user_email"]
    mycursor.execute("SELECT preference_id FROM Preference WHERE login_email=%s", (email,))
    row = mycursor.fetchone()
    if row:
        mycursor.execute("UPDATE Preference SET theme=%s WHERE login_email=%s", (theme, email))
    else:
        mycursor.execute("INSERT INTO Preference (login_email, theme) VALUES (%s,%s)", (email, theme))
    db.commit()

    return jsonify({"ok": True, "theme": theme})


LANG_MAP = {
    "English": "en",
    "Mandarin": "zh",
    "Bahasa Melayu": "id",  
    "en": "en", "zh": "zh", "id": "id",
}

def get_user_lang_code():
    """Return language code like 'en'/'zh'/'id' using DB if available, else session/session default."""

    if "user_email" in session:
        mycursor.execute("SELECT language FROM Preference WHERE login_email=%s", (session["user_email"],))
        row = mycursor.fetchone()
        if row and row[0]:
            return LANG_MAP.get(row[0], "en")
    # otherwise use session["lang"] if you still set it somewhere
    return LANG_MAP.get(session.get("lang", "en"), "en")

def make_t(lang_code: str):

    trans = load_translations(lang_code)
    fallback = load_translations("en")

    def lookup(d, key):
        cur = d
        for part in key.split("."):
            if not isinstance(cur, dict) or part not in cur:
                return None
            cur = cur[part]
        return cur

    def t(key: str, **kwargs):
        val = lookup(trans, key)
        if val is None:
            val = lookup(fallback, key)
        if val is None:
            val = key
        try:
            return str(val).format(**kwargs)
        except Exception:
            return str(val)
    return t


# TOTP Secret (Symmetric Key)
def _get_aes_key() -> bytes:
    key_b64 = os.getenv("TOTP_ENC_KEY")
    if not key_b64:
        raise RuntimeError("Missing TOTP_ENC_KEY in environment")
    return base64.urlsafe_b64decode(key_b64)

def encrypt_secret(plaintext: str) -> str:
    key = _get_aes_key()
    aes = AESGCM(key)
    nonce = os.urandom(12)
    ct = aes.encrypt(nonce, plaintext.encode("utf-8"), None)
    return base64.urlsafe_b64encode(nonce + ct).decode("utf-8")

def decrypt_secret(token_b64: str) -> str:
    key = _get_aes_key()
    data = base64.urlsafe_b64decode(token_b64)
    nonce, ct = data[:12], data[12:]
    aes = AESGCM(key)
    pt = aes.decrypt(nonce, ct, None)
    return pt.decode("utf-8")

@app.route('/userchat')
def userchat():
    if "user_email" not in session:
        return redirect(url_for('before_login'))
    
    if "verify" not in session:
        return redirect(url_for('before_login'))

    get_email = session.get("user_email")
    get_username = session.get("username")
    chat_id = request.args.get("chat_id", type=int)

    lang_code = get_user_lang_code()
    t = make_t(lang_code)

    chats = fetch_user_chats(get_email)
    selected_chat = None
    messages = []

    if chat_id is None and chats:
        chat_id = chats[0]["chat_id"]

    if chat_id is not None:
        selected_chat = fetch_chat_details(chat_id, get_email)
        if selected_chat:
            messages = fetch_chat_messages(chat_id)
        else:
            chat_id = None

    return render_template(
        'userchat.html',
        t=t,
        username=get_username,
        chats=chats,
        selected_chat=selected_chat,
        messages=messages,
        active_chat_id=chat_id,
        user_email=get_email,
    )


@app.route('/userchat/<int:chat_id>')
def userchat_thread(chat_id):
    if "user_email" not in session:
        return redirect(url_for('before_login'))

    if "verify" not in session:
        return redirect(url_for('before_login'))

    return redirect(url_for('userchat', chat_id=chat_id))


@app.route('/userchat/<int:chat_id>/message', methods=['POST'])
def send_chat_message(chat_id):
    if "user_email" not in session:
        return redirect(url_for('before_login'))

    if "verify" not in session:
        return redirect(url_for('before_login'))

    get_email = session.get("user_email")
    message_text = (request.form.get("message") or "").strip()
    if not message_text:
        return redirect(url_for('userchat', chat_id=chat_id))

    chat = fetch_chat_details(chat_id, get_email)
    if not chat:
        return redirect(url_for('userchat'))

    mycursor.execute(
        "INSERT INTO ChatMessage (chat_id, sender_email, message_text, message_type) VALUES (%s,%s,%s,%s)",
        (chat_id, get_email, message_text, "user"),
    )
    db.commit()
    _emit_chat_message(
        chat_id,
        {
            "chat_id": chat_id,
            "message_id": mycursor.lastrowid,
            "sender_email": get_email,
            "message_text": message_text,
            "message_type": "user",
        },
    )

    return redirect(url_for('userchat', chat_id=chat_id))


if __name__ == '__main__':
    socketio.run(app, debug=True)

    # app.run(ssl_context=("localhost+2.pem", "localhost+2-key.pem", debug=True))
