import mysql.connector
import Bins


db = mysql.connector.connect(
    host = "localhost",
    user = "root",
    passwd = "Helloworld1$",
    database = "Neighbourly_Database"
)


mycursor = db.cursor()
  

def create_database():
# Create Database

    mycursor.execute("CREATE DATABASE Neighbourly_Database")


def table_creation():

    mycursor.execute("CREATE TABLE IF NOT EXISTS User (user_id Varchar(50), first_name Varchar(50), last_name Varchar(50), username Varchar(30), gender Varchar(7) Check(gender In('Male','Female','Other')), postal_code Int(6), email Varchar(100), login_email Varchar(100) PRIMARY KEY NOT NULL, phone_num Int(15), bio Varchar(150), points int(4), role Varchar(15) Check(role In('Normal','Admin')) Default 'Normal'  ) ")

    mycursor.execute("CREATE TABLE IF NOT EXISTS Password_Storage (email  Varchar(150) PRIMARY KEY NOT NULL, password Varchar(64), salt Varchar(32) ,totp Varchar(255) , FOREIGN KEY(email) REFERENCES User(login_email)   )")

    mycursor.execute("CREATE TABLE IF NOT EXISTS Listing ( listing_id INT  AUTO_INCREMENT PRIMARY KEY NOT NULL, listing_username Varchar(30) , title Varchar(100), description Varchar(150), category ENUM('Food','Non-Food'), type ENUM('Borrow','Free'), availability_date Varchar(20) , availability_time Varchar(20), photo_path Varchar(255), listing_email Varchar(100), FOREIGN KEY (listing_email) REFERENCES User(login_email))")


    mycursor.execute(" CREATE TABLE IF NOT EXISTS Booking ( booking_id int AUTO_INCREMENT PRIMARY KEY NOT NULL, booking_email Varchar(100), book_listing_id int, selected_date Varchar(15) , selected_time Varchar(15), FOREIGN KEY (booking_email) REFERENCES User(login_email), FOREIGN KEY (book_listing_id) REFERENCES Listing(listing_id) ON DELETE CASCADE ) ")


    mycursor.execute(" CREATE TABLE IF NOT EXISTS Wishlist ( wishlist_id int AUTO_INCREMENT PRIMARY KEY NOT NULL, wishlist_email Varchar(100), wishlist_listing_id int, FOREIGN KEY (wishlist_email) REFERENCES User(login_email), FOREIGN KEY (wishlist_listing_id) REFERENCES Listing(listing_id) ) ")


    mycursor.execute ( "CREATE TABLE IF NOT EXISTS Desire ( desire_id int AUTO_INCREMENT PRIMARY KEY NOT NULL, desire_email Varchar(100), desire_item Varchar(100), desire_description Varchar(150), FOREIGN KEY (desire_email) REFERENCES User(login_email) )")

    mycursor.execute("CREATE TABLE IF NOT EXISTS Feedback ( feedback_id int AUTO_INCREMENT PRIMARY KEY NOT NULL, feedback_username Varchar(30), feedback_email Varchar(100), message Varchar(255) )")   
 

    mycursor.execute("CREATE TABLE IF NOT EXISTS Report ( report_id int AUTO_INCREMENT Primary Key NOT NULL, reported_email Varchar(100), reporter_email Varchar(100), reason Varchar(50), other_reason Varchar(50), description Varchar(150), FOREIGN KEY (reporter_email) REFERENCES User(login_email) )")

# --------------------------------------------------------------------------------------------------------
    mycursor.execute("CREATE TABLE IF NOT EXISTS bins (bin_id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,name VARCHAR(100),address VARCHAR(200),region ENUM('North', 'East', 'West', 'Central', 'Northeast', 'South', 'Southeast', 'Northwest'),type ENUM('Recycling Bin', 'E-recycling Bin'),latitude DOUBLE,longitude DOUBLE)")
    
    mycursor.execute("CREATE TABLE IF NOT EXISTS Preference (preference_id INT AUTO_INCREMENT PRIMARY KEY, login_email VARCHAR(100) NOT NULL, language VARCHAR(20) DEFAULT 'English', font_size INT DEFAULT 100, theme Varchar(8) Check(theme In('system','light','dark')) DEFAULT 'system', CONSTRAINT fk_pref_user FOREIGN KEY (login_email)  REFERENCES User(login_email) ON DELETE CASCADE, CONSTRAINT uniq_pref_user UNIQUE (login_email))")


    mycursor.execute("CREATE TABLE IF NOT EXISTS events (event_id INT AUTO_INCREMENT PRIMARY KEY, title VARCHAR(255), organiser VARCHAR(255), ref_code VARCHAR(50), start_date DATE, end_date DATE, time VARCHAR(50), location VARCHAR(255), price VARCHAR(50), region VARCHAR(50), latitude DOUBLE, longitude DOUBLE )")

    mycursor.execute("CREATE TABLE IF NOT EXISTS otp_verifications (rewardotp_id INT AUTO_INCREMENT PRIMARY KEY, user_email VARCHAR(100) NOT NULL, purpose ENUM('voucher') NOT NULL DEFAULT 'voucher', code_hash BINARY(32) NOT NULL, expires_at DATETIME NOT NULL, attempts INT NOT NULL DEFAULT 0, last_sent_at DATETIME NOT NULL, qty INT NOT NULL, total_points INT NOT NULL, INDEX (user_email, purpose), INDEX (expires_at), FOREIGN KEY (user_email) REFERENCES User(login_email) ON DELETE CASCADE)")  # Verify Reward OTP

    # One-time 2FA backup codes (hashed, salted, single-use)
    mycursor.execute("CREATE TABLE IF NOT EXISTS twofa_backup_codes (backup_id INT AUTO_INCREMENT PRIMARY KEY, user_email VARCHAR(100) NOT NULL, code_hash BINARY(32) NOT NULL, salt BINARY(16) NOT NULL, used_at DATETIME NULL, created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (user_email) REFERENCES User(login_email) ON DELETE CASCADE, INDEX (user_email), INDEX (used_at))")

    
    mycursor.execute("CREATE TABLE IF NOT EXISTS Log (log_id Int AUTO_INCREMENT Primary Key, log_email Varchar(100), failed_login Int(5),log_date Varchar(10),log_time Varchar(10),status Varchar(10) Check(status In('Success','Failed','New')),logout_date Varchar(10)  Default 'No Date',logout_time Varchar(10) Default 'No Time' ,FOREIGN KEY (log_email) REFERENCES User(login_email) ) ")

# language, font size, Theme (system, light, dark mode) 
# def add_points():
#     mycursor.execute("Update User set points = 2000 WHERE first_name = 'Rachel'")
#     db.commit()

# add_points()

# add_points()
# Create

def Create_Log(log_email,failed_login,log_date,log_time,status):
    mycursor.execute("INSERT INTO Log(log_email,failed_login,log_date,log_time,status) VALUES (%s,%s,%s,%s,%s)",(log_email,failed_login,log_date,log_time,status))
    db.commit()




def Create_Reward(reward_name,reward_point,reward_photo_path):
    mycursor.execute("INSERT INTO Reward(reward_name,reward_point,reward_photo_path) VALUES (%s,%s,%s)",(reward_name,reward_point,reward_photo_path))
    db.commit()

def Create_User(user_id, first_name, last_name, login_email):
    mycursor.execute(" INSERT INTO User(user_id, first_name, last_name, login_email) VALUES (%s,%s,%s,%s)", (user_id,first_name,last_name,login_email))
    db.commit()


def Create_User_p2(username, gender, postal_code, email, phone_num, bio, points,login_email):
    mycursor.execute("UPDATE User SET username = %s, gender = %s, postal_code = %s, email = %s, phone_num = %s, bio = %s, points = %s WHERE login_email = %s", (username,gender,postal_code,email,phone_num,bio,points,login_email))
    db.commit()


def Create_Admin(admin_id,first_name,last_name,username,gender,postal_code,login_email,phone_num,bio):
    mycursor.execute("INSERT INTO Admin(admin_id,first_name,last_name,username,gender,postal_code,login_email,phone_num,bio) Values (%s,%s,%s,%s,%s,%s,%s,%s,%s)",(admin_id,first_name,last_name,username,gender,postal_code,login_email,phone_num,bio))
    db.commit()


def Create_Password(email,password,salt):
    mycursor.execute("INSERT INTO Password_Storage(email,password,salt) VALUES (%s,%s,%s)",(email,password,salt))
    db.commit()

def Create_Password_p2(totp,email):
    mycursor.execute("UPDATE Password_Storage Set totp = %s WHERE email = %s ",(totp,email))
    db.commit()

def Create_Admin_Password(email,password,totp):
    mycursor.execute("INSERT into Admin_Password_Storage (email,password,totp) Values (%s,%s,%s) ",(email,password,totp))
    db.commit()
    


def Create_Listing(listing_username, title, description, category, type, availability_date, availability_time, photo_path, listing_email):
    mycursor.execute("INSERT INTO Listing( listing_username, title, description, category, type, availability_date, availability_time, photo_path, listing_email ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",(listing_username, title, description, category, type, availability_date, availability_time, photo_path, listing_email))
    db.commit()


def Create_Booking(booking_email,book_listing_id,selected_date,selected_time):
    mycursor.execute("INSERT INTO Booking (booking_email, book_listing_id, selected_date, selected_time) VALUES (%s,%s,%s,%s)", (booking_email, book_listing_id, selected_date, selected_time))
    db.commit()


def Create_Wishlist(wishlist_email,wishlist_listing_id):
    mycursor.execute("INSERT INTO Wishlist (wishlist_email,wishlist_listing_id) VALUES (%s,%s)",(wishlist_email,wishlist_listing_id))
    db.commit()


def Create_Desire(desire_email,desire_item,desire_description):
    mycursor.execute("INSERT INTO Desire (desire_email,desire_item,desire_description) VALUES (%s,%s,%s)",(desire_email,desire_item,desire_description))
    db.commit()


def Create_Feedback(feedback_username, feedback_email,message):
    mycursor.execute("INSERT INTO Feedback (feedback_username, feedback_email,message) VALUES (%s,%s,%s)",(feedback_username, feedback_email,message))
    db.commit()


def Create_Report(reported_email, reporter_email, reason, other_reason, description):
    mycursor.execute("INSERT INTO Report (reported_email, reporter_email, reason, other_reason, description) VALUES(%s,%s,%s,%s,%s)",(reported_email, reporter_email, reason, other_reason, description))
    db.commit()


# --------------------------------------------------------------------------------------------------------
def Create_Preferences(login_email):
    mycursor.execute("Insert Into Preference(login_email) Values(%s) ",[login_email])
    db.commit()



def Create_Admin(login_email):
    mycursor.execute("Update User Set role = 'Admin' Where login_email = %s ",[login_email]) 
    db.commit()

#Create_Admin("sjy0504j@gmail.com")




# UPDATE



def Update_Password(password,email):
    mycursor.execute("UPDATE Password_Storage Set password = %s WHERE email = %s", (password,email))
    db.commit()

# Note here that points are not updated when a user modifies their profile

def Update_User(username, gender, postal_code, email, phone_num, bio, login_email):
    mycursor.execute("UPDATE User SET username = %s, gender = %s, postal_code = %s, email = %s, phone_num = %s, bio = %s WHERE login_email = %s",(username, gender, postal_code, email, phone_num, bio, login_email))
    db.commit()

def Update_Profile(username,gender,bio,login_email):
    mycursor.execute("UPDATE User SET username =%s, gender=%s, bio = %s Where login_email = %s ",(username,gender,bio,login_email))
    db.commit()

def Update_Phone_Number(phone_num,login_email):
    mycursor.execute("UPDATE User SET phone_num =%s Where login_email = %s ",(phone_num,login_email))
    db.commit()

def Update_Postal(postal_code,login_email):
    mycursor.execute("UPDATE User SET postal_code =%s Where login_email = %s ",(postal_code,login_email))
    db.commit()

def Update_Listing(title, description, category, type, availability_date, availability_time, photo_path,login_email,listing_id):
    mycursor.execute("UPDATE Listing Set title = %s, description = %s, category = %s, type = %s, availability_date = %s, availability_time = %s, photo_path = %s WHERE listing_email = %s And listing_id = %s", (title, description, category, type, availability_date, availability_time, photo_path,login_email,listing_id))
    db.commit()


def Update_Desire(desire_item,desire_description,login_email,desire_id):
    mycursor.execute("UPDATE Desire Set desire_item = %s, desire_description = %s Where desire_email = %s And desire_id = %s ", (desire_item,desire_description,login_email,desire_id))
    db.commit()


# Need to check on this update_feedback - get back to this later, also the feedback in db contains username 

def Update_Feedback(message,login_email):
    mycursor.execute("UPDATE Feedback Set message = %s WHERE feedback_email = %s ", (message,login_email))
    db.commit()


def Update_Log(logout_date,logout_time,log_email,get_date):
    mycursor.execute("UPDATE Log SET logout_date = %s,logout_time =%s Where log_email = %s And log_date = %s ",(logout_date,logout_time,log_email,get_date))
    db.commit()

# Need go research on this, overhere update actually means removing the heart from the pic so technically delete

def Update_Wishlist(listing_id,action,login_email):
    
    if action == "add":

        Create_Wishlist(login_email,listing_id)
        db.commit()
    
    elif action == "remove":
        mycursor.execute("SELECT * FROM Wishlist WHERE wishlist_email = %s AND wishlist_listing_id = %s ", (login_email,listing_id))

        result = mycursor.fetchone()

        if result:
            print("Found: {}".format(result))

            mycursor.execute("DELETE FROM Wishlist WHERE wishlist_email = %s AND wishlist_listing_id = %s ", (login_email,listing_id))
            db.commit()


def Update_Preference(language,font_size,theme,login_email):
    mycursor.execute("Update Preference Set language = %s, font_size = %s, theme = %s Where login_email = %s ",(language,font_size,theme,login_email))
    db.commit()
    

# Delete parts

# Setting the username to block so we can temporary ban
def Temp_Ban_User(login_email):
    mycursor.execute("Update User Set username = 'Block' Where login_email =%s ",[login_email])
    db.commit()

# Delete Listing

def Delete_Listing(login_email, listing_id):

    mycursor.execute("Select listing_id From Listing Where listing_email = %s And listing_id = %s",(login_email,listing_id))

    check_list = mycursor.fetchone()

    if check_list:

        print("Have or not lol")

        mycursor.execute("Delete From Listing Where listing_email = %s And listing_id = %s",(login_email,listing_id))
        db.commit()


def Delete_Desire(login_email,desire_id):
    mycursor.execute("SELECT desire_id From Desire Where desire_email = %s And desire_id = %s",[login_email,desire_id])

    check_desire = mycursor.fetchone()

    if check_desire:
        mycursor.execute("Delete From Desire Where desire_email = %s And desire_id = %s",[login_email,desire_id] )
        db.commit()




# # ---------- PREFERENCE HELPERS ----------

# def get_preference(login_email: str):
#     mycursor.execute("SELECT language, font_size, theme FROM Preference WHERE login_email = %s", (login_email,))
#     row = mycursor.fetchone()
#     if not row:
#         return {"language": "English", "font_size": 100, "theme": "system"}
#     return {"language": row[0] or "English",
#             "font_size": int(row[1] or 100),
#             "theme": (row[2] or "system").lower()}

# def upsert_preference(login_email: str, language=None, font_size=None, theme=None):
#     mycursor.execute("SELECT language, font_size, theme FROM Preference WHERE login_email = %s", (login_email,))
#     row = mycursor.fetchone()
#     if row:
#         cur_language = language if language is not None else row[0]
#         cur_font_size = font_size if font_size is not None else row[1]
#         cur_theme = theme if theme is not None else row[2]
#         mycursor.execute(
#             "UPDATE Preference SET language=%s, font_size=%s, theme=%s WHERE login_email=%s",
#             (cur_language, cur_font_size, cur_theme, login_email)
#         )
#     else:
#         mycursor.execute(
#             "INSERT INTO Preference (language, font_size, theme, login_email) VALUES (%s,%s,%s,%s)",
#             (language or "English", font_size or 100, (theme or "system").lower(), login_email)
#         )
#     db.commit()

"""

# Sample Select Staement
# Trying to find username and password from password storage
def select_password_storage(email,password):

    find_username = mycursor.execute("Select email, password from Password_Storage Where email = %s",[email])

    if find_username:
        for x in find_username:
            retrieve_email = x[0]
            stored_password = x[1]

        # write validation here
        if login_password != stored_password:
                message2 = "The email or password you entered is incorrect"
                return render_template('login.html',form=login_form,message ="",message2=message2)
        else:
            return redirect(url_for('verify_otp'))


    elif not find_username:
        find_admin = mycursor.execute("Select email, password from Admin_Password_Storage Where email = %s",[email])
        if find_admin:
            for x in find_admin:
                retrieve_admin_email = x[0]
                stored_password = x[1]

            if login_password != stored_password:
                message2 = "The email or password you entered is incorrect"
                return render_template('login.html',form=login_form,message ="",message2=message2)
            else:
                return redirect(url_for('verify_otp'))
            

        
    else:
        message2 = "The email or password you entered is incorrect"
        return render_template('login.html',form=login_form,message ="",message2=message2)


"""
    






