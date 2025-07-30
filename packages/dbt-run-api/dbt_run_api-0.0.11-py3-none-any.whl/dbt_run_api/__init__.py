import uvicorn
import os
import yaml
from fastapi import BackgroundTasks, FastAPI
from dbt.cli.main import dbtRunner
from pydantic import BaseModel
import multiprocessing
import subprocess
from fastapi.responses import JSONResponse

app = FastAPI()

def compile_command(run_config):
    cmd_list = ["dbt"]
    cmd_list.append(run_config.pop("cmd"))
    if "vars" in run_config:
        vars_yaml = yaml.dump(run_config.pop("vars"), default_flow_style=None) 
        cmd_list.extend(["--vars", f"{vars_yaml.strip()}"])
    for key, value in run_config.items():
        cmd_list.append(f"--{key}")
        if value != True:
            cmd_list.append(str(value))
    return cmd_list

def compile_odd_command(odd_config):
    cmd_list = ["odd", "dbt"]
    cmd_list.append(odd_config.pop("cmd"))
    for key, value in odd_config.items():
        cmd_list.append(f"--{key}")
        if value != True:
            cmd_list.append(str(value))
    return cmd_list

def dbt_task(cmd_list, return_dict):
    try:
        res = subprocess.run(cmd_list, check=True)
        return_dict["result"] = "Success"
    except subprocess.CalledProcessError as e:
        return_dict["result"] = f"Error: {e}"        


def run_dbt(run_config):
    is_async  = run_config.pop("async", False)
    cmd = compile_command(run_config)
    print(" ".join(cmd))
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    proc = multiprocessing.Process(
        target=dbt_task,
        args=(cmd,return_dict))
    proc.start()
    if not is_async:
       print(proc.join())
    return {'pid': proc.pid, "res": return_dict["result"]}

def run_odd(odd_config):
    is_async  = odd_config.pop("async", False)
    cmd = compile_odd_command(odd_config)
    print(" ".join(cmd))
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    proc = multiprocessing.Process(
        target=dbt_task,
        args=(cmd,return_dict))
    proc.start()
    if not is_async:
       print(proc.join())
    return {'pid': proc.pid, "res": return_dict["result"]}


@app.get('/callback')
def root():
    return {'message': 'This endpoint works!'}


@app.post("/dbt")
async def run_dbt_command_endpoint(run_config: dict, background_tasks: BackgroundTasks):
    background_tasks.add_task(run_dbt, run_config)
    return JSONResponse(status_code=202, content={"message": "DBT task started"})

@app.post("/odd")
async def run_odd_command_endpoint(odd_config: dict, background_tasks: BackgroundTasks):
    background_tasks.add_task(run_odd, odd_config)
    return JSONResponse(status_code=202, content={"message": "ODD task started"})
