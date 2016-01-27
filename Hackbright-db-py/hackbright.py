"""Hackbright Project Tracker.

A front-end for a database that allows users to work with students, class
projects, and the grades students receive in class projects.

Author: Shai Wilson, Shijie Feng
"""
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def connect_to_db(app):
    """Connect the database to our Flask app."""

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///hackbright'
    db.app = app
    db.init_app(app)


def get_student_by_github(github):
    """Given a github account name, print information about the matching student."""

    QUERY = """
        SELECT first_name, last_name, github
        FROM Students
        WHERE github = :github
        """
    db_cursor = db.session.execute(QUERY, {'github': github})
    row = db_cursor.fetchone()
    print "Student: %s %s\nGithub account: %s" % (row[0], row[1], row[2])


def make_new_student(first_name, last_name, github):
    """Add a new student and print confirmation.

    Given a first name, last name, and GitHub account, add student to the
    database and print a confirmation message.
    """

    QUERY = """
            INSERT INTO students VALUES (:first_name, :last_name, :github)
    """

    db_cursor = db.session.execute(QUERY, {'first_name': first_name, 'last_name': last_name,
                                            'github': github})

    db.session.commit()

    print "Successfully added student: %s %s" % (first_name, last_name)


def get_project_by_title(title):
    """Given a project title, print information about the project."""

    QUERY = """SELECT description FROM projects WHERE title = :title"""
    db_cursor = db.session.execute(QUERY, {'title': title})
    result = db_cursor.fetchone()

    print "Successfully query project by title: %s description: %s" % (title, result)

def get_grade_by_github_title(github, title):
    """Print grade student received for a project."""
    
    QUERY = """
        SELECT grade
        FROM grades
        JOIN students ON (student_github = github)
        JOIN projects ON (project_title = title) 
        WHERE github = :github AND title = :title
    """

    db_cursor = db.session.execute(QUERY, {'github': github, 'title': title})
    result = db_cursor.fetchone()

    print "Successfully query %s given github name %s and project title %s." % (
            result[0], github, title) 


def assign_grade(github, title, grade):
    """Assign a student a grade on an assignment and print a confirmation."""
    QUERY = """
            UPDATE grades SET grade = :grade
            WHERE student_github = :github AND project_title = :title
    """

    db_cursor = db.session.execute(QUERY, {'github': github, 'title': title,
                                            'grade' : grade})
    result = db_cursor.fetchone()
    print result

    print "Successfully update student %s project %s grade to %s" % (github,
                                                                       title,
                                                                       result)


def handle_input():
    """Main loop.

    Repeatedly prompt for commands, performing them, until 'quit' is received as a
    command."""

    command = None

    while command != "quit":
        input_string = raw_input("HBA Database> ")
        tokens = input_string.split()
        command = tokens[0]
        args = tokens[1:]

        if command == "student":
            github = args[0]
            get_student_by_github(github)

        # expected : project_name Markov
        # output : get_project_by_title
        elif command == "project_name":
            project_name = args[0]
            get_project_by_title(project_name)

        elif command == "get_grade":
            github = args[0]
            title = args[1]
            get_grade_by_github_title(github, title)

        elif command == "assign_grade":
            github = args[0]
            title = args[1]
            grade = args[2]
            assign_grade(github, title, grade)

        elif command == "new_student":
            first_name, last_name, github = args   # unpack!
            make_new_student(first_name, last_name, github)

        else:
            if command != "quit":
                print "Invalid Entry. Try again."


if __name__ == "__main__":
    app = Flask(__name__)
    connect_to_db(app)

    handle_input()

    db.session.close()
