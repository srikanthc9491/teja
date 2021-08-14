from flask_wtf import Form, TextField, TextAreaField, SubmitField, validators, ValidationError
 
class ContactForm(Form):
  name = TextField("Name",  [validators.Required("Please enter your name.")])
  email = TextField("Email",  [validators.Required("Please enter your email address."), validators.Email("Please enter your email address.")])
  subject = TextField("Subject",  [validators.Required("Please enter a Subject title for us to understand.")])
  message = TextAreaField("Message",  [validators.Required("Please enter the complete message.")])
  submit = SubmitField("Send")
