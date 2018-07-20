from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app import create_app
from app.ext import db
from instance.config import SQLALCHEMY_DATABASE_URI

app = create_app()
app.config[SQLALCHEMY_DATABASE_URI] = 'mysql://root:root@127.0.0.1:3306/firefighting'
#db = SQLAlchemy()
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()