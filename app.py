import atexit

from flask import Flask, render_template, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from alarm import alarm

scheduler = BackgroundScheduler(timezone='Asia/Tokyo')
job = scheduler.add_job(func=alarm, trigger='cron', hour=7, minute=30)
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
    job.reschedule(trigger='cron', hour=hour, minute=minute)
    return jsonify({'status': 'success'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
