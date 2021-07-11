import base64
from email import message
import email
import re
from flask import Flask,render_template,request,redirect
from flask.helpers import url_for  
from matplotlib.figure import Figure
from io import BytesIO
import mysql.connector
from datetime import date, timedelta
import matplotlib.pyplot as plt
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText 

app = Flask(__name__)   
app.static_folder = 'static'
def sendEmail(receiver_address,subject,message):
    mail_content = message
    sender_address = 'tracknetworkmd@gmail.com'
    sender_pass = 'InformationTechnology'
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = subject
    message.attach(MIMEText(mail_content, 'plain'))
    session = smtplib.SMTP('smtp.gmail.com', 587) 
    session.starttls() 
    session.login(sender_address, sender_pass) 
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()
    print('Mail Sent')
def for_pi():
    mydb = mysql.connector.connect(host="localhost",user="root",password="linux")
    mycursor = mydb.cursor()
    mycursor.execute("use coronadatabase")
    data={}
    mycursor.execute("select sum(confirmed_case),sum(cured_case),sum(deaths) from coronacase;")
    a=mycursor.fetchall()
    data["type"]="count"
    data["confirmed"]=int(a[0][0])
    data["cured"]=int(a[0][1])
    data["deaths"]=int(a[0][2])
    return data
@app.route('/',methods=['GET','POST'])   
def home(): 
    heading=["S.no","State","Confirmed","Cured","Deaths"]
    data = read_from_sql("total_report","")
    pi=""
    chart=[]
    if request.method=="POST":
        state=request.form["state"]
        chart =read_from_sql("coronacase","state_name='"+state+"'")
    pi=for_pi()
    return render_template('index.html',heading=heading,data=data,chart=chart,pi=pi) 

@app.route('/insert',methods=['GET','POST'])
def insert():
    data=""
    if request.method=="POST" and len(request.form["name"])>1:
        name=request.form["name"]
        phonenumber=request.form["phonenumber"]
        age=request.form["age"]
        email=request.form["email"]
        address=request.form["address"]
        city=request.form["city"]
        state=request.form["state"]
        booked_date = (date.today())
        scheduled_date=str(booked_date+timedelta(10))
        booked_date=str(booked_date)
        l=[name,phonenumber,age,email,address,city,state,scheduled_date,booked_date]
        r=insert_into_sql("webdata",l,True)
        data="Your appointment is on "+scheduled_date+" your unique ID :"+str(r)
        sendEmail(email,"New vaccination Booking from TrackNetworkMD",data)
        data="Details sent to your Email!"
    return render_template('insert.html',data=data)

@app.route('/signin',methods=["GET","POST"])
def signin():
    data=""
    if request.method=="POST":
        email=request.form["email"]
        password=request.form["password"]
        data=read_from_sql("userlogindetails","email='"+email+"' and password='"+password+"'")
        if len(data)==0:
            data="Incorrect email or password"
        else:
            return redirect("/")
    return render_template('signin.html',data=data)

@app.route('/search',methods=["POST","GET"])
def search():
    message=""
    email=""
    subject=""
    data=""
    if request.method=="POST":
        id=request.form['ID']
        mydb = mysql.connector.connect(host="localhost",user="root",password="linux")
        mycursor = mydb.cursor()
        mycursor.execute("use coronadatabase")
        mycursor.execute("select * from webdata where appointment_id='"+id+"';")
        l=mycursor.fetchall()
        if(len(l)==0):
            data="No record available"
        else:
            data="Message sent to your registered email!"
            temp=[i for i in l[0]]
            email=temp[3]
            for i in temp:message+=str(i)+" | "
            subject="Your vaccination booking details"
            message="Hi, "+temp[0]+" this is your booking details "+message 
    if len(email)>1:sendEmail(email,subject,message)
    return render_template('search.html',data=data)

def read_from_sql(table,constraint):
    mydb = mysql.connector.connect(host="localhost",user="root",password="linux")
    mycursor = mydb.cursor()
    mycursor.execute("use coronadatabase")
    data=[]

    if len(constraint)<=1:
        mycursor.execute("select * from "+table+";")
        l = mycursor.fetchall()
        r=1
        for i in l:
            a=[r,i[0],int(i[1]),int(i[2]),int(i[3])]
            data.append(a)
            r+=1
    else:
        print("select * from "+table+" where "+constraint+";")
        mycursor.execute("select * from "+table+" where "+constraint+";")
        l = mycursor.fetchall()
        for i in l:
            a = [j for j in i]
            data.append(a)
    return data
    
def insert_into_sql(table,records,flag):
    mydb = mysql.connector.connect(host="localhost",user="root",password="linux")
    mycursor = mydb.cursor()
    mycursor.execute("use coronadatabase")
    s=""
    r=""
    if flag==True:
        s=record(records[:-2])
        r=hash(records[1])
        s+=",'"+records[-2]+"',"+"'"+records[-1]+"','"+str(r)+"'"
    else:
        s = record(records)
    print("insert into "+table+" values("+s+")")
    mycursor.execute("insert into "+table+" values("+s+");")
    mydb.commit()
    return r
@app.route("/signup",methods=["POST","GET"])
def signup():
    data=""
    if request.method=="POST":
        name=request.form["name"]
        email=request.form["email"]
        password=request.form["password"]
        record=[name,password,email]
        insert_into_sql("userlogindetails",record,False)
        data="Account created!"
        return redirect("/")
    return render_template("signup.html",data=data)
def record(records):
    s="'"
    s+="','".join(records)
    s+="'"
    return s;
if __name__ =='__main__':

    app.run(debug = True)