#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import sys
import os
from pathlib import Path

def find_test_files(source_dir, pattern):
    """Find all test files matching the given pattern in source_dir and subdirectories
    
    Args:
        source_dir: Directory to search
        pattern: Glob pattern to match files
        
    Returns:
        List of paths to matching files
    """
    source_path = Path(source_dir)
    if not source_path.exists() or not source_path.is_dir():
        print(f"Error: Source directory '{source_dir}' does not exist or is not a directory")
        sys.exit(1)
        
    # Find all matching files in source_dir and subdirectories
    matches = []
    for path in source_path.glob(f"**/{pattern}"):
        if path.is_file():
            matches.append(path)
            
    return matches

def run_test_files(test_files, verbose=False):
    """Run all test files directly like shell execution
    
    Args:
        test_files: List of paths to test files
        verbose: Whether to show verbose output
        
    Returns:
        True if all tests passed, False otherwise
    """
    if not test_files:
        print("No test files found matching the pattern")
        return False
        
    print(f"Found {len(test_files)} test file(s):")
    for i, file_path in enumerate(test_files):
        print(f"  {i+1}. {file_path}")
    print()
    
    all_passed = True
    for file_path in test_files:
        print(f"Running {file_path}")
        try:
            # Execute like a shell command - this will properly pass through Ctrl+C
            cmd = f"{sys.executable} {file_path}"
            exit_code = os.system(cmd)
            
            # Extract the actual exit code (os.system returns a platform-dependent value)
            if os.name == 'nt':  # Windows
                exit_code = exit_code
            else:  # Unix-like
                exit_code = exit_code >> 8
                
            if exit_code != 0:
                all_passed = False
                print(f"Error: {file_path} failed with exit code {exit_code}")
                    
        except KeyboardInterrupt:
            print("\nTest execution interrupted by user")
            return False
        except Exception as e:
            print(f"Error running {file_path}: {e}")
            all_passed = False
            
        print()
    
    return all_passed

def main():
    """Main entry point for the unittest2doc command line tool"""
    parser = argparse.ArgumentParser(description="Run unittest2doc tests and generate documentation")
    parser.add_argument("-s", "--source", default="tests", help="Source directory containing test files (default: tests)")
    parser.add_argument("-p", "--pattern", default="test_*.py", help="File pattern to match test files")
    parser.add_argument("-v", "--verbose", action="store_true", help="Increase output verbosity")
    
    args = parser.parse_args()
    
    # Check if source directory exists
    source_path = Path(args.source)
    if not source_path.exists():
        print(f"Error: Source directory '{args.source}' does not exist")
        sys.exit(1)
    
    test_files = find_test_files(args.source, args.pattern)
    success = run_test_files(test_files, args.verbose)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
