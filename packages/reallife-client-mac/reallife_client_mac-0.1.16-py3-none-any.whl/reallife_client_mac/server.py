""" server """
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pydantic import BaseModel # 导入 BaseModel
from fastapi import FastAPI
from .core import ReallifeClient

async def perform_startup_tasks():
    """ 1 """
    print("Performing startup tasks...")
    scheduler.start()
    print("APScheduler 启动")
    # Your existing startup logic here

async def perform_shutdown_tasks():
    """ 1 """
    print("Performing shutdown tasks...")
    scheduler.shutdown()
    print("APScheduler 关闭")
    # Your existing shutdown logic here

class TaskRequest(BaseModel):
    """ 1 """
    task: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    """_summary_

    Args:
        app (FastAPI): _description_
    """
    await perform_startup_tasks()
    yield
    await perform_shutdown_tasks()


app = FastAPI(lifespan=lifespan)

scheduler = BackgroundScheduler()

reallife = ReallifeClient()

scheduler.add_job(reallife.kanban, CronTrigger(hour=9, minute=40, day_of_week='mon-fri'))


@app.get("/build_kanban")
async def build_kanban():
    """_summary_

    Args:
        app (FastAPI): _description_
    """
    result = reallife.kanban()
    return {"message": result}

@app.get("/add_kanban")
async def add_kanban():
    """_summary_

    Args:
        app (FastAPI): _description_
    """
    result = reallife.add_kanban(6)
    return {"message": result}


class BuildFlexibleConfigRequest(BaseModel):
    """ 1 """
    task: str = None
    type: str = 'flex' # or pool
    action: bool = True



@app.post("/build_flexible")
async def build_flexible(build_flexible_config: BuildFlexibleConfigRequest):
    """_summary_

    Args:
        build_flexible_config (BuildFlexibleConfigRequest): _description_
    """
    result = reallife.build_flexible(
        task=build_flexible_config.task,
        type=build_flexible_config.type,
        action=build_flexible_config.action
    )
    return {"message": result}

@app.post("/tips")
async def tips(task_request:TaskRequest):
    """_summary_

    Args:
        task_request (TaskRequest): _description_

    Returns:
        _type_: _description_
    """
    task = task_request.task
    reallife.tips(task)
    return {"message": '以添加'}

@app.get("/receive")
async def query_the_current_task():
    """_summary_

    Returns:
        _type_: _description_
    """
    result = reallife.query_the_current_task()
    # return {"message": result}
    if result[1] == "!":
        messages = result.split(' ',1)
        if len(messages) == 1:
            return {"message": messages[0]}
        else:
            return {"message":messages[1]}
    else:
        return {"message": result}


@app.get("/start")
async def start():
    """_summary_

    Returns:
        _type_: _description_
    """
    result = reallife.start()
    # return {"message": result}
    if result[1] == "!":
        messages = result.split(' ',1)
        if len(messages) == 1:
            return {"message": messages[0]}
        else:
            return {"message":messages[1]}
    else:
        return {"message": result}

@app.get("/close")
async def close():
    """_summary_

    Returns:
        _type_: _description_
    """
    result = reallife.close()
    return {"message": result}

@app.get("/run")
async def run():
    """_summary_

    Returns:
        _type_: _description_
    """
    result = reallife.run()
    return {"message": result}
    



if __name__ == "__main__":
    import argparse
    import uvicorn
    from .log import Log

    parser = argparse.ArgumentParser(
        description="Start a simple HTTP server similar to http.server."
    )
    parser.add_argument(
        'port',
        metavar='PORT',
        type=int,
        nargs='?',  # 端口是可选的
        default=8021,
        help='Specify alternate port [default: 8000]'
    )

    parser.add_argument(
        '--env',
        type=str,
        default='dev', # 默认是开发环境
        choices=['dev', 'prod'],
        help='Set the environment (dev or prod) [default: dev]'
    )

    args = parser.parse_args()

    port = args.port
    if args.env == "dev":
        port += 100
        Log.reset_level('debug',env = args.env)
    elif args.env == "prod":
        Log.reset_level('info',env = args.env)# ['debug', 'info', 'warning', 'error', 'critical']

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        reload=False  # 启用热重载
    )
