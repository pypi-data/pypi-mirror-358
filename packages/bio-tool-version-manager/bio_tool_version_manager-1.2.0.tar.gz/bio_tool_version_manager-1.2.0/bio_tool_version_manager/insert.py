# -*- coding: utf-8 -*-

from .models import Workflow, workflowtool, Tool, Process, ToolDatabase
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Dict


def get_or_create_workflow(session: Session, workflow_name: str, workflow_version: str,
                            tools: List[Tool]) -> Workflow:
    """
    Queries database and returns workflow-object with exact tool combination and workflow
    name and version. Will create a new object if neccessary
    """
    # query workflows, which have the same number of tool
    existing_workflow = session.query(Workflow).join(workflowtool).filter(
        Workflow.name == workflow_name,
        Workflow.version == workflow_version
    ).group_by(Workflow.id).having(
            func.count(workflowtool.c.tool_id) == len(tools))

    # loop over workflows in db and find workflow where each tools are present in exact version
    if existing_workflow:
        for wf in existing_workflow:
            if all(tool in tools for tool in wf.tools):
                print(f"Existing Workflow: {wf.name} with ID {wf.id}")
                return wf 

    # create a new workflow (if above does not return a workflow object)
    new_workflow = Workflow(name=workflow_name, version=workflow_version, tools=tools)
    session.add(new_workflow)
    session.commit()

    print(f"New Workflow created: {new_workflow.name} with ID {new_workflow.id}")
    return new_workflow


def get_or_create_tool(session: Session, tool_attributes: Dict) -> Tool:
    """
    Queries database and returns tool-object if it exists in exact name, version, 
     parameters and database
    """
    if tool_attributes.get("database") is not None:
        db = get_or_create_database(session, name=tool_attributes['database'].get('name'), 
                                    version=tool_attributes['database'].get('version'))
    else:
        db = None
    return _get_or_create_tool(session, name=tool_attributes['name'], version=tool_attributes['version'],
                                 parameter=tool_attributes.get('parameter'), database=db)


def get_or_create_database(session: Session, name: str, version: str) -> ToolDatabase:
    """
    Queries database and returns "ToolDatabase"-object with name and version. The "ToolDatabase"-object
    represents an optional sub-versioned ingredience to a bioinformatic tool. e.g. "BLAST-database"
    like resfinder_db, amrfinderdb, SILVA, ...
    """
    db = session.query(ToolDatabase).filter_by(name=name, version=version).first()
    if db:
        return db
    else:
        new_db = ToolDatabase(name=name, version=version)
        session.add(new_db)
        session.commit()
        return new_db
    
    
def _get_or_create_tool(session: Session, name: str, version: str, parameter: str=None, 
                        database: str=None) -> Tool:
    """
    internal sub-fuction to get_or_create tool that handles the tool creation
    """
    tool = session.query(Tool).filter_by(name=name, version=version, 
                        parameter=parameter, database=database).first()
    
    if tool:
        return tool
    else:
        new_tool = Tool(name=name, version=version, parameter=parameter, database=database)
        session.add(new_tool)
        session.commit()  # Speichere das neue Tool
        return new_tool
    
    
def update_process(session: Session, workflow: Workflow, process_id: int, 
                   set_finished: bool=False) -> None:
    """
    Update the process object with `workflow`-reference and optionally set `status` to "finished",
    adding the timestamp to `finished_at`
    """
    process = session.query(Process).filter(Process.id == process_id).first()

    if not process:
        raise ValueError(f"No process found with ID: {process_id}")
        
    process.workflow = workflow
    if set_finished:
        process.finish()
    session.add(process)
    session.commit()
    
    
def create_json_from_db(session: Session, process_id: int) -> Dict:
    """
    query database and create json that represents all workflow tool versions for given process
    """
    
    # Abfrage des Prozesses basierend auf der ID
    process = session.query(Process).filter(Process.id == process_id).first()
    
    if not process:
        raise ValueError(f"No process found with ID: {process_id}")
    
    # Holt die zugehörigen Workflow- und Tool-Informationen
    workflow = session.query(Workflow).filter(Workflow.id == process.workflow_id).first()
    if not workflow:
        raise ValueError(f"No workflow found for process ID: {process_id}")

    tools = workflow.tools  # Zugriff auf die Tools über die Beziehung

    tool_list = []
    for tool in tools:
        tool_dict = {"name":tool.name, "version":tool.version, "parameter":tool.parameter}
        if tool.database:
            db = {"name":tool.database.name, "version":tool.database.version}
            tool_dict["database"] = db
        tool_list.append(tool_dict)
        
    # create json-format
    process_json = {
        "process_id": process.id,
        "workflow": {
            "name": workflow.name,
            "version": workflow.version,
            "tools": tool_list
        }
    }   
            
    return process_json