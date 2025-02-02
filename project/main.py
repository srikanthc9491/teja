from flask import Blueprint, render_template, request, jsonify, redirect, url_for, Flask, session, flash
from flask_login import login_required, current_user
import pandas as pd
from flask import app
import os.path
import matplotlib.pyplot as plt
import json
import razorpay
from project.forms import ContactForm
from flask_mail import Message, Mail
main = Blueprint('main', __name__)


razorpay_client = razorpay.Client(auth=("rzp_test_eTLJcDvEJdeU2G", "a2TS4HG8wpO84TuiPZHiG0CR"))
from project.models import User
from run import mail, db



    
@main.route('/predata', methods= ['GET', 'POST'])
def app_charge():
    if request.method == "POST":
        return redirect(url_for('main.pay', id=current_user.id))
        
    
    
    
@main.route('/pay/<id>', methods= ['GET', 'POST'])
def pay(id):
    user=User.query.filter_by(id=id).first()
    client= razorpay.Client(auth=("rzp_test_eTLJcDvEJdeU2G", "a2TS4HG8wpO84TuiPZHiG0CR"))
    amount = 10000
    payment= client.order.create({'amount' : int(amount), 'currency' : 'INR', 'payment_capture' : '1'})
    return render_template('pay.html', payment = payment)


@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template("welcome.html")



@main.route('/Resources', methods=['GET', 'POST'])
def Resources():
    return render_template("Resources.html")


@main.route('/Contact_Us', methods=['GET', 'POST'])
def Contact_Us():
    form = ContactForm()
    if request.method == 'POST':
      if form.validate() == False:
        flash('All fields are required.')
        return render_template("Contact_Us.html", form=form)
      else:
        msg = Message(form.subject.data, sender='contact@example.com', recipients=['pavanteja14@gmail.com'])
        msg.body = """
        From: %s &lt;%s&gt;
        %s
        """ % (form.name.data, form.email.data, form.message.data)
        mail.send(msg)
        return render_template('Contact_Us.html', success=True)
    elif request.method == 'GET':
      return render_template("Contact_Us.html", form=form)




@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
   user= current_user
   if user:
               ### flash message to user.
        flash('welcome back. Please login(check remember me to have easy access!')
        return render_template('profile.html', name=current_user.name)
   else:
        flash('please signup to access everything! ')
        return redirect(url_for('auth.signup')) 
    





@main.route('/Home', methods=['GET'])
@login_required
def welcome_page():
    return render_template("welcome_page.html")




@main.route('/Home', methods=['GET', 'POST'])
@login_required
def upload_file():
    b2bfile = request.files['ab']
    if len(b2bfile.filename) >= 2 :
      session["b2b"]=b2bfile.filename
      b2bfile.save(b2bfile.filename)
      Bdata = pd.read_csv(b2bfile.filename)
        
    else:
      pass
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        uploaded_file.save(uploaded_file.filename)
        ## read the csv_file
    session["gst"] = uploaded_file.filename 
    data = pd.read_csv(uploaded_file.filename)
   # session["gst"] = data
    df= data[['Transaction Type', 'Ship To State', 'Tax Exclusive Gross','Total Tax Amount']]
    df['percent']= (df['Total Tax Amount']*100)/df['Tax Exclusive Gross']
    df['percent'] = df['percent'].round(0)
    df['percent']= df['percent'].fillna(0)
    df['percent']= df['percent'].astype(int)
    df['Total Tax Amount'] = df['Total Tax Amount'].astype('int64')
    df = df.astype({"Transaction Type":'category'})
    df1= df[(df['Transaction Type'] != 'Refund') & (df['Transaction Type'] != 'Cancel')]
    Refund= df[(df['Transaction Type'] == 'Refund')]
    Cancel= data[['Order Id', 'Transaction Type', 'Ship To State', 'Total Tax Amount']]
    Cancel = Cancel.astype({"Transaction Type":'category'})
    Cancel= Cancel[(Cancel['Transaction Type'] == 'Cancel')]
    dfb= Refund.groupby(['Ship To State', 'percent']).agg({'Total Tax Amount': ['sum']})
    dfb= dfb.dropna
  
    dfa= df1.groupby(['Ship To State', 'percent']).agg({'Total Tax Amount': ['sum']})
    dfa= dfa.dropna
    print(dfb)
    gstin= data['Seller Gstin'].iloc[0] 
    no_orders= df1['Transaction Type'].count()
    no_refunds= Refund['Transaction Type'].count()
    no_cancel= Cancel['Transaction Type'].count()
    totalSale= df1.agg({'Tax Exclusive Gross': ['sum']})
    totalTax= df1.agg({'Total Tax Amount': ['sum']})
    states= df1[['Ship To State', 'Total Tax Amount']]
    states=dict(states.values)
  #  states= states.set_index('Ship To State').T.to_dict('list')
    statestable= pd.DataFrame(df1['Ship To State'].unique())
    dfc= df1.groupby(['Ship To State']).agg({'Total Tax Amount': ['sum']})
    data= states
    return render_template("predata.html", tables=[statestable.to_html(classes='data', header=False)], titles = ['na', 'you have to file GSTR 1 for these states'], gstin=gstin, no_orders=no_orders, totalTax=totalTax, data=data, no_refunds=no_refunds, no_cancel=no_cancel, totalSale=totalSale) 


@main.route('/data', methods= ['GET', 'POST'])
def datae():
     payment_id = request.args['payment_id']
     if payment_id != '':
        dfd= pd.read_csv(session.get('gst'))
     gstin= dfd['Seller Gstin'].iloc[0]
     add= dfd['Ship To State'] 
     dfw= dfd[['Transaction Type', 'Ship To State','Order Id']]
     sales= dfd[['Transaction Type', 'Ship To State','Order Id', 'Tax Exclusive Gross', 'Total Tax Amount']]
     sales= sales.astype({"Transaction Type":'category'})
     sales= sales[(sales['Transaction Type'] != 'Refund') & (sales['Transaction Type'] != 'Cancel')]
     sale= sales[['Ship To State','Order Id', 'Tax Exclusive Gross', 'Total Tax Amount']]
     df= dfd[['Transaction Type', 'Ship To State', 'Tax Exclusive Gross', 'Total Tax Amount']]
     df['percent']= (df['Total Tax Amount']*100)/df['Tax Exclusive Gross']
     df['percent'].fillna(0)
     df['percent'] = df['percent'].round(0)
     df['percent']= df['percent'].fillna(0)
     df['percent']= df['percent'].astype(int)
     df['Total Tax Amount'] = df['Total Tax Amount'].astype('int64')
     df = df.astype({"Transaction Type":'category'})
     df1= df[(df['Transaction Type'] != 'Cancel')]
     Refund= df[(df['Transaction Type'] == 'Refund')]
     dfw = dfw.astype({"Transaction Type":'category'})
     Cancel= dfw[(dfw['Transaction Type'] == 'Cancel')]
     dfa= df1.groupby(['Ship To State', 'percent']).agg({'Tax Exclusive Gross': ['sum']})
     dfa_html= dfa.to_html()
     sale_html= sale.to_html()
     Refund_html= Refund.to_html()
     Cancel_html= Cancel.to_html()
     no_orders= df1['Transaction Type'].count()
     no_refunds= Refund['Transaction Type'].count()
     no_cancel= Cancel['Transaction Type'].count()
     totalSale= df1.agg({'Tax Exclusive Gross': ['sum']})
     totalTax= df1.agg({'Total Tax Amount': ['sum']})
     
     if 'b2b' in session :   
       bbb= pd.read_csv(session.get('b2b'))
       b2b= bbb[['Customer Bill To Gstid', 'Invoice Number', 'Invoice Date', 'Transaction Type', 'Ship To State', 'Invoice Amount', 'Tax Exclusive Gross', 'Total Tax Amount']]
       b2b= b2b.astype({"Transaction Type":'category'})
       b2b= b2b[(b2b['Transaction Type'] != 'Refund') & (b2b['Transaction Type'] != 'Cancel')]
       b2b['percent']= bbb['Cgst Rate']+bbb['Sgst Rate']+bbb['Utgst Rate']+bbb['Igst Rate']
       tab= b2b[['Invoice Number', 'Customer Bill To Gstid', 'Invoice Date','Ship To State', 'Invoice Amount', 'Tax Exclusive Gross', 'Total Tax Amount','percent']]
       tab.set_index('Invoice Number', inplace=True)
       tab_html= tab.to_html()
       return render_template("data.html", tableb=[tab_html], titleb = ['na', 'Your B2B orders'], tables=[dfa_html, sale_html, Refund_html, Cancel_html], titles = ['na', 'you have to file GSTR 1 for these states', 'Your successful orders', 'Your Refunds', 'Your Cancelled Order Data'], gstin=gstin, no_orders=no_orders, totalTax=totalTax, no_refunds=no_refunds, no_cancel=no_cancel, add=add, totalSale=totalSale)
       session.pop('b2b',None)
     else:
       return render_template("data.html", tables=[dfa_html, sale_html, Refund_html, Cancel_html], titles = ['na', 'you have to file GSTR 1 for these states', 'Your successful orders', 'Your Refunds', 'Your Cancelled Order Data'], gstin=gstin, no_orders=no_orders, totalTax=totalTax, no_refunds=no_refunds, no_cancel=no_cancel, add=add, totalSale=totalSale)
       
     



  #  dfa.to_sql('taxData', con=engine, if_exists='replace')
   # engine.execute("SELECT * FROM taxData").fetchall()

   
