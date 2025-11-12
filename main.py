import random
import string
from flask import Flask, render_template, redirect, request
import mysql.connector

app = Flask(__name__)


def get_db():
    return mysql.connector.connect(
        host="localhost",           
        user="root",     
        password="123456", 
        database="url_shortener"    
    )


def generateshorturl(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        long_url = request.form['long_url'].strip()
        custom_code = request.form.get('custom_code', '').strip()
        short_url = custom_code if custom_code else generateshorturl()

        db = get_db()
        cursor = db.cursor()

        
        cursor.execute("SELECT id FROM urls WHERE short_code = %s", (short_url,))
        while cursor.fetchone():
            if custom_code:
                return " Custom code already taken. Try another.", 400
            short_url = generateshorturl()
            cursor.execute("SELECT id FROM urls WHERE short_code = %s", (short_url,))

        
        cursor.execute(
            "INSERT INTO urls (short_code, long_url, click_count) VALUES (%s, %s, %s)",
            (short_url, long_url, 0)
        )
        db.commit()

        return render_template(
            "shortened.html",
            short_url=f"{request.url_root}{short_url}",
            click_count=0
        )

    return render_template("index.html")


@app.route("/<short_url>")
def redirecturl(short_url):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT long_url, click_count FROM urls WHERE short_code = %s", (short_url,))
    result = cursor.fetchone()

    if result:
        new_count = result['click_count'] + 1
        cursor.execute("UPDATE urls SET click_count = %s WHERE short_code = %s", (new_count, short_url))
        db.commit()
        return redirect(result['long_url'])
    else:
        return " URL not found", 404


if __name__ == "__main__":
    app.run(debug=True)