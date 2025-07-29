#!/usr/bin/env python3
"""
BTC Block to Price Indexer

This script creates a mapping of Ethereum block numbers directly to BTC prices.
It uses a web3 node to fetch block timestamps and combines them with BTC price data.
Features parallel processing for accelerated data collection.

Usage:
    python -m web3_oracle.tools.index_btc_blocks [--output OUTPUT_FILE] [--node-url NODE_URL] [--price-file PRICE_FILE] [--workers WORKERS]

Args:
    --output: Path to save the output CSV file (default: ../data/btc_block_prices.csv)
    --node-url: Web3 node URL (default: http://192.168.0.105:8545)
    --price-file: Path to the BTC price data CSV file (default: ../data/bitcoin_prices.csv)
    --sample-interval: Block interval for sampling (default: 10000)
    --workers: Number of worker threads for parallel processing (default: 10)
"""

import argparse
import csv
import json
import os
import sys
import time
import concurrent.futures
from typing import Dict, List, Tuple, Optional
import pandas as pd
import bisect
from pathlib import Path
from web3 import Web3
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Block number ranges to sample
# We'll sample blocks at regular intervals
SAMPLE_RANGES = [
    (10000, 21000000, 10000),  # Sample every 10,000 blocks
]

# Special blocks to include regardless of sampling interval
# These are important blocks that we want to ensure are in the dataset
SPECIAL_BLOCKS = [
    18039284,  # Special block from requirements
    19302940,  # Special block from requirements
]

def get_block_timestamp_from_web3(args) -> Tuple[int, int]:
    """
    Get the timestamp for a specific Ethereum block using web3
    
    Args:
        args: Tuple containing (block_number, w3)
        
    Returns:
        Tuple of (block_number, timestamp)
    """
    block_number, w3 = args
    try:
        block = w3.eth.get_block(block_number)
        timestamp = block.timestamp
        logger.info(f"Successfully fetched block {block_number} with timestamp {timestamp}")
        return block_number, timestamp
    except Exception as e:
        logger.error(f"Error getting block {block_number}: {str(e)}")
        return block_number, 0

def fetch_block_timestamps_parallel(w3: Web3, sample_interval: int = 10000, max_workers: int = 10) -> List[Tuple[int, int]]:
    """
    Fetch timestamps for a range of block numbers using parallel processing
    
    Args:
        w3: Web3 instance
        sample_interval: Interval for sampling blocks
        max_workers: Maximum number of worker threads
        
    Returns:
        List of (block_number, timestamp) tuples
    """
    # Get the latest block number
    try:
        latest_block = w3.eth.block_number
        logger.info(f"Latest block number: {latest_block}")
    except Exception as e:
        logger.error(f"Error getting latest block: {str(e)}")
        latest_block = 20000000  # Fallback to a reasonable value
    
    # Collect all block numbers to fetch
    blocks_to_fetch = []
    
    # Process standard ranges
    for start_block, end_block, step in SAMPLE_RANGES:
        # Skip ranges beyond the latest block
        if start_block > latest_block:
            continue
            
        # Cap end_block at latest_block
        end_block = min(end_block, latest_block)
        
        # Add blocks in range
        blocks_to_fetch.extend(range(start_block, end_block + 1, step))
    
    # Add special blocks that should be included regardless of sampling interval
    blocks_to_fetch.extend(SPECIAL_BLOCKS)
    
    # Remove duplicates and sort
    blocks_to_fetch = sorted(set(blocks_to_fetch))
    logger.info(f"Preparing to fetch {len(blocks_to_fetch)} blocks using {max_workers} worker threads")
    
    # Create arguments for the worker function
    args_list = [(block, w3) for block in blocks_to_fetch]
    block_timestamps = []
    
    # Use ThreadPoolExecutor for parallel processing
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit tasks in batches to avoid overwhelming the node
        batch_size = 50
        for i in range(0, len(args_list), batch_size):
            batch_args = args_list[i:i+batch_size]
            futures = [executor.submit(get_block_timestamp_from_web3, arg) for arg in batch_args]
            
            # Process completed futures
            for future in concurrent.futures.as_completed(futures):
                try:
                    block_number, timestamp = future.result()
                    if timestamp > 0:
                        block_timestamps.append((block_number, timestamp))
                except Exception as e:
                    logger.error(f"Error processing task: {str(e)}")
            
            # Small pause between batches
            if i + batch_size < len(args_list):
                logger.info(f"Processed {i + batch_size}/{len(args_list)} blocks. Pausing briefly...")
                time.sleep(1)
    
    # Sort by block number
    block_timestamps.sort(key=lambda x: x[0])
    logger.info(f"Successfully fetched {len(block_timestamps)} block timestamps")
    
    return block_timestamps

def load_price_data(price_file: str) -> pd.DataFrame:
    """
    Load BTC price data from CSV file
    
    Args:
        price_file: Path to the BTC price file
        
    Returns:
        DataFrame: Price data with timestamp as index
    """
    file_path = Path(price_file)
    
    if not file_path.exists():
        raise FileNotFoundError(f"BTC price file not found at {file_path}")
    
    # Load the CSV file
    df = pd.read_csv(file_path)
    
    # Bitcoin price data timestamps are typically in milliseconds, convert to seconds if needed
    if 'timestamp' in df.columns and df['timestamp'].iloc[0] > 1e12:
        logger.info("Converting timestamps from milliseconds to seconds")
        df['timestamp'] = df['timestamp'] // 1000
    
    # Sort by timestamp
    df = df.sort_values('timestamp')
    
    return df

def find_latest_price_before(df: pd.DataFrame, timestamp: int) -> float:
    """
    Find the latest BTC price before the given timestamp
    
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
        logger.warning(f"Timestamp {timestamp} is before any available BTC price data. Using earliest price.")
        return df.iloc[0]['price']
    
    # Otherwise, return the price at the latest timestamp before the given timestamp
    return df.iloc[idx - 1]['price']

def create_block_price_mapping(block_timestamps: List[Tuple[int, int]], price_data: pd.DataFrame) -> List[Tuple[int, float]]:
    """
    Create a mapping of block numbers to BTC prices
    
    Args:
        block_timestamps: List of (block_number, timestamp) tuples
        price_data: DataFrame with BTC price data
        
    Returns:
        List of (block_number, price) tuples
    """
    block_prices = []
    
    for block_number, timestamp in block_timestamps:
        price = find_latest_price_before(price_data, timestamp)
        block_prices.append((block_number, price))
        logger.debug(f"Block {block_number} with timestamp {timestamp} mapped to BTC price {price}")
        
    return block_prices

def write_csv(block_prices: List[Tuple[int, float]], output_file: str) -> None:
    """
    Write block prices to a CSV file
    
    Args:
        block_prices: List of (block_number, price) tuples
        output_file: Path to the output CSV file
    """
    # Ensure the directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['block_number', 'btc_price'])
        for block_number, price in block_prices:
            writer.writerow([block_number, price])

def main():
    parser = argparse.ArgumentParser(description='Index Ethereum blocks to BTC prices')
    parser.add_argument('--output', default='../data/btc_block_prices.csv',
                        help='Path to save the output CSV file')
    parser.add_argument('--node-url', default='http://192.168.0.105:8545',
                        help='Web3 node URL')
    parser.add_argument('--price-file', default='../data/bitcoin_prices.csv',
                        help='Path to the BTC price data CSV file')
    parser.add_argument('--sample-interval', type=int, default=10000,
                        help='Block interval for sampling')
    parser.add_argument('--workers', type=int, default=10,
                        help='Number of worker threads for parallel processing')
    args = parser.parse_args()
    
    try:
        # Connect to web3 node
        w3 = Web3(Web3.HTTPProvider(args.node_url))
        if not w3.is_connected():
            logger.error(f"Could not connect to web3 node at {args.node_url}")
            return 1
        
        logger.info(f"Connected to web3 node at {args.node_url}")
        
        # Calculate output path based on whether the provided path is absolute or relative
        output_path = args.output
        if not os.path.isabs(output_path):
            # If the path is relative, make it relative to the script location
            script_dir = os.path.dirname(os.path.abspath(__file__))
            output_path = os.path.join(script_dir, output_path)
        
        # Calculate price file path
        price_file_path = args.price_file
        if not os.path.isabs(price_file_path):
            # If the path is relative, make it relative to the script location
            script_dir = os.path.dirname(os.path.abspath(__file__))
            price_file_path = os.path.join(script_dir, price_file_path)
        
        # Fetch block timestamps using parallel processing
        logger.info(f"Fetching block timestamps from web3 node using {args.workers} worker threads...")
        block_timestamps = fetch_block_timestamps_parallel(w3, args.sample_interval, args.workers)
        
        if not block_timestamps:
            logger.error("No block timestamps fetched. Exiting.")
            return 1
        
        # Load price data
        logger.info(f"Loading BTC price data from {price_file_path}...")
        try:
            price_data = load_price_data(price_file_path)
        except FileNotFoundError:
            logger.error(f"Price file {price_file_path} not found.")
            # Try to find bitcoin_prices.csv in the primary data directory
            web3_oracle_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            alt_price_path = os.path.join(web3_oracle_dir, 'data', 'bitcoin_prices.csv')
            logger.info(f"Trying alternative price file path: {alt_price_path}")
            price_data = load_price_data(alt_price_path)
        
        # Create block price mapping
        logger.info("Creating block-to-BTC-price mapping...")
        block_prices = create_block_price_mapping(block_timestamps, price_data)
        
        # Write to CSV
        logger.info(f"Writing {len(block_prices)} entries to {output_path}...")
        write_csv(block_prices, output_path)
        
        logger.info(f"Block-to-BTC-price mapping successfully written to {output_path}")
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 