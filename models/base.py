from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Application(db.Model):
    __tablename__ = 'applications'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    mode = Column(String(50), default='completion')  # completion or chat
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    prompts = relationship('Prompt', back_populates='application')
    datasets = relationship('Dataset', back_populates='application')

class Prompt(db.Model):
    __tablename__ = 'prompts'
    
    id = Column(Integer, primary_key=True)
    application_id = Column(Integer, ForeignKey('applications.id'))
    name = Column(String(255))
    content = Column(Text, nullable=False)
    type = Column(String(50))  # system, user, assistant
    created_at = Column(DateTime, default=datetime.utcnow)
    application = relationship('Application', back_populates='prompts')

class Dataset(db.Model):
    __tablename__ = 'datasets'
    
    id = Column(Integer, primary_key=True)
    application_id = Column(Integer, ForeignKey('applications.id'))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    data_type = Column(String(50))  # text, qa, conversation
    created_at = Column(DateTime, default=datetime.utcnow)
    application = relationship('Application', back_populates='datasets')
    documents = relationship('Document', back_populates='dataset')

class Document(db.Model):
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True)
    dataset_id = Column(Integer, ForeignKey('datasets.id'))
    name = Column(String(255))
    content = Column(Text)
    metadata = Column(JSON)
    embedding_model = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    dataset = relationship('Dataset', back_populates='documents')

class Tool(db.Model):
    __tablename__ = 'tools'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    type = Column(String(50))  # api, python, shell
    config = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
