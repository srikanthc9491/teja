from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
import pandas as pd
import os.path


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
    Cancel= data[['Item Description', 'Transaction Type', 'Ship To State', 'Total Tax Amount']]
    Cancel = Cancel.astype({"Transaction Type":'category'})
    Cancel= Cancel[(Cancel['Transaction Type'] == 'Cancel')]
    dfb= Refund.groupby(['Ship To State', 'percent']).agg({'Total Tax Amount': ['sum']})
    dfb= dfb.dropna(0)
  
    dfa= df1.groupby(['Ship To State', 'percent']).agg({'Total Tax Amount': ['sum']})
    dfa= dfa.dropna(0)
    print(dfb)

    return render_template("data.html", tables=[dfa.to_html(classes='data', header=True), Refund.to_html(classes='data', header=True), Cancel.to_html(classes='data', header=True) ], titles = ['na', 'This is Your GSTR-1 Section 7 data', 'Your Refund Data', 'Your Cancellations'])




  #  dfa.to_sql('taxData', con=engine, if_exists='replace')
   # engine.execute("SELECT * FROM taxData").fetchall()

   
