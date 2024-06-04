from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import subprocess
import threading
import os
import time
import logging

app = Flask(__name__)
script_dir = os.path.join(os.path.dirname(__file__), 'scripts')
current_script = None
current_thread = None
update_interval = 600  # Default update interval in seconds

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_script(script_name):
    global current_script
    script_path = os.path.join(script_dir, script_name)
    while True:
        logging.info(f'Starting script: {script_name}')
        current_script = subprocess.Popen(["python", script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = current_script.communicate()
        logging.info(f'Script output: {stdout.decode("utf-8")}')
        if stderr:
            logging.error(f'Script error: {stderr.decode("utf-8")}')
        time.sleep(update_interval)  # Wait for the specified interval

@app.route('/')
def index():
    scripts = [f for f in os.listdir(script_dir) if f.endswith('.py') and not f.endswith('_config.py')]
    configs = [f for f in os.listdir(script_dir) if f.endswith('_config.py')]
    return render_template('index.html', scripts=scripts, configs=configs, running=current_script is not None, interval=update_interval)

@app.route('/start', methods=['POST'])
def start_script():
    global current_thread
    script_name = request.form['script']
    if current_script is None:
        logging.info(f'Starting new thread for script: {script_name}')
        current_thread = threading.Thread(target=run_script, args=(script_name,))
        current_thread.start()
    else:
        logging.warning('Script is already running')
    return redirect(url_for('index'))

@app.route('/stop', methods=['POST'])
def stop_script():
    global current_script
    if current_script is not None:
        logging.info('Stopping script')
        current_script.terminate()
        current_script = None
    else:
        logging.warning('No script is currently running')
    return redirect(url_for('index'))

@app.route('/upload', methods=['POST'])
def upload_script():
    file = request.files['file']
    file.save(os.path.join(script_dir, file.filename))
    logging.info(f'Uploaded new script: {file.filename}')
    return redirect(url_for('index'))

@app.route('/copy', methods=['POST'])
def copy_script():
    source_script = request.form['source_script']
    new_script_name = request.form['new_script_name']
    source_path = os.path.join(script_dir, source_script)
    dest_path = os.path.join(script_dir, new_script_name)
    with open(source_path, 'r') as src, open(dest_path, 'w') as dst:
        dst.write(src.read())
    logging.info(f'Copied script from {source_script} to {new_script_name}')
    return redirect(url_for('index'))

@app.route('/update_interval', methods=['POST'])
def update_interval_route():
    global update_interval
    update_interval = int(request.form['interval'])
    logging.info(f'Updated interval to {update_interval} seconds')
    return redirect(url_for('index'))

@app.route('/config/<script_name>')
def edit_config(script_name):
    config_path = os.path.join(script_dir, f"{script_name}_config.py")
    with open(config_path, 'r') as file:
        config = file.read()
    logging.info(f'Editing config for script: {script_name}')
    return render_template('config.html', script_name=script_name, config=config)

@app.route('/update_config/<script_name>', methods=['POST'])
def update_config(script_name):
    config_path = os.path.join(script_dir, f"{script_name}_config.py")
    config = request.form['config']
    with open(config_path, 'w') as file:
        file.write(config)
    logging.info(f'Updated config for script: {script_name}')
    return redirect(url_for('index'))

@app.route('/logs')
def logs():
    return render_template('logs.html', logs=get_logs())

def get_logs():
    logs = []
    if current_script:
        stdout, stderr = current_script.communicate()
        logs.append(stdout.decode('utf-8'))
        if stderr:
            logs.append(stderr.decode('utf-8'))
    return logs

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(script_dir, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
