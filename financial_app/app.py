from flask import Flask , render_template ,request,session,redirect,url_for
from flask_mysqldb import MySQL
from flask_mail import Mail,Message

app = Flask(__name__)

app.config['MYSQL_HOST'] = "remotemysql.com"
app.config['MYSQL_USER'] = '#user_id'
app.config['MYSQL_PASSWORD'] = '#db_password'
app.config['MYSQL_DB'] = '#db_name'

app.config["MAIL_SERVER"] = 'smtp.gmail.com'
app.config['MAIL_PORT']=465
app.config['MAIL_USERNAME']="#Email"
app.config['MAIL_PASSWORD']=  "#password"
app.config["MAIL_USE_TLS"]= False
app.config["MAIL_USE_SSL"]=True
mail1 = Mail(app)


app.secret_key = 'a'
mysql = MySQL(app)


@app.route('/')
def home():
    return render_template("home.html")

@app.route('/signup1')
def signup1():
    return render_template("sign_up.html")

@app.route('/login1',methods=['POST','GET'])
def login1():
    return render_template("login.html")


@app.route('/signup',methods=['POST'])
def signup():
    msg = ''
    if(request.method=="POST"):
        name  =request.form["username"]
        email  =request.form["email"]
        work = request.form["work"]
        mobile = request.form["mobile"]
        address = request.form["address"]
        pass1 = request.form["password1"]
        pass2 = request.form["password2"]
        a1 = [name,email,mobile,work,address]
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE email= %s', (email,))
        email_info = cursor.fetchone()

        if(email_info!=None):
            msg="Email Already Exists"
        elif(pass1!=pass2):
            msg="Password doesn't Match"
        else:
            cursor.execute('INSERT INTO users VALUES (NULL, % s, % s, %s, % s, % s,%s)', (str(name), str(email),str(mobile),str(work),str(address),str(pass1)))
            msg = 'You have successfully registered !'
        mysql.connection.commit()
    return render_template('sign_up.html', msg = msg)



@app.route('/login',methods=['POST'])
def login():
    msg = ''
    if(request.method=="POST"):
        email  =request.form["email"]
        session["email"]=email
        password = request.form["password"]
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE email= %s', (str(email),))
        email_info = cursor.fetchone()
        cursor1 = mysql.connection.cursor()
        cursor1.execute('SELECT * FROM users WHERE email= %s AND password= %s', [str(email),str(password)])
        email_pass_info = cursor1.fetchone()
        mysql.connection.commit()
        if(email_info==None):
            msg="Email dosen't Exists"
            return render_template('login.html',msg1=msg)
        elif(email_pass_info==None):
            msg="Password is incorrect"
            return render_template('login.html',msg1=msg)
        else:
            cursor2 = mysql.connection.cursor()
            cursor4 = mysql.connection.cursor()
            cursor5 = mysql.connection.cursor()
            print(session['email'])
            cursor2.execute('SELECT * FROM exp WHERE email = %s',[session['email']])
            cursor4.execute('SELECT sum(expense) FROM exp  WHERE email = %s',[session['email']])
            cursor5.execute('SELECT  * FROM limits  WHERE email = %s',[session['email']])
            amount = cursor4.fetchall()
            account = cursor2.fetchall()
            limits1 =cursor5.fetchall()
            flag=1
            if(None in amount[0]):
                print("yes--------------------------------------------------yes")
                flag=0
            print("Limits: Amount :",limits1,len(amount),amount,account)

            if(None in amount[0]):
                return render_template('main.html')
            print("Limits: Amount :",limits1,len(amount),amount,account)

            if(len(limits1)==0):
                print("-------------------------------------------------------------------------------------------------------------")
                print("account : ",account)
                if(account!=None or flag):
                    return render_template('main.html',pred = account,amount="Total Amount : "+str(*amount[0])+" Rs")
                else:
                    return render_template('main.html')
            elif(float(limits1[-1][-1])<float(amount[0][0])):
                message = Message("Expenses Reminder",sender="#Email",recipients=[session['email']])
                message.body = "This Email is To Intemiate You that your expenses raises its limits. That is your prefeered limits are "+str(limits1[-1][-1])+". But the Total amount spend was "+str(amount[0][0])+" Thank you"
                mail1.send(message)

            mysql.connection.commit()
            # print("accountdislay",account)
            # session.__exit__
            if(account==None or amount[0][0]==None):
                return render_template('main.html')
            return render_template('main.html',pred = account,amount="Total Amount : "+str(*amount[0])+" Rs")
    

@app.route('/display',methods=['POST','GET'])
def display():
    if(request.method=='POST'):
        type1 = request.form["type"]
        exp = request.form["exp"]
        description = request.form["description"]

        cursor2 = mysql.connection.cursor()
        cursor3 = mysql.connection.cursor()
        cursor4 = mysql.connection.cursor()
        cursor5 = mysql.connection.cursor()
        print(session['email'])
        cursor2.execute('INSERT INTO exp VALUES(NULL, %s,%s,%s,%s)',[session['email'],str(type1),str(exp),str(description)])
        mysql.connection.commit()
        cursor3.execute('SELECT * FROM exp WHERE email = %s',[session['email']])
        cursor4.execute('SELECT sum(expense) FROM exp  WHERE email = %s',[session['email']])
        cursor5.execute('SELECT * FROM limits  WHERE email = %s',[session['email']])
        account = cursor3.fetchall()   
        amount = cursor4.fetchall()
        limits1 = cursor5.fetchall() 
        # print(limits1[-1][-1],amount[0][0])
        flag=1
        if(None in amount[0]):
                print("yes")
                flag=0
        if(None in amount[0]):
                return render_template('main.html')
        if(len(limits1)==0):
            if(account!=None or flag):
                return render_template('main.html',pred = account,amount="Total Amount : "+str(*amount[0])+" Rs")
            else:
                return render_template('main.html')
        elif(float(limits1[-1][-1]) < float(amount[0][0])):
            message = Message("Expenses Reminder",sender="#Email",recipients=[session['email']])
            message.body = "This Email is To Intemiate You that your expenses raises its limits. That is your prefeered limits are "+str(limits1[-1][-1])+". But the Total amount spend was "+str(amount[0][0])+" Thank you"
            mail1.send(message)
        mysql.connection.commit()
        if(account==None or amount[0][0]==None):
            return render_template('main.html')
        return render_template('main.html',pred = account,amount="Total Amount : "+str(*amount[0])+" Rs")

@app.route('/display1',methods=['post','Get'])
def display1():
    if(request.method=='POST'):
        limit = request.form["limit"]
        cursor2 = mysql.connection.cursor()
        print(limit)
        cursor2.execute('INSERT INTO limits VALUES(NULL, %s,%s)',[session['email'],str(limit)])
        mysql.connection.commit()
        cursor3 = mysql.connection.cursor()
        cursor4 = mysql.connection.cursor()
        cursor5 = mysql.connection.cursor()
        print(session['email'])
        cursor3.execute('SELECT * FROM exp WHERE email = %s',[session['email']])
        cursor4.execute('SELECT sum(expense) FROM exp  WHERE email = %s',[session['email']])
        cursor5.execute('SELECT * FROM limits  WHERE email = %s',[session['email']])
        account = cursor3.fetchall()   
        amount = cursor4.fetchall()
        limits1 = cursor5.fetchall() 
        mysql.connection.commit()
        if(None in amount[0]):
                print("yes")
                flag=0
        if(None in amount[0]):
                return render_template('main.html')
        if(len(limits1)==0):
            if(account!=None or flag):
                return render_template('main.html',pred = account,amount="Total Amount : "+str(*amount[0])+" Rs")
            else:
                return render_template('main.html')
        elif(float(limits1[-1][-1])<float(amount[0][0])):
            message = Message("Expenses Reminder",sender="#Email",recipients=[session['email']])
            message.body = "This Email is To Intemiate You that your expenses raises its limits. That is your prefeered limits are "+str(limits1[-1][-1])+". But the Total amount spend was "+str(amount[0][0])+" Thank you"
            mail1.send(message)
        mysql.connection.commit()
        if(account==None or amount[0][0]==None):
            return render_template('main.html')
        return render_template('main.html',pred = account,amount="Total Amount : "+str(*amount[0])+" Rs")


@app.route('/delete',methods=['post','Get'])
def delete():
    if(request.method=='POST'):
        cursor = mysql.connection.cursor()
        cursor.execute('DELETE  FROM exp WHERE email= %s',(session['email'],))
        mysql.connection.commit()
        return render_template('main.html')

@app.route('/logout',methods=['post','Get'])
def logout():
    session.__exit__
    return render_template("home.html")


if __name__=="__main__":
    app.run(host="0.0.0.0",debug=True,port=8080)
    