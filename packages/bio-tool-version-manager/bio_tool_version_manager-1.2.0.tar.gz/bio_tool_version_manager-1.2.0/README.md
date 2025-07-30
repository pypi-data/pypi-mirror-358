# Workflow Tool Manager

**Workflow Tool Manager** is a python package to create a json file during a bioinformatic workflow (e.g. written in nextflow) to track the software tools, versions, parameters and database by incrementally adding new entries in each process.

## Installation

Installable via `pip`:

```bash
pip install bio_tool_version_manager
```

## Usage

### CLI

1. **Incrementally add new tools to the "workflowfile"**:

```
bio_tool_version_manager add -h
usage: bio_tool_version_manager add [-h] [-n WORKFLOW_NAME] [--wf_version WF_VERSION] [-t TOOL_NAME]
                                    [--tool_version TOOL_VERSION] [-p TOOL_PARAMETER] [-f JSON_FILE]
                                    [--db_name DB_NAME] [--db_version DB_VERSION]

options:
  -h, --help            show this help message and exit
  -n WORKFLOW_NAME
  --wf_version WF_VERSION
                        workflow version
  -t TOOL_NAME
  --tool_version TOOL_VERSION
  -p TOOL_PARAMETER
  -f, --file JSON_FILE  Path to input JSON file
  --db_name DB_NAME
  --db_version DB_VERSION

```

2. **Insert into a database (requires sqlalchemy, sqlite or mariadb-database)**:

```
bio_tool_version_manager insert -h
usage: bio_tool_version_manager insert [-h] -f JSON_FILE --pid PROCESS_ID [-d DATABASE] [-H HOSTNAME] [-u DBUSER] [--finish]
                                       [-p MARIADBPASSWORD]

options:
  -h, --help            show this help message and exit
  -f, --file JSON_FILE  Path to input JSON file
  --finish              set process status to finished and finished_at timestamp
  --pid PROCESS_ID      Process ID to store
  -d, --database DATABASE
                        mysql database name or path to sqlite-db [./agres.db]
  -H, --hostname HOSTNAME
                        mysql hostname; if not provided sqlite-db will be used
  -u, --user DBUSER     mysql database username
  -p, --password MARIADBPASSWORD
                        mysql password
```

3. **Dump versions/workflow from database for specified process**:

```
bio_tool_version_manager dump -h
usage: bio_tool_version_manager dump [-h] --pid PROCESS_ID [-f JSON_FILE] [-d DATABASE] [-H HOSTNAME] [-u DBUSER] [-p MARIADBPASSWORD]

options:
  -h, --help            show this help message and exit
  --pid PROCESS_ID      Process ID to create JSON from
  -f, --file JSON_FILE  Path to output JSON file
  -d, --database DATABASE
                        mysql database name or path to sqlite-db [./agres.db]
  -H, --hostname HOSTNAME
                        mysql hostname; if not provided sqlite-db will be used
  -u, --user DBUSER     mysql database username
  -p, --password MARIADBPASSWORD
                        mysql password
```

### Python-API

The the package can also be imported and used within python:

```python
from workflow_tool_manager.insert import get_or_create_tool, get_or_create_workflow
from sqlalchemy.orm import sessionmaker


# Create session to your engine (assume you already have a db connection as sqlalchemy-engine)
Session = sessionmaker(bind=engine)  
session = Session()  

tool1_dict = {
  'name':'blastn', 
  'version':'2.10.1', 
  'parameter':'-evalue 0.01',
  'database': {
    'name': 'mynt',
    'version': '0.1a',
  },
}

tool2_dict = {
  'name':'Tool2', 
  'version':'2.0', 
  'parameter':'--fast',
}

tool1 = get_or_create_tool(session, tool1_dict)  
tool2 = get_or_create_tool(session, tool2_dict)  
workflow = get_or_create_workflow(session, name='myworkflow', version='1.0', tools=[tool1, tool2])  

```

## License

This project is licensed under MIT license
