# ITSGOLU_OFFICIAL Configuration File
# Owner: https://t.me/ITSGOLU_OFFICIAL
# Created by: ITSGOLU_OFFICIAL

"""
ClassPlus Token Generator Configuration
This file contains configuration settings for the token generator
"""

# Application Settings
APP_NAME = "ClassPlus Auto Token Generator"
OWNER = "ITSGOLU_OFFICIAL"
CONTACT = "https://t.me/ITSGOLU_OFFICIAL"

# Token Generation Settings
MAX_RETRY_ATTEMPTS = 10
GENERATION_TIMEOUT = 30

# ClassPlus Organization Codes (6-letter capital codes)
ORG_CODES = [
    "YSRPS", "TSEK9", "NTYPE", "AZAGR", "GAXVZ",  # Known working codes
    "UPSCEX", "IASEX", "SSCEX", "BANKEX", "RAILWY",  # Exam preparation
    "MATHSX", "PHYSX", "CHEMX", "BIOX", "ENGX",      # Subject codes  
    "CLASSX", "STUDYX", "LEARNX", "TEACHX", "EDUX",  # Education related
    "DEMOX", "TESTX", "TRIALX", "FREEX", "SAMPLEX"   # Trial/Demo codes
]

# Temporary Email Services
TEMP_EMAILS = [
    'user1@temp-mail.org',
    'user2@temp-mail.org', 
    'user3@temp-mail.org',
    'user4@temp-mail.org',
    'user5@temp-mail.org'
]

# API Configuration
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Content-Type': 'application/json'
}

print(f"Configuration loaded by {OWNER}")
print(f"Contact: {CONTACT}")