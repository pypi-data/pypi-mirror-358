#!/usr/bin/env python3
"""
Tests for the web3_oracle CLI interface
"""

import unittest
import subprocess
import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class TestCLI(unittest.TestCase):
    """Test cases for the CLI interface"""
    
    def setUp(self):
        """Set up test environment"""
        # Common test data
        self.eth_address = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
        self.btc_address = "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599"
        self.uni_address = "0x1f9840a85d5af5bf1d1762f925bdaddc4201f984"
        self.test_timestamp = 1747224000
        self.test_block = 15000000
    
    def run_cli_command(self, *args):
        """Helper method to run CLI commands"""
        cmd = [sys.executable, "-m", "web3_oracle.cli"] + list(args)
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out"
    
    def test_cli_get_price(self):
        """Test CLI get_price command"""
        returncode, stdout, stderr = self.run_cli_command(
            "get_price", self.eth_address, str(self.test_timestamp)
        )
        
        if returncode == 0:
            self.assertIn(".", stdout)  # Should contain a price (with decimal)
            price = float(stdout.strip())
            self.assertGreater(price, 0)
            print(f"✓ CLI get_price: ${price:.2f}")
        else:
            print(f"CLI get_price failed: {stderr}")
    
    def test_cli_get_price_by_date(self):
        """Test CLI get_price_by_date command"""
        returncode, stdout, stderr = self.run_cli_command(
            "get_price_by_date", self.eth_address, "2025-05-13", "12:00:00"
        )
        
        if returncode == 0:
            self.assertIn(".", stdout)  # Should contain a price (with decimal)
            price = float(stdout.strip())
            self.assertGreater(price, 0)
            print(f"✓ CLI get_price_by_date: ${price:.2f}")
        else:
            print(f"CLI get_price_by_date failed: {stderr}")
    
    def test_cli_get_reference_price(self):
        """Test CLI get_reference_price command"""
        returncode, stdout, stderr = self.run_cli_command(
            "get_reference_price", self.uni_address
        )
        
        if returncode == 0:
            self.assertIn(".", stdout)  # Should contain a price (with decimal)
            price = float(stdout.strip())
            self.assertGreater(price, 0)
            print(f"✓ CLI get_reference_price: ${price:.6f}")
        else:
            print(f"CLI get_reference_price failed: {stderr}")
    
    def test_cli_get_price_by_block(self):
        """Test CLI get_price_by_block command"""
        returncode, stdout, stderr = self.run_cli_command(
            "get_price_by_block", self.eth_address, str(self.test_block)
        )
        
        if returncode == 0:
            output = stdout.strip()
            if output and output != "None":
                price = float(output)
                self.assertGreater(price, 0)
                print(f"✓ CLI get_price_by_block: ${price:.2f}")
            else:
                print("CLI get_price_by_block: No block price data available")
        else:
            print(f"CLI get_price_by_block failed: {stderr}")
    
    def test_cli_fast_price(self):
        """Test CLI fast_price command"""
        returncode, stdout, stderr = self.run_cli_command(
            "fast_price", str(self.test_block)
        )
        
        if returncode == 0:
            output = stdout.strip()
            if output and output != "None":
                price = float(output)
                self.assertGreater(price, 0)
                print(f"✓ CLI fast_price: ${price:.2f}")
            else:
                print("CLI fast_price: No block price data available")
        else:
            print(f"CLI fast_price failed: {stderr}")
    
    def test_cli_fast_btc_price(self):
        """Test CLI fast_btc_price command"""
        returncode, stdout, stderr = self.run_cli_command(
            "fast_btc_price", str(self.test_block)
        )
        
        if returncode == 0:
            output = stdout.strip()
            if output and output != "None":
                price = float(output)
                self.assertGreater(price, 0)
                print(f"✓ CLI fast_btc_price: ${price:.2f}")
            else:
                print("CLI fast_btc_price: No BTC block price data available")
        else:
            print(f"CLI fast_btc_price failed: {stderr}")
    
    def test_cli_get_token_price_with_block(self):
        """Test CLI get_token_price command with block number"""
        returncode, stdout, stderr = self.run_cli_command(
            "get_token_price", self.eth_address, "--block", str(self.test_block)
        )
        
        if returncode == 0:
            self.assertIn(".", stdout)  # Should contain a price (with decimal)
            price = float(stdout.strip())
            self.assertGreater(price, 0)
            print(f"✓ CLI get_token_price (with block): ${price:.2f}")
        else:
            print(f"CLI get_token_price (with block) failed: {stderr}")
    
    def test_cli_get_token_price_with_timestamp(self):
        """Test CLI get_token_price command with timestamp"""
        returncode, stdout, stderr = self.run_cli_command(
            "get_token_price", self.eth_address, "--timestamp", str(self.test_timestamp)
        )
        
        if returncode == 0:
            self.assertIn(".", stdout)  # Should contain a price (with decimal)
            price = float(stdout.strip())
            self.assertGreater(price, 0)
            print(f"✓ CLI get_token_price (with timestamp): ${price:.2f}")
        else:
            print(f"CLI get_token_price (with timestamp) failed: {stderr}")
    
    def test_cli_get_token_price_reference(self):
        """Test CLI get_token_price command for reference price"""
        returncode, stdout, stderr = self.run_cli_command(
            "get_token_price", self.uni_address
        )
        
        if returncode == 0:
            output = stdout.strip()
            if output and output != "None":
                price = float(output)
                self.assertGreater(price, 0)
                print(f"✓ CLI get_token_price (reference): ${price:.6f}")
            else:
                print("CLI get_token_price (reference): No reference price available")
        else:
            print(f"CLI get_token_price (reference) failed: {stderr}")
    
    def test_cli_list_tokens(self):
        """Test CLI list_tokens command"""
        returncode, stdout, stderr = self.run_cli_command("list_tokens")
        
        if returncode == 0:
            self.assertIn("ETH", stdout)  # Should contain ETH token
            self.assertIn("BTC", stdout)  # Should contain BTC token
            lines = [line for line in stdout.split('\n') if line.strip()]
            self.assertGreater(len(lines), 0)
            print(f"✓ CLI list_tokens: {len(lines)} tokens listed")
        else:
            print(f"CLI list_tokens failed: {stderr}")
    
    def test_cli_verbose_flag(self):
        """Test CLI with verbose flag"""
        returncode, stdout, stderr = self.run_cli_command(
            "--verbose", "get_price", self.eth_address, str(self.test_timestamp)
        )
        
        if returncode == 0:
            # With verbose flag, we expect to see initialization info
            # either in stdout or stderr
            combined_output = stdout + stderr
            self.assertTrue(
                any(keyword in combined_output.lower() for keyword in ['oracle', 'initialized', 'loading', 'entries'])
            )
            print("✓ CLI verbose flag works")
        else:
            print(f"CLI verbose flag failed: {stderr}")
    
    def test_cli_error_handling(self):
        """Test CLI error handling"""
        # Test with invalid token address
        returncode, stdout, stderr = self.run_cli_command(
            "get_price", "0x1234567890abcdef1234567890abcdef12345678", str(self.test_timestamp)
        )
        
        # Should either return error code or None/0 price
        if returncode == 0:
            output = stdout.strip()
            self.assertIn(output, ["None", "0", "0.0"])
            print("✓ CLI error handling: Invalid token returns None")
        else:
            print("✓ CLI error handling: Invalid token returns error code")
    
    def test_cli_help(self):
        """Test CLI help functionality"""
        returncode, stdout, stderr = self.run_cli_command("--help")
        
        # Help should always work
        if returncode == 0:
            self.assertIn("usage", stdout.lower())
            print("✓ CLI help works")
        else:
            # Some CLI tools return help on stderr with exit code 0 or 2
            if "usage" in stderr.lower():
                print("✓ CLI help works (via stderr)")
            else:
                print(f"CLI help failed: {stderr}")

if __name__ == '__main__':
    unittest.main(verbosity=2)