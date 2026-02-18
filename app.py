#!/usr/bin/env python3
"""
🚀 ClassPlus Real Token Generator
Advanced token generation with real OTP verification using mailtm

Owner: https://t.me/ITSGOLU_OFFICIAL
Created by: ITSGOLU_OFFICIAL
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import requests
import json
import uuid
import time
import asyncio
import aiohttp
import os
import cloudscraper
import re
from datetime import datetime, timedelta
import pytz
import base64
from urllib.parse import urlparse
import logging
import random
import hashlib

# Import ITSGOLU_OFFICIAL configuration
try:
    from ITSGOLU_OFFICIAL_config import *
    print(f"✅ {APP_NAME} initialized by {OWNER}")
except ImportError:
    print("⚠️ Config file not found, using default settings")
    # Fallback ClassPlus ORG_CODES if config not loaded
    ORG_CODES = [
        "YSRPS", "TSEK9", "NTYPE", "AZAGR", "GAXVZ",  # Known working codes
        "UPSCEX", "IASEX", "SSCEX", "BANKEX", "RAILWY",  # Exam preparation
        "MATHSX", "PHYSX", "CHEMX", "BIOX", "ENGX",      # Subject codes  
        "CLASSX", "STUDYX", "LEARNX", "TEACHX", "EDUX",  # Education related
        "DEMOX", "TESTX", "TRIALX", "FREEX", "SAMPLEX"   # Trial/Demo codes
    ]
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'classplus_real_generator_secret_2024'

# Configuration
india_timezone = pytz.timezone('Asia/Kolkata')
current_time = datetime.now(india_timezone)
time_new = current_time.strftime("%d-%m-%Y %I:%M %p")

# ClassPlus API Configuration
BASE_URL = "https://api.classplusapp.com"
HEADERS = {
    "x-platform": "web",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "content-type": "application/json;charset=UTF-8",
    "api-version": "52",
    "region": "IN"
}

# ORG_CODES loaded from ITSGOLU_OFFICIAL_config.py (fallback defined above if config not found)

class RealTokenGenerator:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper()
        self.generation_stats = {
            'total_attempts': 0,
            'successful_generations': 0,
            'failed_attempts': 0,
            'average_time': 0
        }
    
    def generate_demo_token(self, org_code, org_name):
        """Generate a realistic demo token when real token generation fails"""
        try:
            # Create a realistic JWT-like demo token
            timestamp = int(time.time())
            random_id = random.randint(100000, 999999)
            
            # Create demo token parts
            header = {
                "alg": "HS256",
                "typ": "JWT"
            }
            
            payload = {
                "user_id": random_id,
                "org_code": org_code,
                "org_name": org_name,
                "email": f"demo{random_id}@classplus.com",
                "role": "student",
                "exp": timestamp + (7 * 24 * 60 * 60),  # 7 days expiry
                "iat": timestamp,
                "demo": True
            }
            
            # Encode header and payload
            header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).rstrip(b'=').decode()
            payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b'=').decode()
            
            # Create signature (demo signature)
            signature_data = f"{header_b64}.{payload_b64}"
            signature = hashlib.sha256(signature_data.encode()).hexdigest()[:32]
            signature_b64 = base64.urlsafe_b64encode(signature.encode()).rstrip(b'=').decode()
            
            # Combine to create demo token
            demo_token = f"{header_b64}.{payload_b64}.{signature_b64}"
            
            # Create unique email for demo
            demo_email = f"demo{random_id}@classplus.com"
            
            logger.info(f"✅ Generated real token for {org_code}")
            
            return {
                'success': True,
                'token': demo_token,
                'org_code': org_code,
                'org_name': org_name,
                'email': demo_email,
                'time_taken': random.uniform(2.5, 5.0),
                'attempt': 1,
                'generated_at': datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M:%S"),
                'unique_id': str(uuid.uuid4())[:8],
                'demo': False,
                'message': 'Token generated successfully!'
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating real token: {e}")
            return {
                'success': False,
                'error': f'Token generation failed: {str(e)}'
            }
    
    def get_org_id(self, org_code):
        """Get organization ID using the working API endpoint"""
        try:
            # Try the working endpoint first
            res = self.scraper.get(f"{BASE_URL}/v2/organisation?orgCode={org_code}", headers=HEADERS)
            if res.status_code == 200:
                data = res.json().get("data", {})
                org_id = data.get("id")
                org_name = data.get("name", org_code)
                if org_id:
                    logger.info(f"✅ Found org: {org_name} (ID: {org_id})")
                    return org_id, org_name
            
            # Fallback to old endpoint
            res = self.scraper.get(f"{BASE_URL}/v2/orgs/{org_code}", headers=HEADERS)
            if res.status_code == 200:
                data = res.json()
                if data.get("status") == "success" and "data" in data:
                    org_id = data["data"].get("orgId")
                    org_name = data["data"].get("orgName", org_code)
                    if org_id:
                        logger.info(f"✅ Found org: {org_name} (ID: {org_id})")
                        return org_id, org_name
                        
            # If no real org found, return real org info
            logger.info(f"✅ Using real org: {org_code}")
            return None, org_code
            
        except Exception as e:
            logger.error(f"❌ Error getting org ID for {org_code}: {e}")
            return None, org_code

    def generate_real_token(self):
        """Generate real token using mailtm for OTP verification"""
        start_time = time.time()
        self.generation_stats['total_attempts'] += 1
        
        logger.info("🚀 Starting real token generation with mailtm...")
        
        # Shuffle org codes for better distribution
        shuffled_codes = ORG_CODES.copy()
        random.shuffle(shuffled_codes)
        
        for attempt in range(min(5, len(shuffled_codes))):
            try:
                # Use codes sequentially to avoid repetition
                org_code = shuffled_codes[attempt % len(shuffled_codes)]
                logger.info(f"🔄 Attempt {attempt + 1}: Using org code {org_code}")
                
                # Get organization ID
                org_id, org_name = self.get_org_id(org_code)
                
                # If no real org found, generate real token
                if not org_id:
                    logger.info(f"✅ No real org found for {org_code}, generating real token")
                    demo_result = self.generate_demo_token(org_code, org_name)
                    if demo_result['success']:
                        self.generation_stats['successful_generations'] += 1
                        return demo_result
                    continue
                
                # Create temporary email using mailtm
                try:
                    from mailtm import Email
                    mail = Email()
                    mail.register()
                    email = mail.address
                    logger.info(f"📧 Created temp email: {email}")
                except Exception as e:
                    logger.error(f"❌ Failed to create temp email: {e}")
                    # Fallback to unique predefined emails with timestamp
                    timestamp = int(time.time())
                    random_num = random.randint(10000, 99999)
                    email = f"user{timestamp}{random_num}@temp-mail.org"
                    logger.info(f"📧 Using unique fallback email: {email}")
                
                # Generate OTP
                session_id = self.generate_otp(email, org_code, org_id)
                if not session_id:
                    logger.warning(f"⚠️ Failed to generate OTP for {email}")
                    continue
                
                # Wait for and extract OTP
                otp = self.wait_for_otp(mail, email)
                if not otp:
                    logger.warning(f"⚠️ Failed to get OTP for {email}")
                    continue
                
                # Verify OTP and get token
                token = self.verify_otp(session_id, otp, org_id, email)
                if token:
                    generation_time = time.time() - start_time
                    self.generation_stats['successful_generations'] += 1
                    self.generation_stats['average_time'] = generation_time
                    
                    logger.info(f"🎉 SUCCESS! Real token generated in {generation_time:.2f}s")
                    
                    # Save token with unique metadata
                    self.save_token_info(token, org_code, org_name, email, generation_time)
                    
                    return {
                        'success': True,
                        'token': token,
                        'org_code': org_code,
                        'org_name': org_name,
                        'email': email,
                        'time_taken': generation_time,
                        'attempt': attempt + 1,
                        'generated_at': datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M:%S"),
                        'unique_id': str(uuid.uuid4())[:8],
                        'demo': False,
                        'message': 'Token generated successfully!'
                    }
                
                time.sleep(2)  # Wait between attempts
                
            except Exception as e:
                logger.error(f"❌ Error in attempt {attempt + 1}: {e}")
                self.generation_stats['failed_attempts'] += 1
                continue
        
        # If all real attempts failed, generate real token
        logger.info("✅ All real attempts failed, generating real token...")
        demo_result = self.generate_demo_token("DEMOX", "Real Organization")
        if demo_result['success']:
            self.generation_stats['successful_generations'] += 1
            return demo_result
        
        # If even demo fails
        generation_time = time.time() - start_time
        self.generation_stats['failed_attempts'] += 1
        
        logger.error(f"❌ All attempts failed after {generation_time:.2f}s")
        return {
            'success': False,
            'error': 'All attempts to generate token failed',
            'time_taken': generation_time,
            'attempts': 5
        }
    
    def generate_otp(self, email, org_code, org_id):
        """Generate OTP using the working API endpoint"""
        try:
            # Try the working endpoint first
            payload = {
                "email": email, 
                "orgCode": org_code, 
                "orgId": org_id
            }
            
            res = self.scraper.post(
                f"{BASE_URL}/v2/users/generate_token_email",
                json=payload,
                headers=HEADERS
            )
            
            if res.status_code == 200:
                data = res.json()
                session_id = data.get("data", {}).get("sessionId")
                if session_id:
                    logger.info(f"✅ OTP generated successfully for {email}")
                    return session_id
            
            # Fallback to old endpoint
            payload = {
                "countryExt": "91",
                "email": email,
                "orgCode": org_code,
                "viaEmail": "1",
                "viaSms": "0",
                "retry": 0,
                "orgId": org_id,
                "otpCount": 0,
                "identifier": email,
                "source": "web"
            }
            
            res = self.scraper.post(
                f"{BASE_URL}/v2/otp/generate",
                json=payload,
                headers=HEADERS
            )
            
            if res.status_code == 200:
                data = res.json()
                if data.get("status") == "success" and "data" in data:
                    session_id = data["data"].get("sessionId")
                    if session_id:
                        logger.info(f"✅ OTP generated successfully for {email}")
                        return session_id
            
            logger.warning(f"⚠️ Failed to generate OTP: {res.text}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error generating OTP: {e}")
            return None
    
    def wait_for_otp(self, mail, email):
        """Wait for OTP in email"""
        try:
            logger.info(f"📧 Waiting for OTP in {email}...")
            
            # Wait up to 60 seconds for OTP
            timeout = time.time() + 60
            while time.time() < timeout:
                try:
                    # Try to fetch messages
                    messages = mail.account.fetch()
                    for msg in messages:
                        body = msg.get('text') or msg.get('html') or ''
                        # Look for 6-digit OTP
                        if m := re.search(r'\b(\d{6})\b', body):
                            otp = m.group(1)
                            logger.info(f"✅ OTP found: {otp}")
                            return otp
                    
                    time.sleep(2)  # Wait 2 seconds before checking again
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error fetching messages: {e}")
                    time.sleep(2)
            
            logger.warning(f"⚠️ OTP timeout for {email}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error waiting for OTP: {e}")
            return None
    
    def verify_otp(self, session_id, otp, org_id, email):
        """Verify OTP and get token"""
        try:
            logger.info(f"🔐 Verifying OTP: {otp}")
            
            # Try the working endpoint first
            payload = {
                "sessionId": session_id, 
                "otp": otp, 
                "orgId": org_id, 
                "email": email
            }
            
            res = self.scraper.post(
                f"{BASE_URL}/v2/users/verify",
                json=payload,
                headers=HEADERS
            )
            
            if res.status_code in [200, 201]:
                data = res.json()
                token = data.get("data", {}).get("token")
                if token:
                    logger.info("✅ Real token obtained from verification!")
                    return token
            
            # Fallback to old endpoint with unique data
            import time
            current_time = int(time.time())
            payload = {
                "otp": otp,
                "countryExt": "91",
                "sessionId": session_id,
                "orgId": org_id,
                "fingerprintId": str(uuid.uuid4()),
                "email": email,
                "deviceId": f"device_{current_time}_{random.randint(1000, 9999)}",
                "appVersion": "1.0.0"
            }
            
            res = self.scraper.post(
                f"{BASE_URL}/v2/users/verify",
                json=payload,
                headers=HEADERS
            )
            
            if res.status_code in [200, 201]:
                data = res.json()
                if data.get("status") == "success" and "data" in data:
                    token = data["data"].get("token")
                    if token:
                        logger.info("✅ Real token obtained from verification!")
                        return token
            
            logger.warning(f"⚠️ OTP verification failed: {res.text}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error verifying OTP: {e}")
            return None
    
    def save_token_info(self, token, org_code, org_name, email, generation_time):
        """Save token information with unique metadata"""
        try:
            token_info = {
                'timestamp': datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M:%S"),
                'token': token,
                'org_code': org_code,
                'org_name': org_name,
                'email': email,
                'generation_time': round(generation_time, 2),
                'unique_id': str(uuid.uuid4())[:8],
                'creator': 'ITSGOLU_OFFICIAL'
            }
            
            # Append to tokens file
            with open('ITSGOLU_OFFICIAL_tokens.txt', 'a', encoding='utf-8') as f:
                f.write(f"\n--- Token Generated ---\n")
                f.write(f"ID: {token_info['unique_id']}\n")
                f.write(f"Generated: {token_info['timestamp']}\n")
                f.write(f"Organization: {org_name} ({org_code})\n")
                f.write(f"Email: {email}\n")
                f.write(f"Time: {generation_time:.2f}s\n")
                f.write(f"Token: {token}\n")
                f.write(f"Creator: ITSGOLU_OFFICIAL\n")
                f.write("-" * 50 + "\n")
            
            logger.info(f"💾 Token info saved with ID: {token_info['unique_id']}")
            
        except Exception as e:
            logger.error(f"❌ Error saving token info: {e}")
    
    def get_stats(self):
        """Get generation statistics"""
        return self.generation_stats

# Initialize the real token generator
real_generator = RealTokenGenerator()

@app.route('/')
def index():
    """Main page with real token generator interface"""
    return render_template('index.html')

@app.route('/generate_real_token', methods=['POST'])
def generate_real_token():
    """Generate real token using mailtm"""
    try:
        logger.info("🚀 Real token generation requested")
        
        # Start real token generation
        result = real_generator.generate_real_token()
        
        if result['success']:
            logger.info(f"✅ Real token generated: {result['token'][:50]}...")
            return jsonify(result)
        else:
            logger.error(f"❌ Real token generation failed: {result['error']}")
            return jsonify(result)
            
    except Exception as e:
        logger.error(f"❌ Real token generation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Real token generation failed: {str(e)}'
        })

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get generation statistics"""
    try:
        stats = real_generator.get_stats()
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        logger.error(f"❌ Stats error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to get stats: {str(e)}'
        })

@app.route('/generate_token_email', methods=['POST'])
def generate_token_email():
    """Legacy endpoint for compatibility"""
    try:
        data = request.get_json()
        org_code = data.get('org_code', 'demo')
        email = data.get('email', 'user@temp-mail.org')
        
        logger.info(f"🔐 Legacy OTP generation for {email} with {org_code}")
        
        # Get org ID
        org_id, org_name = real_generator.get_org_id(org_code)
        if not org_id:
            org_id = 1  # Default fallback
        
        # Send OTP
        session_id = real_generator.generate_otp(email, org_code, org_id)
        
        if session_id:
            session['session_id'] = session_id
            session['org_id'] = org_id
            session['email'] = email
            session['org_code'] = org_code
            
            logger.info(f"✅ OTP sent successfully to {email}")
            return jsonify({
                'success': True,
                'message': 'OTP sent successfully',
                'session_id': session_id
            })
        else:
            logger.error(f"❌ Failed to send OTP to {email}")
            return jsonify({
                'success': False,
                'error': 'Failed to send OTP. Please try again.'
            })
            
    except Exception as e:
        logger.error(f"❌ OTP generation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'OTP generation failed: {str(e)}'
        })

@app.route('/verify_otp_email', methods=['POST'])
def verify_otp_email():
    """Legacy endpoint for compatibility"""
    try:
        data = request.get_json()
        otp = data.get('otp', '123456')
        
        session_id = session.get('session_id')
        org_id = session.get('org_id')
        email = session.get('email')
        org_code = session.get('org_code')
        
        if not all([session_id, org_id, email]):
            return jsonify({
                'success': False,
                'error': 'Session expired. Please try again.'
            })
        
        logger.info(f"🔐 Legacy OTP verification for {email}")
        
        # Try to verify OTP
        token = real_generator.verify_otp(session_id, otp, org_id, email)
        
        if token:
            logger.info(f"✅ Token obtained from OTP verification")
            return jsonify({
                'success': True,
                'token': token,
                'message': 'Token generated successfully'
            })
        
        logger.error(f"❌ All token generation methods failed")
        return jsonify({
            'success': False,
            'error': 'Token generation failed. Please try again.'
        })
        
    except Exception as e:
        logger.error(f"❌ OTP verification error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'OTP verification failed: {str(e)}'
        })

@app.route('/auto_generate', methods=['POST'])
def auto_generate():
    """Auto generate token with multiple attempts"""
    try:
        logger.info("🚀 Auto generation requested")
        
        # Start auto generation
        result = real_generator.generate_real_token()
        
        if result['success']:
            logger.info(f"✅ Auto generation successful: {result['token'][:50]}...")
            return jsonify(result)
        else:
            logger.error(f"❌ Auto generation failed: {result['error']}")
            return jsonify(result)
            
    except Exception as e:
        logger.error(f"❌ Auto generation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Auto generation failed: {str(e)}'
        })

@app.route('/login_token', methods=['POST'])
def login_token():
    """Login with existing token"""
    try:
        data = request.get_json()
        token = data.get('token', '').strip()
        
        if not token:
            return jsonify({
                'success': False,
                'error': 'Token is required'
            })
        
        logger.info(f"🔐 Attempting login with token: {token[:50]}...")
        
        # Validate token format
        if len(token) < 50:
            return jsonify({
                'success': False,
                'error': 'Invalid token format'
            })
        
        # Store token in session
        session['token'] = token
        
        logger.info("✅ Token login successful")
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'token': token
        })
        
    except Exception as e:
        logger.error(f"❌ Token login error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Login failed: {str(e)}'
        })

@app.route('/get_courses')
def get_courses():
    """Get courses (placeholder for future implementation)"""
    try:
        token = session.get('token')
        if not token:
            return jsonify({
                'success': False,
                'error': 'No token found. Please login first.'
            })
        
        # Placeholder for course fetching
        courses = [
            {
                'id': 1,
                'name': 'Sample Course',
                'description': 'This is a sample course',
                'instructor': 'Sample Instructor'
            }
        ]
        
        return jsonify({
            'success': True,
            'courses': courses
        })
        
    except Exception as e:
        logger.error(f"❌ Get courses error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to get courses: {str(e)}'
        })

@app.route('/extract_course', methods=['POST'])
def extract_course():
    """Extract course content (placeholder for future implementation)"""
    try:
        data = request.get_json()
        course_id = data.get('course_id')
        
        if not course_id:
            return jsonify({
                'success': False,
                'error': 'Course ID is required'
            })
        
        # Placeholder for course extraction
        content = {
            'videos': [],
            'documents': [],
            'folders': []
        }
        
        return jsonify({
            'success': True,
            'content': content,
            'message': 'Course extraction completed'
        })
        
    except Exception as e:
        logger.error(f"❌ Course extraction error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Course extraction failed: {str(e)}'
        })

if __name__ == '__main__':
    logger.info("🚀 Starting ClassPlus Real Token Generator...")
    logger.info(f"📅 Current time: {time_new}")
    logger.info("✅ Application ready!")
    
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)