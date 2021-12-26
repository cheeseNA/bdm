import atexit

from flask import Flask, render_template, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler


def print_test():
    print('triggered')


scheduler = BackgroundScheduler(timezone='Asia/Tokyo')
scheduler.add_job(func=print_test, trigger='interval', seconds=10)
scheduler.start()

atexit.register(lambda: scheduler.shutdown())

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/set-WpByVmm5LF', methods=["POST"])
def set_time():
    print(request.form)
    time = request.form['time']
    hour = int(time[:2])
    minute = int(time[3:])
    print(hour, minute)
    print(scheduler.get_jobs())
    job_id = scheduler.get_jobs()[0].id
    scheduler.reschedule_job(job_id=job_id, trigger='interval', seconds=minute)
    return jsonify({'status': 'success'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
