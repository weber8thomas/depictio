from datetime import datetime
import sys
sys.path.append("/Users/tweber/Gits/depictio")

import os
import re
from typing import Dict, Type, List, Tuple, Optional, Any
from pydantic import BaseModel, ValidationError
import yaml
from fastapi_backend.configs.models import DataCollection, File, Workflow, DataCollectionConfig, WorkflowConfig, RootConfig, WorkflowRun


def get_config(filename: str):
    """
    Get the config file.
    """
    if not filename.endswith(".yaml"):
        raise ValueError("Invalid config file. Must be a YAML file.")
    if not os.path.exists(filename):
        raise ValueError(f"The file '{filename}' does not exist.")
    if not os.path.isfile(filename):
        raise ValueError(f"'{filename}' is not a file.")
    else:
        with open(filename, "r") as f:
            yaml_data = yaml.safe_load(f)
        return yaml_data


def validate_config(config: Dict, pydantic_model: Type[BaseModel]) -> BaseModel:
    """
    Load and validate the YAML configuration
    """
    if not isinstance(config, dict):
        raise ValueError("Invalid config. Must be a dictionary.")
    try:
        data = pydantic_model(**config)
    except ValidationError as e:
        raise ValueError(f"Invalid config: {e}")
    return data


def populate_file_models(workflow: Workflow) -> List[DataCollection]:
    """
    Returns a list of DataCollection models for a given workflow.
    """

    datacollections_models = []
    for datacollection_id, metadata in workflow.data_collections.items():
        datacollection_instance = DataCollection(
            data_collection_id=datacollection_id,
            description=metadata.description,
            config=metadata.config,
        )
        print(datacollection_instance)
        datacollections_models.append(datacollection_instance)

    return datacollections_models


def validate_worfklow(workflow: Workflow, config: RootConfig) -> dict:
    """
    Validate the workflow.
    """
    # workflow_config = config.workflows[workflow_name]
    # print(workflow_config)

    datacollection_models = populate_file_models(workflow)
    
    # Create a dictionary of validated datacollections with datacollection_id as the key
    validated_datacollections = {datacollection.data_collection_id: datacollection for datacollection in datacollection_models}

    print(validated_datacollections)    
    # Update the workflow's files attribute in the main config
    workflow.data_collections = validated_datacollections
    
    return workflow

def validate_all_workflows(config: RootConfig) -> RootConfig:
    """
    Validate all workflows in the config.
    """
    for workflow in config.workflows:
        validate_worfklow(workflow, config)
    
    return config

def scan_files(run_location: str, data_collection: DataCollection) -> List[File]:
    """
    Scan the files for a given workflow.
    """
    # Get the workflow's parent_runs_location

    if not os.path.exists(run_location):
        raise ValueError(f"The directory '{run_location}' does not exist.")
    if not os.path.isdir(run_location):
        raise ValueError(f"'{run_location}' is not a directory.")

    file_list = list()

    for root, dirs, files in os.walk(run_location):
        for file in files:
            if re.match(data_collection.config.regex, file):
                file_location = os.path.join(root, file)
                filename = file
                creation_time_float = os.path.getctime(file_location)
                modification_time_float = os.path.getmtime(file_location)

                # Convert the float values to datetime objects
                creation_time_dt = datetime.fromtimestamp(creation_time_float)
                modification_time_dt = datetime.fromtimestamp(modification_time_float)

                # Convert the datetime objects to ISO formatted strings
                creation_time_iso = creation_time_dt.isoformat()
                modification_time_iso = modification_time_dt.isoformat()

                data_collection_id = data_collection.data_collection_id
                    
                file_instance = File(
                    filename=filename,
                    file_location=file_location,
                    creation_time=creation_time_iso,
                    modification_time=modification_time_iso,
                    data_collection_id=data_collection_id
                )
                print(file_instance)
                file_list.append(file_instance)
    return file_list


def scan_runs(parent_runs_location, workflow_config: WorkflowConfig, data_collection: DataCollection) -> List[WorkflowRun]:
    """
    Scan the runs for a given workflow.
    """
    # Get the workflow's parent_runs_location

    if not os.path.exists(parent_runs_location):
        raise ValueError(f"The directory '{parent_runs_location}' does not exist.")
    if not os.path.isdir(parent_runs_location):
        raise ValueError(f"'{parent_runs_location}' is not a directory.")
    
    for run in os.listdir(parent_runs_location):
        if re.match(workflow_config.runs_regex, run):
            print(run)
            run_location = os.path.join(parent_runs_location, run)
            print(run_location)
            files = scan_files(run_location, data_collection)
            print(files)
            execution_time = datetime.fromtimestamp(os.path.getctime(run_location)).isoformat()

            # Create a WorkflowRun instance
            workflow_run = WorkflowRun(
                run_id=run,
                files=files,
                workflow_config=workflow_config,
                run_location=run_location,
                execution_time=execution_time,
                execution_profile=None
            )
            print(workflow_run)

            # print(os.l

    