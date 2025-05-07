from flask import Flask, request, render_template, jsonify
import json
from task_management_up import add_task, modify_task, delete_task, list_tasks, execute_task, list_task_logs

app = Flask(__name__)
TASK_TYPES = ['send_email', 'send_sms', 'send_cmd', 'send_sql']


@app.route('/')
def task_list():
    tasks = list_tasks()
    task_list = []
    print(f"length of tasks { len(tasks) }")

    if( len(tasks) > 0 ):
        print("here >>11 ")
        for task_id, task in tasks.items():
            print("here >>11.1 ")
            task_info = {
                'task_id': task_id,
                'task_type': task['task_type'],
                'trigger': task['trigger'],
                'params': task['params'],
                'last_execution_time': None  # 这里简单假设为 None，实际可根据日志判断
            }
            task_list.append(task_info)
    print(">>>render_templet index..")
    return render_template('index.html', tasks=task_list)


@app.route('/add_task', methods=['GET', 'POST'])
def add_task_page():
    if request.method == 'POST':
        task_id = request.form.get('task_id')
        trigger_type = request.form.get('trigger_type')
        trigger_params_str = request.form.get('trigger_params')
        task_type = request.form.get('task_type')
        params_str = request.form.get('params')
        try:
            trigger_params = json.loads(trigger_params_str)
            params = json.loads(params_str)
            if add_task(task_id, trigger_type, trigger_params, task_type, params):
                return "任务添加成功"
            else:
                return "任务添加失败"
        except json.JSONDecodeError:
            return "输入的参数不是有效的 JSON 格式"
    return render_template('add_task.html', task_types=TASK_TYPES)


@app.route('/modify_task/<task_id>', methods=['GET', 'POST'])
def modify_task_page(task_id):
    tasks = list_tasks()
    if task_id not in tasks:
        return "任务不存在"
    task = tasks[task_id]
    if request.method == 'POST':
        trigger_type = request.form.get('trigger_type')
        trigger_params_str = request.form.get('trigger_params')
        params_str = request.form.get('params')
        try:
            trigger_params = json.loads(trigger_params_str)
            params = json.loads(params_str)
            modify_task(task_id, trigger_type, trigger_params, params)
            return "任务修改成功"
        except json.JSONDecodeError:
            return "输入的参数不是有效的 JSON 格式"
    return render_template('modify_task.html',
                           task_id=task_id,
                           trigger_params=json.dumps(task['trigger']['params']),
                           params=json.dumps(task['params']))


@app.route('/delete_task/<task_id>')
def delete_task_page(task_id):
    delete_task(task_id)
    return "任务删除成功"


@app.route('/execute_task/<task_id>')
def execute_task_page(task_id):
    execute_task(task_id)
    return "任务已触发执行"


@app.route('/task_logs')
def task_logs():
    task_type = request.args.get('task_type')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    page = int(request.args.get('page', 1))
    logs, total = list_task_logs(task_type, start_time, end_time, page)
    log_list = []
    for log in logs:
        log_info = {
            'task_id': log.task_id,
            'task_type': log.task_type,
            'trigger_rule': log.trigger_rule,
            'params': log.params,
            'result': log.result,
            'duration': log.duration,
            'execution_time': log.execution_time
        }
        log_list.append(log_info)
    return render_template('task_logs.html',
                           log_list=log_list,
                           task_types=TASK_TYPES,
                           selected_task_type=task_type,
                           start_time=start_time,
                           end_time=end_time,
                           page=page,
                           total=total)


if __name__ == '__main__':
    app.run(debug=True)
    