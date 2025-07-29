#!/usr/bin/env python3
"""
Quick Start - PyCDN Natural Import System

This example shows the basic usage of PyCDN's revolutionary import system
that allows you to import packages directly from CDN servers using natural Python syntax.
"""

import pycdn

def main():
    print("PyCDN Quick Start - Natural Import System")
    print("=" * 50)
    
    # Step 1: Connect to CDN server
    print("1. Connecting to CDN server...")
    cdn = pycdn.pkg("http://localhost:8000")
    print(f"✓ Connected to {cdn._cdn_client.url}")
    print(f"✓ Import prefix registered: '{cdn._prefix}'")
    
    # Step 2: Classic usage (still works)
    print("\n2. Classic usage:")
    try:
        result = cdn.math.sqrt(16)
        print(f"cdn.math.sqrt(16) = {result}")
    except Exception as e:
        print(f"Classic usage error: {e}")
    
    # Step 3: Natural import syntax (NEW!)
    print("\n3. Natural import syntax:")
    try:
        # Import functions directly
        from cdn.math import sqrt, pow
        print("✓ Successfully imported: from cdn.math import sqrt, pow")
        
        # Use them naturally
        result1 = sqrt(25)
        result2 = pow(2, 8)
        print(f"sqrt(25) = {result1}")
        print(f"pow(2, 8) = {result2}")
        
    except Exception as e:
        print(f"Import error: {e}")
        print("Note: This requires a running PyCDN server with math package")
    
    # Step 4: Import classes
    print("\n4. Class imports:")
    try:
        from cdn.openai import OpenAI
        print("✓ Successfully imported: from cdn.openai import OpenAI")
        
        # Create instance (would work with real OpenAI package)
        # client = OpenAI(api_key="test-key")
        # print(f"Created client: {client}")
        
    except Exception as e:
        print(f"Class import error: {e}")
        print("Note: This is expected without OpenAI package on CDN")
    
    # Step 5: Custom prefixes
    print("\n5. Custom prefixes:")
    try:
        # Create connection with custom prefix
        ml_cdn = pycdn.pkg("http://localhost:8000", prefix="ml")
        print(f"✓ Created ML CDN with prefix: '{ml_cdn._prefix}'")
        
        # Now you could use: from ml.tensorflow import keras
        # Or: from ml.pytorch import nn
        print("  Usage: from ml.tensorflow import keras")
        print("  Usage: from ml.pytorch import nn")
        
    except Exception as e:
        print(f"Custom prefix error: {e}")
    
    print("\n" + "=" * 50)
    print("🚀 PyCDN: The Netflix of Python packages!")
    print("No more 'pip install' - just import and use!")
    print("=" * 50)

if __name__ == "__main__":
    main()