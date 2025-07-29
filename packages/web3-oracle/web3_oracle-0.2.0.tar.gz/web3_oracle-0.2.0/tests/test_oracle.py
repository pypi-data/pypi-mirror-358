#!/usr/bin/env python3
"""
Comprehensive unit tests for the web3_oracle package
"""

import unittest
import os
from datetime import datetime
import pytz
from pathlib import Path
import sys

# Add the parent directory to the path so we can import the oracle module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from web3_oracle.oracle import Oracle

class TestOracle(unittest.TestCase):
    """Comprehensive test cases for the Oracle class"""
    
    def setUp(self):
        """Set up test environment with real data files"""
        # Use the real data directory from the package
        self.oracle = Oracle(verbose=True)
        
        # Common test addresses
        self.eth_address = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
        self.btc_address = "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599"
        self.uni_address = "0x1f9840a85d5af5bf1d1762f925bdaddc4201f984"
        self.usdc_address = "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
        
        # Common test timestamps
        self.test_timestamp = 1747224000  # Recent timestamp from data
        self.test_block = 15000000  # Test block number
    
    def test_oracle_initialization(self):
        """Test that Oracle initializes correctly with real data"""
        self.assertIsInstance(self.oracle, Oracle)
        self.assertIsInstance(self.oracle.token_mapping, dict)
        self.assertGreater(len(self.oracle.token_mapping), 0)
        
        # Check that data structures are initialized
        self.assertIsInstance(self.oracle.price_cache, dict)
        self.assertIsInstance(self.oracle.reference_prices, dict)
        self.assertIsInstance(self.oracle.block_prices, dict)
        self.assertIsInstance(self.oracle.btc_block_prices, dict)
        
    def test_token_mapping_loaded(self):
        """Test that token mapping is loaded correctly"""
        # Check that ETH/WETH is in the mapping
        self.assertIn(self.eth_address, self.oracle.token_mapping)
        self.assertEqual(self.oracle.token_mapping[self.eth_address]['symbol'], 'ETH')
        
        # Check that BTC/WBTC is in the mapping
        self.assertIn(self.btc_address, self.oracle.token_mapping)
        self.assertEqual(self.oracle.token_mapping[self.btc_address]['symbol'], 'BTC')
    
    # Test new direct ETH/BTC price lookup methods
    def test_get_eth_price_by_timestamp(self):
        """Test getting ETH price directly by timestamp"""
        price = self.oracle.get_eth_price_by_timestamp(self.test_timestamp)
        self.assertIsNotNone(price)
        self.assertIsInstance(price, float)
        self.assertGreater(price, 0)
        print(f"ETH price at timestamp {self.test_timestamp}: ${price:.2f}")
    
    def test_get_btc_price_by_timestamp(self):
        """Test getting BTC price directly by timestamp"""
        price = self.oracle.get_btc_price_by_timestamp(self.test_timestamp)
        self.assertIsNotNone(price)
        self.assertIsInstance(price, float)
        self.assertGreater(price, 0)
        print(f"BTC price at timestamp {self.test_timestamp}: ${price:.2f}")
    
    def test_get_price_eth_legacy(self):
        """Test getting ETH price by timestamp using legacy method"""
        price = self.oracle.get_price(self.eth_address, self.test_timestamp)
        self.assertIsNotNone(price)
        self.assertIsInstance(price, float)
        self.assertGreater(price, 0)
    
    def test_get_price_btc_legacy(self):
        """Test getting BTC price by timestamp using legacy method"""
        price = self.oracle.get_price(self.btc_address, self.test_timestamp)
        self.assertIsNotNone(price)
        self.assertIsInstance(price, float)
        self.assertGreater(price, 0)
    
    def test_get_price_by_datetime(self):
        """Test getting price by datetime"""
        dt = datetime.fromtimestamp(self.test_timestamp, tz=pytz.UTC)
        price = self.oracle.get_price_by_datetime(self.eth_address, dt)
        self.assertIsNotNone(price)
        self.assertIsInstance(price, float)
        self.assertGreater(price, 0)
    
    def test_get_price_by_datetime_timezone_aware(self):
        """Test getting price by timezone-aware datetime"""
        dt = datetime.fromtimestamp(self.test_timestamp, tz=pytz.UTC)
        price = self.oracle.get_price_by_datetime(self.eth_address, dt)
        self.assertIsNotNone(price)
        self.assertIsInstance(price, float)
        self.assertGreater(price, 0)
    
    def test_fast_price_eth_block_10000_logic(self):
        """Test fast ETH price lookup by block (uses block/10000 logic)"""
        block_number = 15000000
        price = self.oracle.fast_price(block_number)
        if self.oracle.block_prices:  # Only test if block prices are available
            self.assertIsNotNone(price)
            self.assertIsInstance(price, float)
            self.assertGreater(price, 0)
            print(f"ETH fast price at block {block_number}: ${price:.2f}")
        else:
            print("ETH block prices not available, skipping test")
    
    def test_fast_btc_price_block_100_logic(self):
        """Test fast BTC price lookup by block (uses block/100 logic)"""
        block_number = 15000000
        price = self.oracle.fast_btc_price(block_number)
        if self.oracle.btc_block_prices:  # Only test if BTC block prices are available
            self.assertIsNotNone(price)
            self.assertIsInstance(price, float)
            self.assertGreater(price, 0)
            print(f"BTC fast price at block {block_number}: ${price:.2f}")
        else:
            print("BTC block prices not available, skipping test")
    
    def test_btc_block_rounding_logic(self):
        """Test that BTC block rounding uses /100 logic correctly"""
        if not self.oracle.btc_block_prices:
            self.skipTest("BTC block prices not available")
        
        # Test that different blocks in the same 100-block range return same price
        base_block = 15000000
        price1 = self.oracle.fast_btc_price(base_block)
        price2 = self.oracle.fast_btc_price(base_block + 50)  # Within same 100-block range
        price3 = self.oracle.fast_btc_price(base_block + 99)  # Still within range
        
        self.assertEqual(price1, price2)
        self.assertEqual(price2, price3)
        print(f"BTC block rounding test: blocks {base_block}, {base_block+50}, {base_block+99} all return ${price1:.2f}")
    
    def test_get_price_by_block_eth(self):
        """Test getting ETH price by block number"""
        price = self.oracle.get_price_by_block(self.eth_address, self.test_block)
        if self.oracle.block_prices:  # Only test if block prices are available
            self.assertIsNotNone(price)
            self.assertIsInstance(price, float)
            self.assertGreater(price, 0)
    
    def test_get_price_by_block_btc(self):
        """Test getting BTC price by block number"""
        price = self.oracle.get_price_by_block(self.btc_address, self.test_block)
        if self.oracle.btc_block_prices:  # Only test if BTC block prices are available
            self.assertIsNotNone(price)
            self.assertIsInstance(price, float)
            self.assertGreater(price, 0)
    
    def test_get_price_by_block_unsupported_token(self):
        """Test getting price by block for unsupported token (should return None)"""
        price = self.oracle.get_price_by_block(self.usdc_address, self.test_block)
        self.assertIsNone(price)
    
    def test_get_reference_price_altcoins(self):
        """Test getting reference price for altcoins (latest price)"""
        price = self.oracle.get_reference_price(self.uni_address)
        if self.oracle.reference_prices:  # Only test if reference prices are available
            self.assertIsNotNone(price)
            self.assertIsInstance(price, float)
            self.assertGreater(price, 0)
            print(f"UNI reference price: ${price:.6f}")
        else:
            print("Reference prices not available, skipping test")
    
    def test_get_reference_price_multiple_tokens(self):
        """Test getting reference prices for multiple altcoins"""
        if not self.oracle.reference_prices:
            self.skipTest("Reference prices not available")
        
        # Test multiple tokens from reference prices
        test_addresses = list(self.oracle.reference_prices.keys())[:3]
        for address in test_addresses:
            price = self.oracle.get_reference_price(address)
            self.assertIsNotNone(price)
            self.assertIsInstance(price, float)
            self.assertGreater(price, 0)
            print(f"Reference price for {address}: ${price:.6f}")
    
    def test_get_token_price_unified_eth_block(self):
        """Test unified token price lookup for ETH with block number (priority 1)"""
        price = self.oracle.get_token_price(self.eth_address, block_number=self.test_block)
        self.assertIsNotNone(price)
        self.assertIsInstance(price, float)
        self.assertGreater(price, 0)
        print(f"ETH unified price (block {self.test_block}): ${price:.2f}")
    
    def test_get_token_price_unified_btc_block(self):
        """Test unified token price lookup for BTC with block number (priority 2)"""
        price = self.oracle.get_token_price(self.btc_address, block_number=self.test_block)
        self.assertIsNotNone(price)
        self.assertIsInstance(price, float)
        self.assertGreater(price, 0)
        print(f"BTC unified price (block {self.test_block}): ${price:.2f}")
    
    def test_get_token_price_unified_reference(self):
        """Test unified token price lookup using reference price (priority 3)"""
        price = self.oracle.get_token_price(self.uni_address)
        if self.oracle.reference_prices:  # Only test if reference prices are available
            self.assertIsNotNone(price)
            self.assertIsInstance(price, float)
            self.assertGreater(price, 0)
            print(f"UNI unified price (reference): ${price:.6f}")
    
    def test_get_token_price_unified_timestamp(self):
        """Test unified token price lookup with timestamp (priority 5)"""
        price = self.oracle.get_token_price(self.eth_address, timestamp=self.test_timestamp)
        self.assertIsNotNone(price)
        self.assertIsInstance(price, float)
        self.assertGreater(price, 0)
        print(f"ETH unified price (timestamp {self.test_timestamp}): ${price:.2f}")
    
    def test_unified_price_priority_order(self):
        """Test that unified price method follows correct priority order"""
        # Test that ETH with block number uses direct block mapping (priority 1)
        if self.oracle.block_prices:
            block_price = self.oracle.get_token_price(self.eth_address, block_number=self.test_block)
            direct_block_price = self.oracle.fast_price(self.test_block)
            self.assertEqual(block_price, direct_block_price)
            print(f"ETH priority test: block method returns ${block_price:.2f}")
        
        # Test that BTC with block number uses direct block mapping (priority 2)
        if self.oracle.btc_block_prices:
            block_price = self.oracle.get_token_price(self.btc_address, block_number=self.test_block)
            direct_block_price = self.oracle.fast_btc_price(self.test_block)
            self.assertEqual(block_price, direct_block_price)
            print(f"BTC priority test: block method returns ${block_price:.2f}")
        
        # Test that altcoin uses reference price (priority 3)
        if self.oracle.reference_prices and self.uni_address in self.oracle.reference_prices:
            unified_price = self.oracle.get_token_price(self.uni_address)
            reference_price = self.oracle.get_reference_price(self.uni_address)
            self.assertEqual(unified_price, reference_price)
            print(f"UNI priority test: reference method returns ${unified_price:.6f}")
    
    def test_get_token_info(self):
        """Test getting token info"""
        info = self.oracle.get_token_info(self.eth_address)
        self.assertIsNotNone(info)
        self.assertEqual(info['symbol'], 'ETH')
        self.assertIn('name', info)
    
    def test_nonexistent_token(self):
        """Test getting price for nonexistent token"""
        fake_address = "0x1234567890abcdef1234567890abcdef12345678"
        price = self.oracle.get_price(fake_address, self.test_timestamp)
        self.assertIsNone(price)
        
        info = self.oracle.get_token_info(fake_address)
        self.assertIsNone(info)
        
        # Test with new methods
        ref_price = self.oracle.get_reference_price(fake_address)
        self.assertIsNone(ref_price)
    
    def test_get_available_tokens(self):
        """Test getting available tokens"""
        tokens = self.oracle.get_available_tokens()
        self.assertIsInstance(tokens, dict)
        self.assertGreater(len(tokens), 0)
        
        # Check that ETH is in available tokens
        self.assertIn(self.eth_address, tokens)
        self.assertEqual(tokens[self.eth_address]['symbol'], 'ETH')
        
        print(f"\nAvailable tokens ({len(tokens)}):")
        for addr, info in list(tokens.items())[:5]:
            print(f"  {info['symbol']}: {addr}")
    
    def test_data_loading_capabilities(self):
        """Test that data loading capabilities are properly reported"""
        print(f"\nData availability:")
        print(f"  ETH block prices: {len(self.oracle.block_prices)} entries")
        print(f"  BTC block prices: {len(self.oracle.btc_block_prices)} entries")
        print(f"  Reference prices: {len(self.oracle.reference_prices)} entries")
        print(f"  Token mappings: {len(self.oracle.token_mapping)} entries")
        
        # At minimum, we should have token mappings
        self.assertGreater(len(self.oracle.token_mapping), 0)
        
        # Show sample reference prices if available
        if self.oracle.reference_prices:
            print(f"\nSample reference prices:")
            for addr, price in list(self.oracle.reference_prices.items())[:3]:
                symbol = self.oracle.token_mapping.get(addr, {}).get('symbol', 'Unknown')
                print(f"  {symbol} ({addr}): ${price:.6f}")
    
    def test_consistency_between_methods(self):
        """Test consistency between different price lookup methods"""
        # Test ETH price consistency
        eth_price_legacy = self.oracle.get_price(self.eth_address, self.test_timestamp)
        eth_price_direct = self.oracle.get_eth_price_by_timestamp(self.test_timestamp)
        
        # Note: unified method may use reference price instead of timestamp due to priority order
        # So we test legacy vs direct methods which should be identical
        self.assertEqual(eth_price_legacy, eth_price_direct)
        print(f"ETH price consistency (legacy vs direct): ${eth_price_legacy:.2f}")
        
        # Test BTC price consistency
        btc_price_legacy = self.oracle.get_price(self.btc_address, self.test_timestamp)
        btc_price_direct = self.oracle.get_btc_price_by_timestamp(self.test_timestamp)
        
        self.assertEqual(btc_price_legacy, btc_price_direct)
        print(f"BTC price consistency (legacy vs direct): ${btc_price_legacy:.2f}")
        
        # Test that unified method works (may use different priority)
        eth_price_unified = self.oracle.get_token_price(self.eth_address, timestamp=self.test_timestamp)
        btc_price_unified = self.oracle.get_token_price(self.btc_address, timestamp=self.test_timestamp)
        
        # Unified method should return valid prices (may be different due to priority)
        self.assertIsNotNone(eth_price_unified)
        self.assertIsNotNone(btc_price_unified)
        print(f"ETH unified method: ${eth_price_unified:.2f}")
        print(f"BTC unified method: ${btc_price_unified:.2f}")
    
    def test_datetime_functionality(self):
        """Test datetime-based price lookups"""
        dt = datetime.fromtimestamp(self.test_timestamp, tz=pytz.UTC)
        
        # Test ETH price by datetime
        price_by_dt = self.oracle.get_price_by_datetime(self.eth_address, dt)
        price_by_ts = self.oracle.get_price(self.eth_address, self.test_timestamp)
        
        self.assertEqual(price_by_dt, price_by_ts)
        print(f"ETH datetime test: ${price_by_dt:.2f} at {dt}")
        
        # Test with naive datetime (should be treated as UTC)
        naive_dt = datetime.fromtimestamp(self.test_timestamp)
        price_naive = self.oracle.get_price_by_datetime(self.eth_address, naive_dt)
        self.assertEqual(price_naive, price_by_ts)
    
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        # Test with very old timestamp
        old_timestamp = 1000000000  # Year 2001
        price = self.oracle.get_eth_price_by_timestamp(old_timestamp)
        if price is not None:
            self.assertGreater(price, 0)
            print(f"Old timestamp test: ${price:.2f}")
        
        # Test with future timestamp
        future_timestamp = 2000000000  # Year 2033
        price = self.oracle.get_btc_price_by_timestamp(future_timestamp)
        if price is not None:
            self.assertGreater(price, 0)
            print(f"Future timestamp test: ${price:.2f}")
        
        # Test with zero block number
        if self.oracle.block_prices:
            price = self.oracle.fast_price(0)
            if price is not None:
                self.assertGreater(price, 0)
                print(f"Block 0 test: ${price:.2f}")
    
    def test_case_insensitive_addresses(self):
        """Test that token addresses are case-insensitive"""
        # Test with uppercase address
        upper_address = self.eth_address.upper()
        price_lower = self.oracle.get_price(self.eth_address, self.test_timestamp)
        price_upper = self.oracle.get_price(upper_address, self.test_timestamp)
        
        self.assertEqual(price_lower, price_upper)
        print(f"Case insensitive test: ${price_lower:.2f} (both cases)")

if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)