from flask import Blueprint, render_template, request, jsonify, redirect, url_for, Flask, session
from flask_login import login_required, current_user
import pandas as pd
import os.path
import matplotlib.pyplot as plt
import json
import razorpay
main = Blueprint('main', __name__)


razorpay_client = razorpay.Client(auth=("rzp_test_eTLJcDvEJdeU2G", "a2TS4HG8wpO84TuiPZHiG0CR"))
from project.models import User
from run import db

    
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


@main.route('/Community_Forums', methods=['GET', 'POST'])
def Community_Forums():
    return render_template("Community_Forums.html")




@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)





@main.route('/Home', methods=['GET'])
def welcome_page():
    return render_template("welcome_page.html")




@main.route('/Home', methods=['GET', 'POST'])
@login_required
def upload_file():
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
    df1= df[(df['Transaction Type'] == 'MFNShipment')]
    Refund= df[(df['Transaction Type'] == 'Refund')]
    Cancel= data[['Order Id', 'Transaction Type', 'Ship To State', 'Total Tax Amount']]
    Cancel = Cancel.astype({"Transaction Type":'category'})
    Cancel= Cancel[(Cancel['Transaction Type'] == 'Cancel')]
    dfb= Refund.groupby(['Ship To State', 'percent']).agg({'Total Tax Amount': ['sum']})
    dfb= dfb.dropna
  
    dfa= df1.groupby(['Ship To State', 'percent']).agg({'Total Tax Amount': ['sum']})
    dfa= dfa.dropna
    print(dfb)
    states= pd.DataFrame(df1['Ship To State'].unique()) 
    totalTax= df1.agg({'Total Tax Amount': ['sum']})
    
    dfc= df1.groupby(['Ship To State']).agg({'Total Tax Amount': ['sum']})
    data= states.to_dict('index')
    return render_template("predata.html", tables=[states.to_html(classes='data', header=False)], titles = ['na', 'you have to file GSTR 1 for these states'], totalTax=totalTax, data=data) 

@main.route('/data', methods= ['GET', 'POST'])
def datae():
    dfd= pd.read_csv(session.get('gst'))
    gstin= dfd['Seller Gstin'].iloc[0]
    df= dfd[['Transaction Type', 'Ship To State', 'Tax Exclusive Gross', 'Total Tax Amount']]
    df['percent']= (df['Total Tax Amount']*100)/df['Tax Exclusive Gross']
    df['percent'].fillna(0)
    df['percent'] = df['percent'].round(0)
    df['percent']= df['percent'].fillna(0)
    df['percent']= df['percent'].astype(int)
    df['Total Tax Amount'] = df['Total Tax Amount'].astype('int64')
    df = df.astype({"Transaction Type":'category'})
    df1= df[(df['Transaction Type'] == 'MFNShipment')]
    Refund= df[(df['Transaction Type'] == 'Refund')]
    Cancel= df[(df['Transaction Type'] == 'Canel')]
    dfa= df1.groupby(['Ship To State', 'percent']).agg({'Total Tax Amount': ['sum']})
    dfa_html= dfa.to_html()
    Refund_html= Refund.to_html()
    Cancel_html= Cancel.to_html()
    return render_template("data.html", tables=[dfa_html, Refund_html, Cancel_html], titles = ['na', 'you have to file GSTR 1 for these states', 'Your Refunds', 'Your Cancelled Order Data'])




  #  dfa.to_sql('taxData', con=engine, if_exists='replace')
   # engine.execute("SELECT * FROM taxData").fetchall()

   
