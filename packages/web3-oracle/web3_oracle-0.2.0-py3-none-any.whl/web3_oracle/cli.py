#!/usr/bin/env python3
"""
Command Line Interface for web3_oracle

Usage:
    python -m web3_oracle.cli [--verbose] get_price <token_address> <timestamp>
    python -m web3_oracle.cli [--verbose] get_price_by_date <token_address> <date> <time>
    python -m web3_oracle.cli [--verbose] get_reference_price <token_address>
    python -m web3_oracle.cli [--verbose] get_price_by_block <token_address> <block_number>
    python -m web3_oracle.cli [--verbose] fast_price <block_number>
    python -m web3_oracle.cli [--verbose] get_token_price <token_address> [--block <block_number>] [--timestamp <timestamp>]
    python -m web3_oracle.cli [--verbose] list_tokens

Args:
    --verbose, -v: Enable verbose logging (shows initialization info)
    get_price: Get token price by contract address and Unix timestamp
    get_price_by_date: Get token price by contract address and date/time
    get_reference_price: Get reference price for a token from altcoins data
    get_price_by_block: Get token price by contract address and Ethereum block number
    fast_price: Get Ethereum price at a specific block number (fast lookup)
    get_token_price: Unified function to get token price (auto-selects optimal method)
    list_tokens: List all available tokens

Example:
    python -m web3_oracle.cli get_price 0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2 1620518400
    python -m web3_oracle.cli --verbose get_price_by_date 0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2 2021-05-08 12:00:00
    python -m web3_oracle.cli get_reference_price 0x1f9840a85d5af5bf1d1762f925bdaddc4201f984
    python -m web3_oracle.cli get_price_by_block 0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2 15000000
    python -m web3_oracle.cli fast_price 19302940
    python -m web3_oracle.cli get_token_price 0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2 --block 15000000
    python -m web3_oracle.cli get_token_price 0x1f9840a85d5af5bf1d1762f925bdaddc4201f984
    python -m web3_oracle.cli --verbose list_tokens
"""

import sys
import argparse
from datetime import datetime
from .oracle import Oracle

def main():
    """Main entry point for CLI"""
    parser = argparse.ArgumentParser(description='Web3 Oracle - Token Price CLI')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # get_price command
    price_parser = subparsers.add_parser('get_price', help='Get token price by contract address and timestamp')
    price_parser.add_argument('token_address', help='Token contract address')
    price_parser.add_argument('timestamp', type=int, help='Unix timestamp')
    
    # get_price_by_date command
    date_parser = subparsers.add_parser('get_price_by_date', help='Get token price by contract address and date/time')
    date_parser.add_argument('token_address', help='Token contract address')
    date_parser.add_argument('date', help='Date in YYYY-MM-DD format')
    date_parser.add_argument('time', help='Time in HH:MM:SS format')
    
    # get_reference_price command
    ref_parser = subparsers.add_parser('get_reference_price', help='Get reference price for a token')
    ref_parser.add_argument('token_address', help='Token contract address')
    
    # get_price_by_block command
    block_parser = subparsers.add_parser('get_price_by_block', help='Get token price by contract address and block number (WETH/WBTC only)')
    block_parser.add_argument('token_address', help='Token contract address (WETH or WBTC)')
    block_parser.add_argument('block_number', type=int, help='Ethereum block number')
    
    # fast_price command
    fast_parser = subparsers.add_parser('fast_price', help='Get Ethereum price at a specific block (fast lookup)')
    fast_parser.add_argument('block_number', type=int, help='Ethereum block number')
    
    # fast_btc_price command
    fast_btc_parser = subparsers.add_parser('fast_btc_price', help='Get Bitcoin price at a specific block (fast lookup)')
    fast_btc_parser.add_argument('block_number', type=int, help='Ethereum block number')
    
    # get_token_price command (unified)
    unified_parser = subparsers.add_parser('get_token_price', 
                                        help='Unified function to get token price (auto-selects optimal method)')
    unified_parser.add_argument('token_address', help='Token contract address')
    unified_parser.add_argument('--block', type=int, help='Ethereum block number (optional)', default=None)
    unified_parser.add_argument('--timestamp', type=int, help='Unix timestamp (optional)', default=None)
    
    # list_tokens command
    subparsers.add_parser('list_tokens', help='List all available tokens')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Initialize oracle
    oracle = Oracle(verbose=args.verbose)
    
    if args.command == 'get_price':
        price = oracle.get_price(args.token_address, args.timestamp)
        if price is not None:
            token_info = oracle.get_token_info(args.token_address) or {'symbol': 'Unknown'}
            print(f"Price of {token_info.get('symbol', 'Unknown')} at timestamp {args.timestamp}: ${price:.6f}")
        else:
            print(f"Price not found for token {args.token_address} at timestamp {args.timestamp}")
            return 1
    
    elif args.command == 'get_price_by_date':
        try:
            dt = datetime.strptime(f"{args.date} {args.time}", '%Y-%m-%d %H:%M:%S')
            price = oracle.get_price_by_datetime(args.token_address, dt)
            
            if price is not None:
                token_info = oracle.get_token_info(args.token_address) or {'symbol': 'Unknown'}
                print(f"Price of {token_info.get('symbol', 'Unknown')} at {args.date} {args.time}: ${price:.6f}")
            else:
                print(f"Price not found for token {args.token_address} at {args.date} {args.time}")
                return 1
        except ValueError:
            print("Error: Invalid date/time format. Use YYYY-MM-DD for date and HH:MM:SS for time.")
            return 1
    
    elif args.command == 'get_reference_price':
        price = oracle.get_reference_price(args.token_address)
        if price is not None:
            token_info = oracle.get_token_info(args.token_address) or {'symbol': 'Unknown'}
            print(f"Reference price for {token_info.get('symbol', 'Unknown')}: ${price:.6f}")
        else:
            print(f"Reference price not found for token {args.token_address}")
            return 1
    
    elif args.command == 'get_price_by_block':
        price = oracle.get_price_by_block(args.token_address, args.block_number)
        if price is not None:
            token_info = oracle.get_token_info(args.token_address) or {'symbol': 'Unknown'}
            print(f"Price of {token_info.get('symbol', 'Unknown')} at block {args.block_number}: ${price:.6f}")
        else:
            print(f"Price not found for token {args.token_address} at block {args.block_number}")
            return 1
    
    elif args.command == 'fast_price':
        price = oracle.fast_price(args.block_number)
        if price is not None:
            print(f"Fast ETH price lookup at block {args.block_number}: ${price:.6f}")
        else:
            print(f"Fast ETH price lookup failed for block {args.block_number}")
            return 1
    
    elif args.command == 'fast_btc_price':
        price = oracle.fast_btc_price(args.block_number)
        if price is not None:
            print(f"Fast BTC price lookup at block {args.block_number}: ${price:.6f}")
        else:
            print(f"Fast BTC price lookup failed for block {args.block_number}")
            return 1
    
    elif args.command == 'get_token_price':
        # Describe the lookup method based on what parameters were provided
        if args.block is not None:
            method_desc = f"block {args.block}"
        elif args.timestamp is not None:
            method_desc = f"timestamp {args.timestamp}"
        else:
            method_desc = "reference price"
            
        price = oracle.get_token_price(args.token_address, block_number=args.block, timestamp=args.timestamp)
        if price is not None:
            token_info = oracle.get_token_info(args.token_address) or {'symbol': 'Unknown'}
            print(f"Price of {token_info.get('symbol', 'Unknown')} using {method_desc}: ${price:.6f}")
        else:
            print(f"Price not found for token {args.token_address} using {method_desc}")
            return 1
    
    elif args.command == 'list_tokens':
        tokens = oracle.get_available_tokens()
        print(f"Available tokens ({len(tokens)}):")
        for address, info in tokens.items():
            print(f"- {info['symbol']} ({info['name']}): {address}")
    
    return 0

if __name__ == '__main__':
    sys.exit(main()) 