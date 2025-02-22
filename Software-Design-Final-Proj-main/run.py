from static import app,db
from flask import Flask,render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from static.admin import admin

if __name__ == "__main__":
    with app.app_context(): #create the database, if not already created
        db.create_all()
    
    admin.init_app(app)

    app.run(host="0.0.0.0", port=8080, threaded=True, debug=True)