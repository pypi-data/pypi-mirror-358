# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime
from sqlalchemy.orm import relationship, DeclarativeBase, mapped_column


class Base(DeclarativeBase):
    pass

# Junction table for the many-to-many relationship
workflowtool = Table(
    'workflowtool', Base.metadata,
    Column('workflow_id', Integer, ForeignKey('workflow.id'), primary_key=True),
    Column('tool_id', Integer, ForeignKey('tool.id'), primary_key=True)
)

# Model for 'tool' table
class Tool(Base):
    __tablename__ = 'tool'
    
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    name = mapped_column(String(100), nullable=False)
    version = mapped_column(String(100), nullable=False)
    parameter = mapped_column(String(1000), nullable=True)
    database_id = mapped_column(Integer, ForeignKey('tool_database.id'), nullable=True)

    # Define the many-to-many relationship with Workflow through the workflowtool table
    workflows = relationship("Workflow", secondary=workflowtool, back_populates="tools")
    database = relationship("ToolDatabase")

# Model for 'workflow' table
class Workflow(Base):
    __tablename__ = 'workflow'
    
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    name = mapped_column(String(100), nullable=False)
    version = mapped_column(String(100), nullable=False)

    # Define the many-to-many relationship with Tool through the workflowtool table
    tools = relationship("Tool", secondary=workflowtool, back_populates="workflows")
    

class ToolDatabase(Base):
    __tablename__ = 'tool_database'
    
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    name = mapped_column(String(100), nullable=False)
    version = mapped_column(String(100), nullable=False)
    
    
class Process(Base):
    __tablename__ = 'process'
    
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    workflow_name = mapped_column(String(100), nullable=True)
    workflow_id = mapped_column(Integer, ForeignKey('workflow.id'), nullable=True)
    status = mapped_column(String(20), nullable=False)
    started_at = mapped_column(DateTime, nullable=True)
    finished_at = mapped_column(DateTime, nullable=True)
    workflow = relationship("Workflow")
    
    def finish(self):
        self.finished_at = datetime.now()
        self.status = "finished"
        
    