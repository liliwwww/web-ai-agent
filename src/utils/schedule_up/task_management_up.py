import smtplib
import json
import time
import logging
import os
import pickle
from email.mime.text import MIMEText
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
import signal
import sys
import psutil
from tools_utils import send_email,send_cmd,send_sms,send_sql

# 配置日志记录
logging.basicConfig(
    filename='scheduler.log',
    level=logging.warning,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

import logging

# 配置日志记录
logging.basicConfig(
    filename='scheduler.log',  # 日志写入文件
    level=logging.WARN,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 添加控制台处理器（关键步骤）
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # 设置控制台输出级别
console_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))  # 可选：简化控制台输出格式
logging.getLogger().addHandler(console_handler)  # 将处理器添加到根日志记录器


# 配置文件路径
DB_FILE_PATH = r'C:\Users\wdp\project\web-ai-agent\src\utils\schedule_up\task_up.db'
TASKS_FILE = r'C:\Users\wdp\project\web-ai-agent\src\utils\schedule_up\tasks_up.pkl'

# 配置持久化存储
jobstores = {
    'default': SQLAlchemyJobStore(url=f'sqlite:///{DB_FILE_PATH}')
}

scheduler = BackgroundScheduler(jobstores=jobstores)
scheduler.start()

# 数据库配置
engine = create_engine(f'sqlite:///{DB_FILE_PATH}')
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


class TaskLog(Base):
    __tablename__ = 'task_logs'
    id = Column(Integer, primary_key=True)
    task_id = Column(String)
    task_type = Column(String)
    trigger_rule = Column(String)
    params = Column(String)
    result = Column(String)
    duration = Column(Float)
    execution_time = Column(DateTime)


Base.metadata.create_all(engine)

# 尝试从文件中加载 tasks 字典
if os.path.exists(TASKS_FILE):
    try:
        with open(TASKS_FILE, 'rb') as f:
            print(">>>load task from FILE")
            tasks = pickle.load(f)
            print(f">>>load task from FILE  ok task len{len(tasks)}")
    except Exception as e:
        logging.error(f"加载任务文件时出错: {e}")
        tasks = {}
else:
    print(">>>load task from {}")
    tasks = {}




TASK_FUNCTION_MAP = {
    'send_email': send_email,
    'send_sms': send_sms,
    'send_cmd': send_cmd,
    'send_sql': send_sql
}


def execute_task(task_id):
    if task_id not in tasks:
        logging.warning(f"任务 {task_id} 不存在")
        return
    try:
        task = tasks[task_id]
        logging.warning(f"任务类型 {task['task_type']} ")
        logging.warning(f"任务参数 {task['params']} ")
        

        task_func = TASK_FUNCTION_MAP.get(task['task_type'])
        if task_func:
            start_time = time.time()
            result = task_func(**task['params'])
            end_time = time.time()
            duration = end_time - start_time
            log = TaskLog(
                task_id=task_id,
                task_type=task['task_type'],
                trigger_rule=json.dumps(task['trigger']),
                params=json.dumps(task['params']),
                result='成功' if result else '失败',
                duration=duration,
                execution_time=time.strftime('%Y-%m-%d %H:%M:%S.%f', time.localtime())
            )
            session.add(log)
            session.commit()
            logging.info(f"任务 {task_id} 执行完成，结果: {'成功' if result else '失败'}，耗时: {duration} 秒")
        else:
            logging.error(f"未知的任务类型: {task['task_type']}")
    except Exception as e:
        logging.error(f"执行任务 {task_id} 时出错: {e}")


def add_task(task_id, trigger_type, trigger_params, task_type, params):
    print(f" step20 add to tasks[]==={task_id}")
    print(f" step20 add to tasks[]==={trigger_type}")
    print(f" step20 add to tasks[]==={trigger_params}")
    print(f" step20 add to tasks[]==={task_type}")
    print(f" step20 add to tasks[]==={params}")
    
    
    
    
    try:
        # step1. add to schedule
        job = None
        if trigger_type == 'date':
            job = scheduler.add_job(execute_task, 'date', run_date=trigger_params['run_date'], args=[task_id])
        elif trigger_type == 'interval':
            job = scheduler.add_job(execute_task, 'interval',
                                    weeks=trigger_params.get('weeks', 0),
                                    days=trigger_params.get('days', 0),
                                    hours=trigger_params.get('hours', 0),
                                    minutes=trigger_params.get('minutes', 0),
                                    seconds=trigger_params.get('seconds', 0),
                                    start_date=trigger_params.get('start_date'),
                                    end_date=trigger_params.get('end_date'),
                                    args=[task_id])
        elif trigger_type == 'cron':
            job = scheduler.add_job(execute_task, 'cron',
                                    year=trigger_params.get('year'),
                                    month=trigger_params.get('month'),
                                    day=trigger_params.get('day'),
                                    week=trigger_params.get('week'),
                                    day_of_week=trigger_params.get('day_of_week'),
                                    hour=trigger_params.get('hour'),
                                    minute=trigger_params.get('minute'),
                                    second=trigger_params.get('second'),
                                    start_date=trigger_params.get('start_date'),
                                    end_date=trigger_params.get('end_date'),
                                    args=[task_id])
        elif trigger_type == 'idle':
            def idle_check():
                cpu_percent = psutil.cpu_percent(interval=1)
                if cpu_percent < 10:  # 假设CPU使用率低于10%为空闲
                    execute_task(task_id)

            #job = scheduler.add_job(send_email, 'cron', hour=10, minute=10, args=[], id="444")
            #job = scheduler.add_job(idle_check, 'interval', seconds=trigger_params.get('idle_duration', 60))
            job = scheduler.add_job(send_email, 'interval', seconds=60)

        print(f" step2 add to tasks[]==={task_id}")
        if job:
            tasks[task_id] = {
                'job': job,
                'trigger': {
                    'type': trigger_type,
                    'params': trigger_params
                },
                'task_type': task_type,
                'params': params
            }

            print(f" step2 add to tasks[]===>>>>>>>>>>{job}")
            print(f" step2 add to tasks[]===>>>>>>>>>>{trigger_type}")
            print(f" step2 add to tasks[]===>>>>>>>>>>{trigger_params}")
            print(f" step2 add to tasks[]===>>>>>>>>>>{task_type}")
            print(f" step2 add to tasks[]===>>>>>>>>>>{params}")

            # 保存 tasks 字典到文件
            with open(TASKS_FILE, 'wb') as f:
                pickle.dump(tasks, f)
            logging.info(f"任务 {task_id} 添加成功")
            print("==========================>>>>>>>>>>45")
            return True
        else:
            logging.error(f"添加任务 {task_id} 失败，未知的触发器类型: {trigger_type}")
            return False
    except Exception as e:
        logging.error(f"添加任务 {task_id} 失败: {e}")
        return False


def modify_task(task_id, trigger_type=None, trigger_params=None, params=None):
    if task_id not in tasks:
        logging.warning(f"任务 {task_id} 不存在")
        return
    try:
        job = tasks[task_id]['job']
        if trigger_type and trigger_params:
            if trigger_type == 'date':
                job.reschedule('date', run_date=trigger_params['run_date'])
            elif trigger_type == 'interval':
                job.reschedule('interval',
                               weeks=trigger_params.get('weeks', 0),
                               days=trigger_params.get('days', 0),
                               hours=trigger_params.get('hours', 0),
                               minutes=trigger_params.get('minutes', 0),
                               seconds=trigger_params.get('seconds', 0),
                               start_date=trigger_params.get('start_date'),
                               end_date=trigger_params.get('end_date'))
            elif trigger_type == 'cron':
                job.reschedule('cron',
                               year=trigger_params.get('year'),
                               month=trigger_params.get('month'),
                               day=trigger_params.get('day'),
                               week=trigger_params.get('week'),
                               day_of_week=trigger_params.get('day_of_week'),
                               hour=trigger_params.get('hour'),
                               minute=trigger_params.get('minute'),
                               second=trigger_params.get('second'),
                               start_date=trigger_params.get('start_date'),
                               end_date=trigger_params.get('end_date'))
            elif trigger_type == 'idle':
                def idle_check():
                    cpu_percent = psutil.cpu_percent(interval=1)
                    if cpu_percent < 10:  # 假设CPU使用率低于10%为空闲
                        execute_task(task_id)

                job.reschedule('interval', seconds=trigger_params.get('idle_duration', 60))
            tasks[task_id]['trigger'] = {
                'type': trigger_type,
                'params': trigger_params
            }
        if params:
            tasks[task_id]['params'] = params
        # 保存 tasks 字典到文件
        with open(TASKS_FILE, 'wb') as f:
            pickle.dump(tasks, f)
        logging.info(f"任务 {task_id} 修改成功")
    except Exception as e:
        logging.error(f"修改任务 {task_id} 失败: {e}")


def delete_task(task_id):
    if task_id not in tasks:
        logging.warning(f"任务 {task_id} 不存在")
        return
    try:
        scheduler.remove_job(task_id)
        del tasks[task_id]
        # 保存 tasks 字典到文件
        with open(TASKS_FILE, 'wb') as f:
            pickle.dump(tasks, f)
        logging.info(f"任务 {task_id} 删除成功")
    except Exception as e:
        logging.error(f"删除任务 {task_id} 失败: {e}")


def list_tasks():
    return tasks


def list_task_logs(task_type=None, start_time=None, end_time=None, page=1, page_size=40):
    query = session.query(TaskLog)
    if task_type:
        query = query.filter(TaskLog.task_type == task_type)
    if start_time:
        query = query.filter(TaskLog.execution_time >= start_time)
    if end_time:
        query = query.filter(TaskLog.execution_time <= end_time)
    total = query.count()
    logs = query.offset((page - 1) * page_size).limit(page_size).all()
    return logs, total


def signal_handler(sig, frame):
    logging.info("程序被手动中断，正在停止调度器...")
    scheduler.shutdown()
    session.close()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


def main():
    try:
        while True:
            time.sleep(1)
    except Exception as e:
        logging.error(f"程序出现异常: {e}")
        scheduler.shutdown()
        session.close()
        sys.exit(1)

def test():
    

    print("OK1")
    # 测试添加任务功能
    task_id = 93
    trigger_type="date"
    ###                      重要                 ###
    ###  必须加 json.loads() 才可以 ###
    ###                      重要                 ###
    trigger_params = json.loads('{"run_date": "2025-12-10 08:00:00"}')
    task_type = "send_email"
    params = json.loads('{"to": "test@example.com", "title": "测试邮件", "body": "这是一封测试邮件"}')

    #title = "Test Task"
    #description = "This is a test task."
    
    
    print("OK2")
    task_id = add_task(task_id, trigger_type,trigger_params,task_type,params)
    print(f"OK3{task_id}")

    tasks  = list_tasks()
    print("OK2.1")
    
    c = tasks.items()
    print(f"OK3.1 >>{len(c)}")

if __name__ == "__main__":
    test()
    