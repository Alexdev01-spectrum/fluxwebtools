#!/usr/bin/env python3
"""
ALEXDEV BOMB TOOL — Web Server
Author: Alex Jhon Ponce
"""

import uuid, time, threading
from flask import Flask, render_template, request, jsonify
from bomber import BomberTool, CallBomber, NGLSpammer

app = Flask(__name__)
jobs: dict = {}
lock = threading.Lock()


def _new_job(meta: dict) -> str:
    job_id = str(uuid.uuid4())
    with lock:
        jobs[job_id] = {
            'status': 'running',
            'results': [], 'success': 0, 'fail': 0,
            'total': 0, 'abort': False, **meta
        }
    return job_id


# ── SMS bomb ─────────────────────────────────────────────────────────────────

def _run_sms(job_id, phone, rounds):
    tool = BomberTool()
    services = tool.all_services
    with lock:
        jobs[job_id]['total'] = len(services) * rounds
    for round_num in range(1, rounds + 1):
        for name, fn in services:
            with lock:
                if jobs[job_id].get('abort'):
                    jobs[job_id]['status'] = 'aborted'
                    return
            try:
                success, message = fn(phone)
            except Exception as e:
                success, message = False, str(e)[:60]
            with lock:
                jobs[job_id]['results'].append({
                    'service': name, 'success': success,
                    'message': message, 'round': round_num,
                    'ts': time.strftime('%H:%M:%S')
                })
                if success:
                    jobs[job_id]['success'] += 1
                else:
                    jobs[job_id]['fail'] += 1
    with lock:
        jobs[job_id]['status'] = 'done'


@app.route('/api/bomb', methods=['POST'])
def start_bomb():
    body = request.get_json(silent=True) or {}
    phone = body.get('phone', '').strip()
    rounds = max(1, min(int(body.get('rounds', 1)), 50))
    tool = BomberTool()
    if not tool.validate_phone(phone):
        return jsonify({'error': 'Invalid Philippine number. Use 09XXXXXXXXX format.'}), 400
    job_id = _new_job({'phone': phone, 'rounds': rounds, 'mode': 'sms'})
    threading.Thread(target=_run_sms, args=(job_id, phone, rounds), daemon=True).start()
    return jsonify({'job_id': job_id})


# ── Call bomb ─────────────────────────────────────────────────────────────────

def _run_call(job_id, phone, rounds):
    tool = CallBomber()
    services = tool.all_services
    with lock:
        jobs[job_id]['total'] = len(services) * rounds
    for round_num in range(1, rounds + 1):
        for name, fn in services:
            with lock:
                if jobs[job_id].get('abort'):
                    jobs[job_id]['status'] = 'aborted'
                    return
            try:
                success, message = fn(phone)
            except Exception as e:
                success, message = False, str(e)[:60]
            with lock:
                jobs[job_id]['results'].append({
                    'service': name, 'success': success,
                    'message': message, 'round': round_num,
                    'ts': time.strftime('%H:%M:%S')
                })
                if success:
                    jobs[job_id]['success'] += 1
                else:
                    jobs[job_id]['fail'] += 1
    with lock:
        jobs[job_id]['status'] = 'done'


@app.route('/api/call', methods=['POST'])
def start_call():
    body = request.get_json(silent=True) or {}
    phone = body.get('phone', '').strip()
    rounds = max(1, min(int(body.get('rounds', 1)), 20))
    tool = CallBomber()
    if not tool.validate_phone(phone):
        return jsonify({'error': 'Invalid Philippine number. Use 09XXXXXXXXX format.'}), 400
    job_id = _new_job({'phone': phone, 'rounds': rounds, 'mode': 'call'})
    threading.Thread(target=_run_call, args=(job_id, phone, rounds), daemon=True).start()
    return jsonify({'job_id': job_id})


# ── NGL spam ─────────────────────────────────────────────────────────────────

def _run_ngl(job_id, username, message, count):
    spammer = NGLSpammer()
    with lock:
        jobs[job_id]['total'] = count
    spammer.spam(username, message, count, jobs[job_id])


@app.route('/api/ngl', methods=['POST'])
def start_ngl():
    body = request.get_json(silent=True) or {}
    username = body.get('username', '').strip().lstrip('@')
    message  = body.get('message', '').strip()
    count    = max(1, min(int(body.get('count', 10)), 200))
    if not username:
        return jsonify({'error': 'NGL username required'}), 400
    if not message:
        return jsonify({'error': 'Message required'}), 400
    job_id = _new_job({'username': username, 'message': message, 'count': count, 'mode': 'ngl'})
    threading.Thread(target=_run_ngl, args=(job_id, username, message, count), daemon=True).start()
    return jsonify({'job_id': job_id})


# ── Shared ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/status/<job_id>')
def get_status(job_id):
    with lock:
        job = jobs.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    return jsonify(job)


@app.route('/api/abort/<job_id>', methods=['POST'])
def abort_job(job_id):
    with lock:
        if job_id in jobs:
            jobs[job_id]['abort'] = True
    return jsonify({'ok': True})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
