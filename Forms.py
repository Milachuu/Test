from wtforms import Form,StringField,SelectField,TextAreaField,validators,PasswordField,ValidationError
from wtforms.fields import EmailField,FileField



def strong_password(form, field):
    password = field.data
    if len(password) < 7:
        raise ValidationError("Password must be at least 7 characters long.")
    if not any(c.islower() for c in password):
        raise ValidationError("Password must contain at least one lowercase letter.")
    if not any(c.isupper() for c in password):
        raise ValidationError("Password must contain at least one uppercase letter.")
    if not any(c.isdigit() for c in password):
        raise ValidationError("Password must contain at least one digit.")


# If something is broken here for login, just remove the strong function on line 24

class CreateUserForm(Form): 
    first_name = StringField('First Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    last_name = StringField('Last Name', [validators.Length(min=1, max=150), validators.DataRequired()]) 
    email = EmailField('Email', [validators.Email(), validators.DataRequired()])
    password1 = PasswordField('Password',[validators.Length(min=7),validators.DataRequired(),strong_password,validators.equal_to('password2',message="Passwords does not match")])
    password2 = PasswordField('Password (Confirm)',[validators.Length(min=7),validators.DataRequired()])

class CreateUserInfo(Form): 
    username = StringField('Username',[validators.Length(min=3,max=25),validators.DataRequired()])
    gender = SelectField('Gender', [validators.DataRequired()], choices=[('', 'Select'), ('Female', 'Female'), ('Male', 'Male'),('Other', 'Other')], default='') 
    postal_code = StringField('Postal Code', [validators.Length(min=6,max=6), validators.DataRequired()])
    email = EmailField('Email', [validators.Email(), validators.DataRequired()])
    phone_number = StringField('Phone Number', [validators.DataRequired()])
    bio = TextAreaField('Bio', [validators.Optional()]) 

class Login(Form):
    email = EmailField('Email', [validators.Email(), validators.DataRequired()],render_kw={"placeholder":" Enter your email"})
    password = PasswordField('Password',[validators.Length(min=7)],render_kw={"placeholder":" Enter your password"})

class Update(Form):
    email = EmailField('Email', [validators.Email(), validators.DataRequired()])

class Wishlist(Form):

    item = StringField('Item', [validators.Length(min=1, max=150), validators.DataRequired()])
    description = TextAreaField('Description', [validators.Optional()])
   

class Reporting(Form):
    report_email = EmailField('User Email you wish to report', [validators.Email(), validators.DataRequired()])
    report_option = SelectField('Reasons', [validators.DataRequired()], choices=[('', 'Select'), ('Inappropriate Messages', 'Inappropriate messages'), ('Violation of Policies', 'Violation of Policies'),('other','other')], default='')
    report_other = TextAreaField('If you chose others, please write the reason here: ',[validators.length(max=200),validators.Optional()],default="")
    report_description = TextAreaField('Description', [validators.DataRequired()])


