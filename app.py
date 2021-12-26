from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


@app.route('/')
def index():
    params = {
        'hour': 2,
        'minute': 30
    }
    return render_template('index.html', **params)


@app.route('/set-WpByVmm5LF', methods=["POST"])
def set_time():
    print(request.form)
    time = request.form['time']
    hour = int(time[:2])
    minute = int(time[3:])
    print(hour, minute)
    return jsonify({'status': 'success'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
