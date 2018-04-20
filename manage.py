#!.venv/bin/python


import os
import unittest
import coverage
import logging

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask import request, url_for, Response, jsonify, g
import urllib

COV = coverage.coverage(
    branch=True,
    include=['mlapi/*', 'models/*', 'tests/*'],
    omit=[
        'tests/*',
        'mlapi/datadbbase/config.py',
        '*/__init__.py'
    ]
)
COV.start()

from mlapi.app import app, database
from db import dbModels as models


migrate = Migrate(app, database)
manager = Manager(app)

# migrations
manager.add_command('database', MigrateCommand)


@manager.command
def test():
    """Runs the unit tests without test coverage."""
    tests = unittest.TestLoader().discover('tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=3).run(tests)
    if result.wasSuccessful():
        return 0
    return 1

@manager.command
def list_routes():
    import urllib
    output = []
    for rule in app.url_map.iter_rules():

        options = {}
        for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)

        methods = ','.join(rule.methods)
        url = url_for(rule.endpoint, **options)
        line = urllib.parse.unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, url))
        output.append(line)

    for line in sorted(output):
        print(line)

@manager.command
def cov():
    """Runs the unit tests with coverage."""
    tests = unittest.TestLoader().discover('tests')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()
        return 0
    return 1


@manager.command
def create_db():
    """Creates the database tables."""
    database.create_all()


@manager.command
def drop_db():
    """Drops the database tables."""
    database.drop_all()


if __name__ == '__main__':
    manager.run()
