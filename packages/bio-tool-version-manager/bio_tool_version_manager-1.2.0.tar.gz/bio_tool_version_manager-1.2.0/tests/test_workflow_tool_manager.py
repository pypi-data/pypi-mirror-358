# -*- coding: utf-8 -*-

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bio_tool_version_manager.insert import get_or_create_workflow, create_json_from_db
from bio_tool_version_manager.models import Tool, Workflow, Base, Process, ToolDatabase
from bio_tool_version_manager.cli import insert_json_to_db

# New database created
@pytest.fixture(scope='module')
def test_database():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

@pytest.fixture
def session(test_database):
    """Erstelle eine neue Session für jeden Test."""
    Session = sessionmaker(bind=test_database)
    return Session()

def test_create_tool(session):
    """Teste das Erstellen eines neuen Tools."""
    tool = Tool(name='Tool1', version='1.0', parameter='param1')
    session.add(tool)
    session.commit()
    
    retrieved_tool = session.query(Tool).filter_by(name='Tool1').first()
    assert retrieved_tool is not None
    assert retrieved_tool.version == '1.0'

def test_get_or_create_workflow(session):
    """Teste die Ausführung eines Workflows mit Tools."""
    tool1 = Tool(name='Tool1', version='1.0', parameter='param1')
    database = ToolDatabase(name='tool2db', version="1.0b")
    tool2 = Tool(name='Tool2', version='2.0', parameter='param2', database=database)
    session.add(database)
    session.add(tool1)
    session.add(tool2)
    session.commit()

    workflow = get_or_create_workflow(session, 'ExampleWorkflow', '1.0', [tool1, tool2])
    assert workflow is not None
    assert workflow.name == 'ExampleWorkflow'
    assert len(workflow.tools) == 2

def test_insert_json_to_db(session):
    """Teste das Einfügen von JSON-Daten in die Datenbank."""
    process = Process(status="new")
    session.add(process)
    session.commit()
    json_data = {
        "workflow": {
            "tools": [
                {
                    "name": "Tool1",
                    "version": "1.0",
                    "parameter": "param1"
                },
                {
                    "name": "Tool2",
                    "version": "2.0",
                    "parameter": "param2",
                    "database": {
                            "name": "tool2db",
                            "version": "1.0b"
                            }
                }
            ],
            "name": "ExampleWorkflow",
            "version": "1.0",
        }
    }
    
    insert_json_to_db(session, json_data, process.id)  # Setze hier die korrekte Funktion ein

    workflow = session.query(Workflow).filter_by(name="ExampleWorkflow").first()
    db = session.query(ToolDatabase).filter_by(name="tool2db").first()
    assert workflow is not None
    assert workflow.version == "1.0"
    assert len(workflow.tools) == 2
    assert db is not None


def test_create_json_from_db(session):
    """Teste die create_json_from_db Funktion."""
    # Erstelle Beispiel-Tools
    tool1 = Tool(name='Tool1', version='1.0', parameter='param1')
    database = ToolDatabase(name='tool2db', version="1.0b")
    tool2 = Tool(name='Tool2', version='2.0', parameter='param2', database=database)
    
    # Workflow erstellen und Tools verknüpfen
    workflow = Workflow(name='ExampleWorkflow', version='1.0')
    workflow.tools = [tool1, tool2]
    
    # Prozess erstellen, der auf den Workflow verweist
    process = Process(workflow=workflow, status="running")
    
    # Füge die Objekte zur Sitzung hinzu und committe
    session.add(tool1)
    session.add(tool2)
    session.add(workflow)
    session.add(process)
    session.commit()
    
    # Teste create_json_from_db
    process_id = process.id
    result = create_json_from_db(session, process_id)
    
    expected_json = {
        "process_id": process_id,
        "workflow": {
            "tools": [
                {
                    "name": 'Tool1',
                    "version": '1.0',
                    "parameter": 'param1'
                },
                {
                    "name": 'Tool2',
                    "version": '2.0',
                    "parameter": 'param2',
                    "database": {
                            "name": "tool2db",
                            "version": "1.0b"
                            }
                }
            ],
            "name": 'ExampleWorkflow',
            "version": '1.0',
        }
    }

    assert result == expected_json

def test_double_entry(session):
    """Tests if two processes with the same workflow tools only create a new workflow once"""
    process1 = Process(status="new")
    process2 = Process(status="new")
    process3 = Process(status="new")
    session.add(process1)
    session.add(process2)
    session.add(process3)
    session.commit()
    json_data1 = {
        "workflow": {
            "tools": [
                {
                    "name": "Tool1",
                    "version": "1.0",
                    "parameter": "param1"
                },
                {
                    "name": "Tool2",
                    "version": "2.0",
                    "parameter": "param2",
                    "database": {
                            "name": "tool2db_new",
                            "version": "1.0b"
                            }
                }
            ],
            "name": "ExampleWorkflow2",
            "version": "1.0",
        }
    } 

    json_data2 = {
        "workflow": {
            "tools": [
                {
                    "name": "Tool2",
                    "version": "2.0",
                    "parameter": "param2",
                    "database": {
                            "name": "tool2db_new",
                            "version": "1.0b"
                            }
                },  
                {
                    "name": "optional tool3",
                    "version": "1.5",
                    "parameter": "param3",
                },                               
                {
                    "name": "Tool1",
                    "version": "1.0",
                    "parameter": "param1"
                },
            ],
            "name": "ExampleWorkflow2",
            "version": "1.0",
        }
    }

    json_data3 = {
        "workflow": {
            "tools": [
                {
                    "name": "Tool2",
                    "version": "2.0",
                    "parameter": "param2",
                    "database": {
                            "name": "tool2db_new",
                            "version": "1.0b"
                            }
                },
                {
                    "name": "Tool1",
                    "version": "1.0",
                    "parameter": "param1"
                },
            ],
            "name": "ExampleWorkflow2",
            "version": "1.0",
        }
    } 



    insert_json_to_db(session, json_data1, process1.id)  
    insert_json_to_db(session, json_data2, process2.id)  
    insert_json_to_db(session, json_data3, process3.id)  

    workflow = session.query(Workflow).filter_by(name="ExampleWorkflow2")
    db = session.query(ToolDatabase).filter_by(name="tool2db_new")
    assert workflow.count() == 2
    assert db.count() == 1

    
def test_create_json_from_db_not_found(session):
    """Teste create_json_from_db für einen nicht vorhandenen Prozess."""
    with pytest.raises(ValueError):
        create_json_from_db(session, -1)