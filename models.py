import os
from sqlalchemy import Column, String, Integer, create_engine, ForeignKey
from flask_sqlalchemy import SQLAlchemy
import json
from flask_migrate import Migrate


db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''


def setup_db(app):
    app.config.from_object('config')
    db.app = app
    db.init_app(app)
    migrate = Migrate(app, db)
    return db

'''
Stage

'''


class Grade(db.Model):
    __tablename__ = 'Grade'

    id = Column(Integer, primary_key=True, autoincrement=True)
    num = Column(Integer)
    semesters = db.relationship('Semester', backref=db.backref('grade_S', uselist=False), lazy='dynamic')
    modules = db.relationship('Module', backref=db.backref('grade_M', uselist=False), lazy='dynamic')

    def __init__(self, num):
        self.num = num

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        
    def format(self):
        return {
            'id': self.id,
            'stage_num': self.num
        }
        

'''
Semester

'''


class Semester(db.Model):
    __tablename__ = 'Semester'

    id = Column(Integer, primary_key=True, autoincrement=True)
    num = Column(Integer)
    grade_id = Column(Integer, ForeignKey('Grade.id'), nullable=False)
    modules = db.relationship('Module', backref=db.backref('semester', uselist=False), lazy='dynamic')

    def __init__(self, num, grade_id):
        self.num = num
        self.grade_id = grade_id

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        
    def format(self):
        return {
            'id': self.id,
            'grade_id': self.grade_id,
            'semester_num': self.num
        }
        

'''
Module

'''


class Module(db.Model):
    __tablename__ = 'Module'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    grade_id = Column(Integer, ForeignKey('Grade.id'), nullable=False)
    semester_id = Column(Integer, ForeignKey('Semester.id'), nullable=False)
    mcqs = db.relationship('MCQ', backref=db.backref('module', uselist=False), lazy='dynamic')

    def __init__(self, name, grade_id, semester_id):
        self.name = name
        self.grade_id = grade_id
        self.semester_id = semester_id

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        
    def format(self):
        return {
            'id': self.id,
            'grade_id': self.grade_id,
            'semester_id': self.semester_id,
            'name': self.name
        }
        

'''
MCQ

'''


class MCQ(db.Model):
    __tablename__ = 'MCQs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    question = Column(String, nullable=False)
    choice_A = Column(String, nullable=False)
    choice_B = Column(String, nullable=False)
    choice_C = Column(String, nullable=False)
    choice_D = Column(String, nullable=False)
    choice_E = Column(String)
    answer = Column(String, nullable=False)
    module_id = Column(Integer, ForeignKey('Module.id'), nullable=False)

    def __init__(self, question, choice_A, choice_B, choice_C, choice_D, choice_E, answer, module_id):
        self.question = question
        self.choice_A = choice_A
        self.choice_B = choice_B
        self.choice_C = choice_C
        self.choice_D = choice_D
        self.choice_E = choice_E
        self.answer = answer
        self.module_id = module_id

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'question': self.question,
            'choice_A': self.choice_A,
            'choice_B': self.choice_B,
            'choice_C': self.choice_C,
            'choice_D': self.choice_D,
            'choice_E': self.choice_E,
            'answer': self.answer,
            'module_id': self.module_id
        }
