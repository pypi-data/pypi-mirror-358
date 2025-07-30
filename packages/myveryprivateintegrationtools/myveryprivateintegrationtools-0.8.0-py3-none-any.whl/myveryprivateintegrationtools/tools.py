import os

from batch import BatchesInterface

class Config:

    def __init__(self, 
                storage_connection_string: str,
                workflow_name: str, 
                stream_name: str, 
                date: str):

        self.storage_connection_string = storage_connection_string
        self.workflow_name = workflow_name
        self.batch_name = stream_name
        self.date = date 

def get_environment_variables() -> list[(str,str)]:
    return list(os.environ.items())

def get_config(environment_variables: list[(str,str)]) : 

    storage_connection_string = next(x[1] for x in environment_variables if x[0] == "STORAGE_CONNECTION_STRING")
    workflow_name = next(x[1] for x in environment_variables if x[0] == "WORKFLOW_NAME")
    stream_name = next(x[1] for x in environment_variables if x[0] == "BATCH_NAME")
    date = next(x[1] for x in environment_variables if x[0] == "EXECUTION_DATE")

    return Config(storage_connection_string, workflow_name, stream_name, date)

def delete_previous_partial_loads(config: Config):
     return

def write_data(config, batch_json):
    return

def run(providerStreams: BatchesInterface):
    envs = get_environment_variables()
    config = get_config(envs)
    batch = next(batch for batch in providerStreams.get_batches() if batch[0] == config.batch_name)[1]
    batchInstance = batch(envs)
    delete_previous_partial_loads(config)
    for batch in batchInstance.get(config.date):
        write_data(config, batch)