# -*- coding: utf-8 -*-
SQL_ALCHEMY_AVAILABLE = True

import argparse
import sys
try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from .insert import get_or_create_tool, get_or_create_workflow, create_json_from_db, update_process
    from .models import Base
except ImportError:
    SQL_ALCHEMY_AVAILABLE = False

from .io import write_json_file, load_json
from typing import Dict


def incrementally_create_json(json_file_path: str, workflow_name: str=None, workflow_version: str=None,
                              tool_name: str=None, tool_version: str=None, tool_parameter: str=None,
                              db_version: str=None, db_name: str=None) -> None:
    """
    Creates a json formatted file or adds new entries (tools) to an existing json file.
    Workflow name and version parameters will be ignored if the file already exists.
    """
    # Read JSON if it exists (will create) one
    try:
        existing_data = load_json(json_file_path)
    except FileNotFoundError:
        existing_data = {"workflow": {"tools":[]}}
        if workflow_name:
            existing_data["workflow"]["name"] = workflow_name
        if workflow_version:
            existing_data["workflow"]["version"] = workflow_version

    if tool_name:
        tool = {"name":tool_name}
        if tool_version:
            tool["version"] = tool_version
        if tool_parameter:
            tool["parameter"] = tool_parameter
        if db_name or db_version:
            db = {"name": db_name, "version": db_version}
            tool["database"] = db
        existing_data["workflow"]["tools"].append(tool)

    # Schreibe das aktualisierte JSON zurück
    write_json_file(existing_data, json_file_path)

    print(f"Updated JSON file: {json_file_path}")


def insert_json_to_db(session, data: Dict, process_id: int, set_finished=False) -> None:
    """
    Insert the data of json file into the database.
    requires a sqlalchemy session object
    """

    tools = []
    workflow_name = data.get('workflow', {}).get('name', 'Default Workflow')
    workflow_version = data.get('workflow', {}).get('version', '1.0')

    # get or create a tool-entries
    for tool in data.get('workflow', {}).get('tools', []):
        tool = get_or_create_tool(session, tool)
        tools.append(tool)

    # create the workflow (or return workflow if it exists in the exact tools+db versions)
    workflow = get_or_create_workflow(session, workflow_name, workflow_version, tools)
    update_process(session, workflow, process_id, set_finished)


def main():
    """
    entry point for CLI
    """
    parser = argparse.ArgumentParser(description="Workflow Version Management Tool CLI")
    subparsers = parser.add_subparsers(dest='command')

    # Parser für inkrementelles Erstellen/Bearbeiten
    increment_parser = subparsers.add_parser('add', help='Incrementally create/edit JSON file')
    increment_parser.add_argument('-n', dest='workflow_name', required=False)
    increment_parser.add_argument('--wf_version', help='workflow version', required=False)
    increment_parser.add_argument('-t', dest='tool_name')
    increment_parser.add_argument('--tool_version')
    increment_parser.add_argument('-p', dest='tool_parameter', required=False)
    increment_parser.add_argument('-f','--file', dest='json_file', help='Path to input JSON file')
    increment_parser.add_argument('--db_name')
    increment_parser.add_argument('--db_version')
    if SQL_ALCHEMY_AVAILABLE:
        # sub-parser for database import
        insert_parser = subparsers.add_parser('insert', help='Insert JSON file contents into the database')
        insert_parser.add_argument('-f','--file', dest='json_file', help='Path to input JSON file', required=True)
        insert_parser.add_argument('--pid', dest='process_id', type=int, help='Process ID to store', required=True)
        insert_parser.add_argument('--finish', action='store_true', help='set process status to finished and finished_at timestamp')
    
        # sub-parser for database export
        create_parser = subparsers.add_parser('dump', help='Create a JSON file from database for a given process ID')
        create_parser.add_argument('--pid', dest='process_id', type=int, help='Process ID to create JSON from', required=True)
        create_parser.add_argument('-f','--file', dest='json_file', help='Path to output JSON file [stdout]', default=sys.stdout,
                                   type=argparse.FileType('w'))
        
        for p in [insert_parser, create_parser]:
            # db definitions (apply to export and import in database)
            p.add_argument('-d','--database',dest='database',
                    help="mysql database name or path to sqlite-db [./agres.db]",
                    default="./agres.db")
            p.add_argument('-H','--hostname',dest='hostname', 
                    help="mysql hostname; if not provided sqlite-db will be used",
                    required=False)
            p.add_argument('-u','--user',dest='dbuser', help="mysql database username",
                    required=False)
            p.add_argument('-p','--password',dest='mariadbpassword',
                    help="mysql password", required=False)


    args = parser.parse_args()

    # call function to create or add to json file
    if args.command == 'add':
        incrementally_create_json(args.json_file, args.workflow_name, args.wf_version,
                                  args.tool_name, args.tool_version, args.tool_parameter,
                                  args.db_version, args.db_name)
        return
    
    # establish connection to database (mysql or sqlite)
    if SQL_ALCHEMY_AVAILABLE:
        if args.hostname:
            engine = create_engine("mysql+mysqlconnector://%s:%s@%s:3306/%s" %
                            (args.dbuser, args.mariadbpassword, args.hostname, 
                                args.database))
        else:
            engine = create_engine("sqlite:///%s" % args.database)
        session = Session(engine)
        Base.metadata.create_all(engine)
        
        # functions to insert to database or export from database. both need process-id
        if args.command == 'insert':
            json_data = load_json(args.json_file)
            insert_json_to_db(session, json_data, args.process_id, args.finish)
        elif args.command == 'dump':
            json_data = create_json_from_db(session, args.process_id)
            write_json_file(json_data, args.json_file)
            

        session.close()
    

if __name__ == "__main__":
    main()