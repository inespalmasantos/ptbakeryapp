from app import app, db
from flask_script import Manager, prompt_bool
from flask_migrate import Migrate, MigrateCommand

manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)


@manager.command
def init_db():
    db.create_all()
    print 'Initialized the database'


@manager.command
def drop_db():
    if prompt_bool("Are you sure you want to loose all the data"):
        db.drop_all()
        print 'Dropped the databse'


if __name__ == '__main__':
    manager.run()
