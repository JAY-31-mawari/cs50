from flask import Flask,request,render_template,redirect,session
from flask_session import Session
from cs50 import SQL

app=Flask(__name__)
app.config["SESSION_PERMANENT"]=False
app.config["SESSION_TYPE"]="filesystem"
Session(app)

db=SQL("sqlite:///show.db")
user_name="user"
ID=0

@app.route("/")
def greet():
    if not session.get("name"):
        return redirect("/login")
    return redirect("/index")
   
@app.route("/login",methods=["POST","GET"])
def login():
    if request.method == "POST":
        global user_name
        global ID
        ID+=1
        user_name=request.form.get("name")
        password=request.form.get("password")
        encrpt_password=""
        for char in password.upper():
            asci=ord(char)
            encrpt_password=encrpt_password+str(asci)
        session["name"]=user_name
        db.execute("INSERT INTO LOGIN VALUES(?,?,?)",ID,user_name,encrpt_password)
        return redirect("/")
    return render_template("login.html")

@app.route("/index")
def index():
    if not session.get("name"):
        return redirect("/error")
    return render_template("index.html")

@app.route("/error")
def error():
    return render_template("error.html",message=user_name)

@app.route("/search")
def search():
    shows=db.execute("SELECT * FROM SHOW WHERE TITLE LIKE ?", "%" + request.args.get("q") + "%")
    return render_template("search.html",shows=shows)

@app.route("/logout")
def logout():
    session["name"]=None
    return redirect("/index")

@app.route("/deregister",methods=["POST"])
def deregister():
    user_id=request.form.get("id")
    db.execute("DELETE FROM LOGIN WHERE id=?",user_id)
    return None

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/registrants" ,methods=["POST"])
def registrants():
    admin_name=request.form.get("admin_name")
    admin_password=request.form.get("admin_password")
    REGISTER=db.execute("SELECT names FROM register")
    AUTHORIZED_USERS=[]
    for admins in REGISTER:
        AUTHORIZED_USERS.append(admins["names"])
    if admin_name in AUTHORIZED_USERS and admin_password=="1234":
        name=db.execute("SELECT * FROM LOGIN")
        return render_template("registrants.html",names=name)
    return redirect("/")

def decrypt(num):
    j=1
    text=""
    num2=0
    num1=0
    i=0
    while(num):
        i+=1
        num2=num%10
        num=num//10
        num2*=j
        num1=num2+num1
        j*=10
        if i%2 == 0:
            text=str(chr(num1))+text
            num1=0
            j=1

    return text

@app.route("/hacker")
def hackdecrypt():
    login=db.execute("SELECT * FROM LOGIN")
    for word in login:
        text=word["password"]
        value=decrypt(int(text))
        db.execute("INSERT INTO decrypt VALUES(?,?,?)",word["id"],word["name"],value)
    password=db.execute("SELECT * FROM DECRYPT")
    return render_template("decrpyt.html",passwords=password)