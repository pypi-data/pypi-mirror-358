#!/usr/bin/env python3
"""
Enhanced unit tests focusing on the three core features of web3_oracle package:
1. ETH/BTC price by timestamp
2. ETH/BTC price by block number  
3. Altcoin price using latest reference price
"""

import unittest
import os
import tempfile
import shutil
from datetime import datetime
import pandas as pd
import pytz
from pathlib import Path

from web3_oracle import Oracle

class TestOracleEnhanced(unittest.TestCase):
    """Enhanced test cases focusing on the three core features"""
    
    def setUp(self):
        """Set up test environment with mock data to test specific functionality"""
        # Create a temporary directory for test data
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = Path(self.temp_dir) / 'data'
        self.data_dir.mkdir(exist_ok=True)
        
        # Create sample token addresses CSV
        token_addresses = pd.DataFrame({
            'address': [
                '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2',  # ETH
                '0x2260fac5e5542a773aa44fbcfedf7c193bc2c599',  # BTC
                '0x1f9840a85d5af5bf1d1762f925bdaddc4201f984',  # UNI
                '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48'   # USDC
            ],
            'symbol': ['ETH', 'BTC', 'UNI', 'USDC'],
            'name': ['Ethereum', 'Bitcoin', 'Uniswap', 'USD Coin'],
            'price_file': ['ethereum_prices.csv', 'bitcoin_prices.csv', 'ethereum_prices.csv', 'stable_prices.csv']
        })
        token_addresses.to_csv(self.data_dir / 'token_addresses.csv', index=False)
        
        # Create sample ETH price data (Feature 1: ETH price by timestamp)
        eth_prices = pd.DataFrame({
            'timestamp': [1640995200, 1641081600, 1641168000, 1641254400, 1641340800],  # Jan 2022
            'price': [3700.12, 3850.45, 3920.78, 4100.23, 4250.67],
            'volume': [1000000, 1100000, 1200000, 1300000, 1400000]
        })
        eth_prices.to_csv(self.data_dir / 'ethereum_prices.csv', index=False)
        
        # Create sample BTC price data (Feature 1: BTC price by timestamp)
        btc_prices = pd.DataFrame({
            'timestamp': [1640995200, 1641081600, 1641168000, 1641254400, 1641340800],  # Jan 2022
            'price': [47000.50, 48500.75, 49200.25, 50100.80, 51000.90],
            'volume': [5000000, 5500000, 6000000, 6500000, 7000000]
        })
        btc_prices.to_csv(self.data_dir / 'bitcoin_prices.csv', index=False)
        
        # Create sample ETH block prices (Feature 2: ETH price by block, using block/10000 logic)
        eth_block_prices = pd.DataFrame({
            'block_number': [14000000, 14010000, 14020000, 14030000, 14040000, 15000000, 15010000],
            'eth_price': [3700.12, 3750.30, 3800.45, 3850.60, 3900.75, 4100.23, 4150.40]
        })
        eth_block_prices.to_csv(self.data_dir / 'eth_block_prices.csv', index=False)
        
        # Create sample BTC block prices (Feature 2: BTC price by block, using block/100 logic)
        btc_block_prices = pd.DataFrame({
            'block_number': [14000000, 14000100, 14000200, 14000300, 14000400, 15000000, 15000100],
            'btc_price': [47000.50, 47100.60, 47200.70, 47300.80, 47400.90, 50100.80, 50200.90]
        })
        btc_block_prices.to_csv(self.data_dir / 'btc_block_prices.csv', index=False)
        
        # Create sample altcoin reference prices (Feature 3: Altcoin latest prices)
        altcoin_prices = pd.DataFrame({
            'address': [
                '0x1f9840a85d5af5bf1d1762f925bdaddc4201f984',  # UNI
                '0x514910771af9ca656af840dff83e8264ecf986ca',  # LINK  
                '0x95ad61b0a150d79219dcf64e1e6cc01f0b64c4ce'   # SHIB
            ],
            'price': [25.50, 15.75, 0.000025],
            'timestamp': [
                '2025-01-01T12:00:00',
                '2025-01-01T12:00:00', 
                '2025-01-01T12:00:00'
            ]
        })
        altcoin_prices.to_csv(self.data_dir / 'altcoins_prices.csv', index=False)
        
        # Create sample stable coin prices
        stable_prices = pd.DataFrame({
            'timestamp': [1640995200, 1641081600, 1641168000, 1641254400, 1641340800],
            'price': [1.0001, 0.9999, 1.0000, 0.9998, 1.0002],
            'volume': [100000000, 110000000, 120000000, 130000000, 140000000]
        })
        stable_prices.to_csv(self.data_dir / 'stable_prices.csv', index=False)
        
        # Initialize the oracle with the test data directory
        self.oracle = Oracle(data_dir=self.data_dir, verbose=True)
        
        # Test addresses
        self.eth_address = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
        self.btc_address = "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599"
        self.uni_address = "0x1f9840a85d5af5bf1d1762f925bdaddc4201f984"
    
    def tearDown(self):
        """Clean up temporary files"""
        shutil.rmtree(self.temp_dir)
    
    # FEATURE 1: ETH/BTC price by timestamp tests
    def test_feature_1_eth_price_by_timestamp(self):
        """Test Feature 1: ETH price by timestamp using ethereum_prices.csv"""
        timestamp = 1641081600  # Specific timestamp from our test data
        
        # Test new direct method
        price = self.oracle.get_eth_price_by_timestamp(timestamp)
        self.assertEqual(price, 3850.45)  # Expected price from our test data
        print(f"✓ ETH price by timestamp {timestamp}: ${price:.2f}")
        
        # Test legacy method for consistency
        legacy_price = self.oracle.get_price(self.eth_address, timestamp)
        self.assertEqual(price, legacy_price)
        print(f"✓ ETH legacy method consistency: ${legacy_price:.2f}")
    
    def test_feature_1_btc_price_by_timestamp(self):
        """Test Feature 1: BTC price by timestamp using bitcoin_prices.csv"""
        timestamp = 1641254400  # Specific timestamp from our test data
        
        # Test new direct method
        price = self.oracle.get_btc_price_by_timestamp(timestamp)
        self.assertEqual(price, 50100.80)  # Expected price from our test data
        print(f"✓ BTC price by timestamp {timestamp}: ${price:.2f}")
        
        # Test legacy method for consistency
        legacy_price = self.oracle.get_price(self.btc_address, timestamp)
        self.assertEqual(price, legacy_price)
        print(f"✓ BTC legacy method consistency: ${legacy_price:.2f}")
    
    def test_feature_1_closest_price_lookup(self):
        """Test that closest price is returned when exact timestamp not found"""
        # Use timestamp between two data points
        between_timestamp = 1641125000  # Between 1641081600 and 1641168000
        
        eth_price = self.oracle.get_eth_price_by_timestamp(between_timestamp)
        self.assertIn(eth_price, [3850.45, 3920.78])  # Should be one of the closest prices
        print(f"✓ ETH closest price for timestamp {between_timestamp}: ${eth_price:.2f}")
    
    # FEATURE 2: ETH/BTC price by block number tests
    def test_feature_2_eth_price_by_block_10000_logic(self):
        """Test Feature 2: ETH price by block number using block/10000 logic"""
        block_number = 15005000  # Should round to 15010000
        
        # Test fast price method
        price = self.oracle.fast_price(block_number)
        self.assertEqual(price, 4150.40)  # Expected price for block 15010000
        print(f"✓ ETH fast price for block {block_number} (rounds to 15010000): ${price:.2f}")
        
        # Test get_price_by_block method
        block_price = self.oracle.get_price_by_block(self.eth_address, block_number)
        self.assertEqual(price, block_price)
        print(f"✓ ETH block price consistency: ${block_price:.2f}")
    
    def test_feature_2_btc_price_by_block_100_logic(self):
        """Test Feature 2: BTC price by block number using block/100 logic"""
        block_number = 14000250  # Should round to 14000200
        
        # Test fast BTC price method
        price = self.oracle.fast_btc_price(block_number)
        self.assertEqual(price, 47200.70)  # Expected price for block 14000200
        print(f"✓ BTC fast price for block {block_number} (rounds to 14000200): ${price:.2f}")
        
        # Test get_price_by_block method
        block_price = self.oracle.get_price_by_block(self.btc_address, block_number)
        self.assertEqual(price, block_price)
        print(f"✓ BTC block price consistency: ${block_price:.2f}")
    
    def test_feature_2_block_rounding_logic(self):
        """Test that block rounding logic works correctly for ETH (10000) and BTC (100)"""
        # Test ETH block rounding (should use /10000)
        eth_blocks = [14005000, 14007500, 14009999]  # All should round to 14010000
        expected_eth_price = 3750.30
        
        for block in eth_blocks:
            price = self.oracle.fast_price(block)
            self.assertEqual(price, expected_eth_price)
        print(f"✓ ETH block rounding: blocks {eth_blocks} all return ${expected_eth_price:.2f}")
        
        # Test BTC block rounding (should use /100)
        btc_blocks = [14000150, 14000175, 14000199]  # All should round to 14000200
        expected_btc_price = 47200.70
        
        for block in btc_blocks:
            price = self.oracle.fast_btc_price(block)
            self.assertEqual(price, expected_btc_price)
        print(f"✓ BTC block rounding: blocks {btc_blocks} all return ${expected_btc_price:.2f}")
    
    # FEATURE 3: Altcoin price using latest reference price tests
    def test_feature_3_altcoin_latest_price(self):
        """Test Feature 3: Altcoin price using latest price from altcoins_prices.csv"""
        # Test UNI token reference price
        price = self.oracle.get_reference_price(self.uni_address)
        self.assertEqual(price, 25.50)  # Expected reference price from our test data
        print(f"✓ UNI reference price: ${price:.2f}")
        
        # Test that this is used by unified method
        unified_price = self.oracle.get_token_price(self.uni_address)
        self.assertEqual(price, unified_price)
        print(f"✓ UNI unified method uses reference price: ${unified_price:.2f}")
    
    def test_feature_3_multiple_altcoins(self):
        """Test reference prices for multiple altcoins"""
        test_cases = [
            ('0x1f9840a85d5af5bf1d1762f925bdaddc4201f984', 25.50),    # UNI
            ('0x514910771af9ca656af840dff83e8264ecf986ca', 15.75),    # LINK
            ('0x95ad61b0a150d79219dcf64e1e6cc01f0b64c4ce', 0.000025) # SHIB
        ]
        
        for address, expected_price in test_cases:
            price = self.oracle.get_reference_price(address)
            self.assertEqual(price, expected_price)
            print(f"✓ Reference price for {address}: ${price:.6f}")
    
    def test_feature_3_nonexistent_altcoin(self):
        """Test that nonexistent altcoin returns None"""
        fake_address = "0x1234567890abcdef1234567890abcdef12345678"
        price = self.oracle.get_reference_price(fake_address)
        self.assertIsNone(price)
        print(f"✓ Nonexistent altcoin correctly returns None")
    
    # UNIFIED METHOD PRIORITY TESTS
    def test_unified_method_priority_order(self):
        """Test that get_token_price follows the correct priority order"""
        
        # Priority 1: WETH with block number -> Direct block price mapping
        eth_block_price = self.oracle.get_token_price(self.eth_address, block_number=15000000)
        direct_eth_price = self.oracle.fast_price(15000000)
        self.assertEqual(eth_block_price, direct_eth_price)
        print(f"✓ Priority 1 - ETH block price: ${eth_block_price:.2f}")
        
        # Priority 2: WBTC with block number -> Direct block price mapping  
        btc_block_price = self.oracle.get_token_price(self.btc_address, block_number=15000000)
        direct_btc_price = self.oracle.fast_btc_price(15000000)
        self.assertEqual(btc_block_price, direct_btc_price)
        print(f"✓ Priority 2 - BTC block price: ${btc_block_price:.2f}")
        
        # Priority 3: Any token with reference price -> Reference price
        uni_ref_price = self.oracle.get_token_price(self.uni_address)
        direct_ref_price = self.oracle.get_reference_price(self.uni_address)
        self.assertEqual(uni_ref_price, direct_ref_price)
        print(f"✓ Priority 3 - UNI reference price: ${uni_ref_price:.2f}")
        
        # Priority 5: Any token with timestamp -> Regular timestamp lookup
        eth_ts_price = self.oracle.get_token_price(self.eth_address, timestamp=1641081600)
        direct_ts_price = self.oracle.get_eth_price_by_timestamp(1641081600)
        self.assertEqual(eth_ts_price, direct_ts_price)
        print(f"✓ Priority 5 - ETH timestamp price: ${eth_ts_price:.2f}")
    
    # INTEGRATION TESTS
    def test_all_features_integration(self):
        """Integration test covering all three features"""
        print("\\n=== INTEGRATION TEST: All Three Features ===")
        
        # Feature 1: ETH/BTC by timestamp
        eth_ts = self.oracle.get_eth_price_by_timestamp(1641168000)
        btc_ts = self.oracle.get_btc_price_by_timestamp(1641168000)
        print(f"Feature 1 - ETH by timestamp: ${eth_ts:.2f}")
        print(f"Feature 1 - BTC by timestamp: ${btc_ts:.2f}")
        
        # Feature 2: ETH/BTC by block number
        eth_block = self.oracle.fast_price(14020000)
        btc_block = self.oracle.fast_btc_price(14000200)
        print(f"Feature 2 - ETH by block: ${eth_block:.2f}")
        print(f"Feature 2 - BTC by block: ${btc_block:.2f}")
        
        # Feature 3: Altcoin reference price
        uni_ref = self.oracle.get_reference_price(self.uni_address)
        print(f"Feature 3 - UNI reference: ${uni_ref:.2f}")
        
        # All should return valid prices
        self.assertIsNotNone(eth_ts)
        self.assertIsNotNone(btc_ts)
        self.assertIsNotNone(eth_block)
        self.assertIsNotNone(btc_block)
        self.assertIsNotNone(uni_ref)
        
        print("✓ All three features working correctly")
    
    def test_data_source_verification(self):
        """Verify that the correct data sources are being used"""
        # Verify ETH data comes from ethereum_prices.csv
        self.assertIn('ethereum_prices.csv', str(self.oracle.price_cache.keys()) if self.oracle.price_cache else "")
        
        # Verify BTC data comes from bitcoin_prices.csv  
        self.assertIn('bitcoin_prices.csv', str(self.oracle.price_cache.keys()) if self.oracle.price_cache else "")
        
        # Verify block prices are loaded
        self.assertGreater(len(self.oracle.block_prices), 0)
        self.assertGreater(len(self.oracle.btc_block_prices), 0)
        
        # Verify reference prices are loaded
        self.assertGreater(len(self.oracle.reference_prices), 0)
        
        print("✓ All data sources verified")
    
    def test_error_handling(self):
        """Test error handling for edge cases"""
        # Test with block numbers outside data range
        very_high_block = 99999999
        eth_price = self.oracle.fast_price(very_high_block)
        self.assertIsNotNone(eth_price)  # Should return closest available price
        
        # Test with very old timestamp
        old_timestamp = 1000000000
        eth_old = self.oracle.get_eth_price_by_timestamp(old_timestamp)
        self.assertIsNotNone(eth_old)  # Should return earliest available price
        
        print("✓ Error handling works correctly")

if __name__ == '__main__':
    unittest.main(verbosity=2)