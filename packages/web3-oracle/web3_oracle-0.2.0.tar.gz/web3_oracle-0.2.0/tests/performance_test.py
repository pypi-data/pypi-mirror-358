#!/usr/bin/env python3
"""
Performance Test for web3_oracle package

This script tests the performance of get_token_price function in different scenarios:
1. WETH price lookup by block number (direct mapping)
2. WBTC price lookup by block number (direct mapping)
3. Altcoin reference price lookup
4. Regular token price lookup by block number
5. Token price lookup by timestamp

Usage:
    python performance_test.py
"""

import time
from web3_oracle import Oracle
import statistics
from typing import List, Dict, Any, Callable
import pandas as pd
from datetime import datetime

def measure_execution_time(func: Callable, *args, **kwargs) -> float:
    """Measure execution time of a function call"""
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    return end_time - start_time, result

def run_benchmark(oracle: Oracle, test_cases: List[Dict[str, Any]], iterations: int = 100) -> pd.DataFrame:
    """Run benchmark on multiple test cases with multiple iterations"""
    results = []
    
    for test_case in test_cases:
        name = test_case["name"]
        token_address = test_case["token_address"]
        block_number = test_case.get("block_number")
        timestamp = test_case.get("timestamp")
        
        print(f"\nRunning test: {name}")
        
        execution_times = []
        for i in range(iterations):
            if i % 10 == 0 and i > 0:
                print(f"  Completed {i}/{iterations} iterations...")
                
            exec_time, price = measure_execution_time(
                oracle.get_token_price,
                token_address=token_address,
                block_number=block_number,
                timestamp=timestamp
            )
            
            execution_times.append(exec_time)
        
        # Calculate statistics
        avg_time = statistics.mean(execution_times)
        min_time = min(execution_times)
        max_time = max(execution_times)
        median_time = statistics.median(execution_times)
        p95_time = sorted(execution_times)[int(iterations * 0.95)]
        
        print(f"  Results for {name}:")
        print(f"    Average time: {avg_time:.6f}s")
        print(f"    Min time: {min_time:.6f}s")
        print(f"    Max time: {max_time:.6f}s")
        print(f"    Median time: {median_time:.6f}s")
        print(f"    P95 time: {p95_time:.6f}s")
        
        results.append({
            "Test Case": name,
            "Average (s)": avg_time,
            "Min (s)": min_time,
            "Max (s)": max_time,
            "Median (s)": median_time,
            "P95 (s)": p95_time
        })
    
    return pd.DataFrame(results)

def compare_direct_methods(oracle: Oracle, blocks: List[int]) -> pd.DataFrame:
    """Compare direct methods for ETH and BTC price lookups"""
    results = []
    
    print("\n=== Comparing Direct Price Lookup Methods ===")
    
    # Test fast_price method (ETH)
    for block in blocks:
        print(f"\nTesting fast_price (ETH) at block {block}")
        exec_time, price = measure_execution_time(oracle.fast_price, block)
        print(f"  ETH price at block {block}: ${price:.2f}, lookup time: {exec_time:.6f}s")
        
        results.append({
            "Method": "fast_price (ETH)",
            "Block": block,
            "Price": price,
            "Time (s)": exec_time
        })
    
    # Test fast_btc_price method (BTC)
    for block in blocks:
        print(f"\nTesting fast_btc_price (BTC) at block {block}")
        exec_time, price = measure_execution_time(oracle.fast_btc_price, block)
        print(f"  BTC price at block {block}: ${price:.2f}, lookup time: {exec_time:.6f}s")
        
        results.append({
            "Method": "fast_btc_price (BTC)",
            "Block": block,
            "Price": price,
            "Time (s)": exec_time
        })
    
    return pd.DataFrame(results)

def test_specific_blocks(oracle: Oracle, special_blocks: Dict[str, int]) -> None:
    """Test specific blocks mentioned in requirements"""
    print("\n=== Testing Specific Block Numbers ===")
    
    for name, block in special_blocks.items():
        # Test ETH price
        eth_exec_time, eth_price = measure_execution_time(oracle.fast_price, block)
        print(f"ETH price at {name} (block {block}): ${eth_price:.2f}, lookup time: {eth_exec_time:.6f}s")
        
        # Test BTC price
        btc_exec_time, btc_price = measure_execution_time(oracle.fast_btc_price, block)
        print(f"BTC price at {name} (block {block}): ${btc_price:.2f}, lookup time: {btc_exec_time:.6f}s")

def main():
    """Run performance tests"""
    print("Initializing Oracle...")
    oracle = Oracle()
    
    # Example token addresses
    weth_address = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"  # WETH
    wbtc_address = "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599"  # WBTC
    usdc_address = "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"  # USDC
    uni_address = "0x1f9840a85d5af5bf1d1762f925bdaddc4201f984"   # UNI (altcoin)
    link_address = "0x514910771af9ca656af840dff83e8264ecf986ca"  # LINK (altcoin)
    
    # Standard test blocks
    standard_blocks = [10000000, 12000000, 14000000, 16000000]
    
    # Special blocks mentioned in requirements
    special_blocks = {
        "Special Block 1": 18039284,
        "Special Block 2": 19302940
    }
    
    # Timestamps for testing
    timestamps = [1620518400, 1642248000, 1632268800]  # Various timestamps in 2021-2022
    
    # Define test cases for get_token_price
    test_cases = [
        {
            "name": "WETH by block (direct mapping)",
            "token_address": weth_address,
            "block_number": 14000000
        },
        {
            "name": "WBTC by block (direct mapping)",
            "token_address": wbtc_address,
            "block_number": 14000000
        },
        {
            "name": "Altcoin reference price (UNI)",
            "token_address": uni_address
        },
        {
            "name": "Altcoin reference price (LINK)",
            "token_address": link_address
        },
        {
            "name": "Regular token by block (USDC)",
            "token_address": usdc_address,
            "block_number": 14000000
        },
        {
            "name": "WETH by timestamp",
            "token_address": weth_address,
            "timestamp": 1620518400
        },
        {
            "name": "WBTC by timestamp",
            "token_address": wbtc_address,
            "timestamp": 1620518400
        }
    ]
    
    # Test specific blocks from requirements
    test_specific_blocks(oracle, special_blocks)
    
    # Compare direct methods
    df_direct = compare_direct_methods(oracle, standard_blocks + list(special_blocks.values()))
    
    # Set number of iterations for the main benchmark
    iterations = 50
    
    print(f"\n=== Performance Testing get_token_price ({iterations} iterations per test) ===\n")
    
    # Run benchmark
    df_results = run_benchmark(oracle, test_cases, iterations)
    
    # Print summary table
    print("\nPerformance Summary Table:")
    print(df_results.to_string(index=False))
    
    # Calculate speedup compared to slowest method
    slowest_avg = df_results["Average (s)"].max()
    df_results["Speedup"] = slowest_avg / df_results["Average (s)"]
    
    print("\nRelative Performance (Speedup compared to slowest method):")
    print(df_results[["Test Case", "Speedup"]].to_string(index=False))
    
    # Print direct method comparison
    print("\nDirect Method Comparison:")
    
    # Group by method and calculate average
    method_summary = df_direct.groupby("Method").agg({
        "Time (s)": ["mean", "min", "max"]
    }).reset_index()
    method_summary.columns = ["Method", "Average (s)", "Min (s)", "Max (s)"]
    print(method_summary.to_string(index=False))
    
    # Compare specific blocks
    print("\nComparison for Specific Blocks:")
    for block in special_blocks.values():
        eth_data = df_direct[(df_direct["Method"] == "fast_price (ETH)") & (df_direct["Block"] == block)]
        btc_data = df_direct[(df_direct["Method"] == "fast_btc_price (BTC)") & (df_direct["Block"] == block)]
        
        if not eth_data.empty and not btc_data.empty:
            eth_time = eth_data.iloc[0]["Time (s)"]
            btc_time = btc_data.iloc[0]["Time (s)"]
            print(f"Block {block}: ETH {eth_time:.6f}s, BTC {btc_time:.6f}s, Ratio: {eth_time/btc_time:.2f}x")

if __name__ == "__main__":
    main() 