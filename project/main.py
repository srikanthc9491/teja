from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
import pandas as pd
import os.path
import matplotlib.pyplot as plt
import json

main = Blueprint('main', __name__)



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
    data = pd.read_csv(uploaded_file.filename)
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
    states= df1[['Ship To State', 'Total Tax Amount']] 
    States= states.groupby(['Ship To State']) 
    totalTax= df1.agg({'Total Tax Amount': ['sum']})
    
    dfc= data[['Ship To State', 'Total Tax Amount', 'Transaction Type']]
    dfc = dfc.astype({"Transaction Type":'category'})
    dfc= dfc[(dfc['Transaction Type'] == 'MFNShipment')] 
    dfc= dfc[['Ship To State', 'Total Tax Amount']]
    for cols in dfc.columns.tolist()[1:]:
       dfc = dfc.[dfc[cols]>0]


    title = "state wise tax" 
    d = dfc.values.tolist()
    c = dfc.columns.tolist()
    d.insert(0,c)
    pie = json.dumps({'title':title,'data':d})
    
    return render_template("predata.html", tables=[states.to_html(classes='data', header=False)], titles = ['na', 'you have to file GSTR 1 for these states'], totalTax=totalTax, pie=pie) 

    



  #  dfa.to_sql('taxData', con=engine, if_exists='replace')
   # engine.execute("SELECT * FROM taxData").fetchall()

   
