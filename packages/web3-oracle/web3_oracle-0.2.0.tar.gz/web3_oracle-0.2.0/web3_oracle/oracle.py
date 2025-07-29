#!/usr/bin/env python3
"""
Oracle Module - Retrieves token prices based on timestamps or datetime objects

Usage:
    from web3_oracle import Oracle
    from datetime import datetime

    # Initialize the oracle
    oracle = Oracle()

    # Get price by timestamp
    eth_price = oracle.get_price("0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2", 1620518400)

    # Get price by datetime
    dt = datetime(2022, 1, 15, 12, 0, 0)
    btc_price = oracle.get_price_by_datetime("0x2260fac5e5542a773aa44fbcfedf7c193bc2c599", dt)
    
    # Get reference price for less common tokens
    uni_price = oracle.get_reference_price("0x1f9840a85d5af5bf1d1762f925bdaddc4201f984")
    
    # Get Ethereum price by block number
    eth_block_price = oracle.get_price_by_block("0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2", 15000000)
    
    # Use the unified method for any token price (with priority and fallback)
    # This will use block prices for fast WETH lookup or reference prices for altcoins
    token_price = oracle.get_token_price(token_address="0x1f9840a85d5af5bf1d1762f925bdaddc4201f984", block_number=15000000)
"""

import os
import pandas as pd
import bisect
from datetime import datetime
import pytz
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Oracle:
    """
    Oracle class for retrieving token prices by timestamp, datetime, or block number
    """
    
    def __init__(self, data_dir: Optional[str] = None, verbose: bool = False):
        """
        Initialize the Oracle with token data
        
        Args:
            data_dir: Optional directory path where CSV files are stored. 
                     If None, uses the package's data directory.
            verbose: If True, display detailed initialization logs
        """
        if data_dir is None:
            # Use the package's data directory
            self.data_dir = Path(os.path.dirname(os.path.abspath(__file__))) / 'data'
        else:
            self.data_dir = Path(data_dir)
        
        # Load token address mapping
        self.token_mapping = self._load_token_mapping()
        
        # Load block price mapping for fast lookups
        self.block_prices = self._load_block_prices()
        
        # Load BTC block price mapping for fast lookups
        self.btc_block_prices = self._load_btc_block_prices()
        
        # Cache for price dataframes
        self.price_cache: Dict[str, pd.DataFrame] = {}
        
        # Cache for altcoin reference prices
        self.reference_prices = self._load_reference_prices()
        
        # WETH token address (lowercase for consistency)
        self.weth_address = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2".lower()
        
        # WBTC token address (lowercase for consistency)
        self.wbtc_address = "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599".lower()
        
        if verbose:
            logger.info(f"Oracle initialized with {len(self.token_mapping)} tokens and {len(self.reference_prices)} reference prices")
            logger.info(f"Block price mapping has {len(self.block_prices)} entries for fast ETH price lookups")
            logger.info(f"BTC block price mapping has {len(self.btc_block_prices)} entries for fast BTC price lookups")
    
    def _load_token_mapping(self) -> Dict[str, Dict]:
        """
        Load the token address to price file mapping
        
        Returns:
            Dict: Dictionary mapping token addresses to token information
        """
        mapping_file = self.data_dir / 'token_addresses.csv'
        
        if not mapping_file.exists():
            raise FileNotFoundError(f"Token mapping file not found at {mapping_file}")
        
        df = pd.read_csv(mapping_file)
        
        # Convert to dictionary with address as key
        token_mapping = {}
        for _, row in df.iterrows():
            # Convert addresses to lowercase for case-insensitive comparison
            address = row['address'].lower()
            token_mapping[address] = {
                'symbol': row['symbol'],
                'name': row['name'],
                'price_file': row['price_file']
            }
        
        return token_mapping
    
    def _load_block_prices(self) -> Dict[int, float]:
        """
        Load the direct mapping of block numbers to ETH prices
        
        Returns:
            Dict: Dictionary mapping block numbers to ETH prices
        """
        block_price_file = self.data_dir / 'eth_block_prices.csv'
        
        if not block_price_file.exists():
            logger.warning(f"Block prices file not found at {block_price_file}. Fast price lookup will not be available.")
            return {}
        
        try:
            df = pd.read_csv(block_price_file)
            return dict(zip(df['block_number'], df['eth_price']))
        except Exception as e:
            logger.error(f"Error loading block prices: {e}")
            return {}
    
    def _load_btc_block_prices(self) -> Dict[int, float]:
        """
        Load the direct mapping of block numbers to BTC prices
        
        Returns:
            Dict: Dictionary mapping block numbers to BTC prices
        """
        btc_block_price_file = self.data_dir / 'btc_block_prices.csv'
        
        if not btc_block_price_file.exists():
            logger.warning(f"BTC block prices file not found at {btc_block_price_file}. Fast BTC price lookup will not be available.")
            return {}
        
        try:
            df = pd.read_csv(btc_block_price_file)
            return dict(zip(df['block_number'], df['btc_price']))
        except Exception as e:
            logger.error(f"Error loading BTC block prices: {e}")
            return {}
    
    def _load_reference_prices(self) -> Dict[str, float]:
        """
        Load reference prices for altcoins
        
        Returns:
            Dict: Dictionary mapping token addresses to their reference prices
        """
        reference_file = self.data_dir / 'altcoins_prices.csv'
        
        if not reference_file.exists():
            logger.warning(f"Reference price file not found at {reference_file}. Reference prices will not be available.")
            return {}
        
        try:
            df = pd.read_csv(reference_file)
            
            # Create a mapping of addresses to their most recent price
            reference_prices = {}
            for _, row in df.iterrows():
                # Convert addresses to lowercase for case-insensitive comparison
                address = row['address'].lower()
                reference_prices[address] = float(row['price'])
            
            return reference_prices
        except Exception as e:
            logger.error(f"Error loading reference prices: {e}")
            return {}
    
    def _load_price_data(self, price_file: str) -> pd.DataFrame:
        """
        Load price data from CSV file
        
        Args:
            price_file: Name of the price file
            
        Returns:
            DataFrame: Price data with timestamp as index
        """
        # Check if the data is already loaded in cache
        if price_file in self.price_cache:
            return self.price_cache[price_file]
        
        file_path = self.data_dir / price_file
        
        if not file_path.exists():
            raise FileNotFoundError(f"Price file not found at {file_path}")
        
        # Load the CSV file
        df = pd.read_csv(file_path)
        
        # Sort by timestamp
        df = df.sort_values('timestamp')
        
        # Cache the dataframe
        self.price_cache[price_file] = df
        
        return df
    
    def _find_closest_price(self, df: pd.DataFrame, timestamp: int) -> float:
        """
        Find the closest price to the given timestamp
        
        Args:
            df: DataFrame containing price data
            timestamp: Unix timestamp to find price for
            
        Returns:
            float: Price at or closest to the timestamp
        """
        timestamps = df['timestamp'].values
        
        # Find the index of the timestamp that is greater than or equal to the target
        idx = bisect.bisect_left(timestamps, timestamp)
        
        # If the timestamp is exactly found or we're at the beginning
        if idx < len(timestamps) and timestamps[idx] == timestamp:
            return df.iloc[idx]['price']
        
        # If we're beyond the last timestamp, return the last price
        if idx >= len(timestamps):
            return df.iloc[-1]['price']
        
        # If we're at the beginning, return the first price
        if idx == 0:
            return df.iloc[0]['price']
        
        # Find the closest timestamp (either before or after)
        prev_idx = idx - 1
        if abs(timestamps[prev_idx] - timestamp) <= abs(timestamps[idx] - timestamp):
            return df.iloc[prev_idx]['price']
        else:
            return df.iloc[idx]['price']
    
    def _find_latest_price_before(self, df: pd.DataFrame, timestamp: int) -> float:
        """
        Find the latest price before the given timestamp
        
        Args:
            df: DataFrame containing price data
            timestamp: Unix timestamp to find price for
            
        Returns:
            float: Price at the latest timestamp before the given timestamp
        """
        timestamps = df['timestamp'].values
        
        # Find the index of the timestamp that is greater than or equal to the target
        idx = bisect.bisect_left(timestamps, timestamp)
        
        # If the timestamp is exactly found, return the price at that timestamp
        if idx < len(timestamps) and timestamps[idx] == timestamp:
            return df.iloc[idx]['price']
        
        # If we're at the beginning, use the first available price
        if idx == 0:
            logger.warning(f"Timestamp {timestamp} is before any available price data. Using earliest price.")
            return df.iloc[0]['price']
        
        # Otherwise, return the price at the latest timestamp before the given timestamp
        return df.iloc[idx - 1]['price']
    
    def _find_closest_block_price(self, block_number: int) -> Optional[float]:
        """
        Find the closest ETH price for a block number using the direct mapping
        
        Args:
            block_number: Ethereum block number
            
        Returns:
            float or None: ETH price at the closest block, or None if not available
        """
        if not self.block_prices:
            logger.warning("Block prices not loaded. Cannot find direct price for block.")
            return None
        
        # Round to nearest 10,000 block for faster lookups
        rounded_block = round(block_number / 10000) * 10000
        
        # If the rounded block is in our mapping, return the price directly
        if rounded_block in self.block_prices:
            return self.block_prices[rounded_block]
        
        # Find the closest available block
        blocks = sorted(self.block_prices.keys())
        idx = bisect.bisect_left(blocks, rounded_block)
        
        # If beyond the last block, use the last price
        if idx >= len(blocks):
            return self.block_prices[blocks[-1]]
        
        # If at the beginning, use the first price
        if idx == 0:
            return self.block_prices[blocks[0]]
        
        # Find the closest block (either before or after)
        prev_block = blocks[idx - 1]
        current_block = blocks[idx]
        
        if abs(prev_block - rounded_block) <= abs(current_block - rounded_block):
            return self.block_prices[prev_block]
        else:
            return self.block_prices[current_block]
    
    def get_price(self, token_address: str, timestamp: int) -> Optional[float]:
        """
        Get token price at the specified timestamp
        
        Args:
            token_address: Ethereum token contract address
            timestamp: Unix timestamp
            
        Returns:
            float: Token price at the timestamp, or None if not found
        """
        # Convert address to lowercase for case-insensitive lookup
        token_address = token_address.lower()
        
        if token_address not in self.token_mapping:
            logger.warning(f"Token address {token_address} not found in mapping")
            return None
        
        token_info = self.token_mapping[token_address]
        price_file = token_info['price_file']
        
        try:
            df = self._load_price_data(price_file)
            price = self._find_closest_price(df, timestamp)
            return price
        except FileNotFoundError as e:
            logger.error(f"Error fetching price data: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None
    
    def get_price_by_datetime(self, token_address: str, dt: datetime) -> Optional[float]:
        """
        Get token price at the specified datetime
        
        Args:
            token_address: Ethereum token contract address
            dt: Datetime object (naive datetimes are assumed to be in UTC)
            
        Returns:
            float: Token price at the datetime, or None if not found
        """
        # Ensure datetime is timezone-aware and convert to UTC
        if dt.tzinfo is None:
            dt = pytz.UTC.localize(dt)
        else:
            dt = dt.astimezone(pytz.UTC)
        
        # Convert to unix timestamp
        timestamp = int(dt.timestamp())
        
        return self.get_price(token_address, timestamp)
    
    def get_token_info(self, token_address: str) -> Optional[Dict]:
        """
        Get information about a token
        
        Args:
            token_address: Ethereum token contract address
            
        Returns:
            Dict: Token information including symbol and name, or None if not found
        """
        # Convert address to lowercase for case-insensitive lookup
        token_address = token_address.lower()
        
        if token_address not in self.token_mapping:
            return None
        
        return {
            'symbol': self.token_mapping[token_address]['symbol'],
            'name': self.token_mapping[token_address]['name']
        }
    
    def get_available_tokens(self) -> Dict[str, Dict]:
        """
        Get all available tokens
        
        Returns:
            Dict: Dictionary mapping token addresses to token information
        """
        return {addr: {'symbol': info['symbol'], 'name': info['name']} 
                for addr, info in self.token_mapping.items()}
    
    def get_reference_price(self, token_address: str) -> Optional[float]:
        """
        Get the reference price for a token from the altcoins_prices.csv
        
        Args:
            token_address: Ethereum token contract address
            
        Returns:
            float: Reference price for the token, or None if not found
        """
        # Convert address to lowercase for case-insensitive lookup
        token_address = token_address.lower()
        
        if token_address in self.reference_prices:
            return self.reference_prices[token_address]
        
        logger.warning(f"No reference price found for token {token_address}")
        return None
    
    def get_price_by_block(self, token_address: str, block_number: int) -> Optional[float]:
        """
        Get token price at the specified Ethereum block number
        
        Note: This method only works for WETH and WBTC tokens that have direct 
        block-to-price mappings. For other tokens, use get_token_price() instead.
        
        Args:
            token_address: Ethereum token contract address
            block_number: Ethereum block number
            
        Returns:
            float: Token price at the block, or None if not found
        """
        # Convert address to lowercase for case-insensitive lookup
        token_address = token_address.lower()
        
        # Only ETH and BTC have direct block-to-price mappings
        if token_address == self.weth_address and self.block_prices:
            return self._find_closest_block_price(block_number)
        elif token_address == self.wbtc_address and self.btc_block_prices:
            return self._find_closest_btc_block_price(block_number)
        else:
            logger.warning(f"get_price_by_block only supports WETH and WBTC. For token {token_address}, use get_token_price() instead.")
            return None
    
    def fast_price(self, block_number: int) -> Optional[float]:
        """
        Get Ethereum price at a specific block number (fast lookup)
        Method for quickly looking up ETH price at block rounded to nearest 10,000
        
        Args:
            block_number: Ethereum block number
            
        Returns:
            float: Ethereum price at the block, or None if not found
        """
        # Round to nearest 10,000 block for faster lookups
        rounded_block = round(block_number / 10000) * 10000
        
        # Direct lookup using block price mapping (doesn't require timestamps)
        return self._find_closest_block_price(rounded_block)
    
    def _find_closest_btc_block_price(self, block_number: int) -> Optional[float]:
        """
        Find the closest BTC price for a given block number
        
        Args:
            block_number: Ethereum block number
            
        Returns:
            float: BTC price at the closest block, or None if not found
        """
        if not self.btc_block_prices:
            logger.warning("BTC block prices mapping is empty. Cannot perform fast lookup.")
            return None
        
        # Round to nearest 100 as per requirements
        rounded_block = round(block_number / 100) * 100
        
        # If we have an exact match for the rounded block, return it
        if rounded_block in self.btc_block_prices:
            return self.btc_block_prices[rounded_block]
        
        # Get all block numbers
        blocks = sorted(list(self.btc_block_prices.keys()))
        
        # If the requested block is before our earliest data
        if rounded_block < blocks[0]:
            logger.warning(f"Requested block {rounded_block} is before earliest available data at block {blocks[0]}")
            return self.btc_block_prices[blocks[0]]
        
        # If the requested block is after our latest data
        if rounded_block > blocks[-1]:
            logger.warning(f"Requested block {rounded_block} is after latest available data at block {blocks[-1]}")
            return self.btc_block_prices[blocks[-1]]
        
        # Find the index where the block would be inserted to maintain sorted order
        idx = bisect.bisect_left(blocks, rounded_block)
        
        # If we found an exact match
        if idx < len(blocks) and blocks[idx] == rounded_block:
            return self.btc_block_prices[blocks[idx]]
        
        # Find the closest block (either before or after)
        prev_block = blocks[idx - 1]
        current_block = blocks[idx]
        
        if abs(prev_block - rounded_block) <= abs(current_block - rounded_block):
            return self.btc_block_prices[prev_block]
        else:
            return self.btc_block_prices[current_block]
    
    def fast_btc_price(self, block_number: int) -> Optional[float]:
        """
        Get Bitcoin price at a specific block number (fast lookup)  
        Method for quickly looking up BTC price at block rounded to nearest 100
        
        Args:
            block_number: Ethereum block number
            
        Returns:
            float: Bitcoin price at the block, or None if not found
        """
        # Round to nearest 100 block as per requirements
        rounded_block = round(block_number / 100) * 100
        
        # Use the direct mapping for fast lookup
        return self._find_closest_btc_block_price(rounded_block)
    
    def get_eth_price_by_timestamp(self, timestamp: int) -> Optional[float]:
        """
        Get ETH price at the specified timestamp using ethereum_prices.csv
        
        Args:
            timestamp: Unix timestamp
            
        Returns:
            float: ETH price at the timestamp, or None if not found
        """
        try:
            df = self._load_price_data('ethereum_prices.csv')
            price = self._find_closest_price(df, timestamp)
            return price
        except FileNotFoundError as e:
            logger.error(f"Error fetching ETH price data: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting ETH price: {e}")
            return None
    
    def get_btc_price_by_timestamp(self, timestamp: int) -> Optional[float]:
        """
        Get BTC price at the specified timestamp using bitcoin_prices.csv
        
        Args:
            timestamp: Unix timestamp
            
        Returns:
            float: BTC price at the timestamp, or None if not found
        """
        try:
            df = self._load_price_data('bitcoin_prices.csv')
            price = self._find_closest_price(df, timestamp)
            return price
        except FileNotFoundError as e:
            logger.error(f"Error fetching BTC price data: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting BTC price: {e}")
            return None
    
    def get_token_price(self, token_address: str, block_number: Optional[int] = None, timestamp: Optional[int] = None) -> Optional[float]:
        """
        Unified method to get token price with optimal source selection.
        For WETH, uses direct block-price mapping for fast lookups.
        For WBTC, uses direct block-price mapping for fast lookups.
        For other tokens, uses reference price or fallbacks to timestamp-based lookup.
        
        Args:
            token_address: Ethereum token contract address
            block_number: Optional Ethereum block number
            timestamp: Optional Unix timestamp (used if block_number is None)
            
        Returns:
            float: Token price, or None if not found
            
        Priority:
        1. For WETH with block number: Direct block price mapping
        2. For WBTC with block number: Direct block price mapping
        3. For any token with reference price: Reference price
        4. For any token with block number: Convert to timestamp and lookup
        5. For any token with timestamp: Regular timestamp lookup
        """
        # Convert address to lowercase for case-insensitive lookup
        token_address = token_address.lower()
        
        # Case 1: WETH token with block number (fastest path)
        if token_address == self.weth_address and block_number is not None and self.block_prices:
            direct_price = self._find_closest_block_price(block_number)
            if direct_price is not None:
                return direct_price
        
        # Case 2: WBTC token with block number (fast path)
        if token_address == self.wbtc_address and block_number is not None and self.btc_block_prices:
            direct_price = self._find_closest_btc_block_price(block_number)
            if direct_price is not None:
                return direct_price
        
        # Case 3: Any token with reference price
        reference_price = self.get_reference_price(token_address)
        if reference_price is not None:
            return reference_price
            
        # Case 4: Block number lookup for other tokens
        if block_number is not None:
            return self.get_price_by_block(token_address, block_number)
        
        # Case 5: Timestamp lookup
        if timestamp is not None:
            return self.get_price(token_address, timestamp)
            
        # No valid inputs
        logger.warning(f"No valid inputs provided for token price lookup. Token: {token_address}")
        return None 