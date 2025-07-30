# -*- coding: utf-8 -*-

from unittest.mock import patch
from bio_tool_version_manager.cli import incrementally_create_json

@patch('workflow_tool_manager.cli.load_json', side_effect=FileNotFoundError)
@patch('workflow_tool_manager.cli.write_json_file')
def test_incrementally_create_json_new_file(mock_write_json_file, mock_load_json):
    """Teste die Erstellung eines neuen JSON-Files."""
    json_file = 'test_workflow.json'
    
    incrementally_create_json(json_file, workflow_name='TestWorkflow', workflow_version='1.0', 
                              tool_name='TestTool', tool_version='1.0', tool_parameter='param1')

    expected_data = {
        "workflow": {
            "tools": [
                {
                    "name": 'TestTool',
                    "version": '1.0',
                    "parameter": 'param1'
                }
            ],
            "name": 'TestWorkflow',
            "version": '1.0',
        }
    }
    mock_write_json_file.assert_called_once_with(expected_data, json_file)
    
    
@patch('workflow_tool_manager.cli.load_json')
@patch('workflow_tool_manager.cli.write_json_file')
def test_incrementally_create_json_update_file(mock_write_json_file, mock_load_json):
    """Teste das Aktualisieren eines vorhandenen JSON-Files."""
    json_file = 'test_workflow.json'
    
    # Simulate existing JSON
    existing_data = {
        "workflow": {
            "tools": [
                {
                    "name": 'ExistingTool',
                    "version": '1.0',
                    "parameter": 'existing_param'
                }
            ],
            "name": 'TestWorkflow',
            "version": '1.0',
        }
    }
    mock_load_json.return_value = existing_data

    incrementally_create_json(json_file, tool_name='NewTool', tool_version='1.0', tool_parameter='new_param')

    expected_updated_data = {
        "workflow": {
            "tools": [
                {
                    "name": 'ExistingTool',
                    "version": '1.0',
                    "parameter": 'existing_param'
                },
                {
                    "name": 'NewTool',
                    "version": '1.0',
                    "parameter": 'new_param'
                }
            ],
            "name": 'TestWorkflow',
            "version": '1.0',
        }
    }

    mock_write_json_file.assert_called_once_with(expected_updated_data, json_file)
