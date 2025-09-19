#!/usr/bin/env python3
"""
Test script for the Financial Dashboard backend
"""
import os
import sys
import requests
import time
import subprocess
from pathlib import Path

def test_backend():
    """Test the backend API"""
    print("🧪 Testing Financial Dashboard Backend")
    print("=" * 40)
    
    # Check if backend is running
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running")
        else:
            print("❌ Backend returned status code:", response.status_code)
            return False
    except requests.exceptions.RequestException as e:
        print("❌ Backend is not running or not accessible")
        print("Error:", str(e))
        return False
    
    # Test file upload
    sample_file = Path("data/sample_transactions.csv")
    if not sample_file.exists():
        print("❌ Sample data file not found")
        return False
    
    print("📁 Testing file upload...")
    try:
        with open(sample_file, 'rb') as f:
            files = {'file': ('sample_transactions.csv', f, 'text/csv')}
            response = requests.post("http://localhost:8000/upload", files=files, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ File upload successful")
            print(f"📊 Processed {data.get('summary', {}).get('total_transactions', 0)} transactions")
            
            # Check if we have the expected structure
            if 'tiles' in data and 'time_series' in data and 'insights' in data:
                print("✅ Response structure is correct")
                return True
            else:
                print("❌ Response structure is incorrect")
                return False
        else:
            print("❌ File upload failed with status code:", response.status_code)
            print("Response:", response.text)
            return False
            
    except requests.exceptions.RequestException as e:
        print("❌ File upload failed with error:", str(e))
        return False

def start_backend():
    """Start the backend server"""
    print("🚀 Starting backend server...")
    
    # Change to backend directory
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False
    
    # Set environment variable if not set
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY not set. Please set it before running the test.")
        return False
    
    # Start the server
    try:
        process = subprocess.Popen(
            [sys.executable, "main.py"],
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to start
        print("⏳ Waiting for server to start...")
        time.sleep(10)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ Backend server started")
            return process
        else:
            stdout, stderr = process.communicate()
            print("❌ Backend server failed to start")
            print("STDOUT:", stdout.decode())
            print("STDERR:", stderr.decode())
            return None
            
    except Exception as e:
        print("❌ Failed to start backend server:", str(e))
        return None

def main():
    """Main test function"""
    print("Financial Dashboard Backend Test")
    print("=" * 40)
    
    # Check if backend is already running
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code == 200:
            print("✅ Backend is already running")
            backend_process = None
        else:
            raise requests.exceptions.RequestException("Not running")
    except requests.exceptions.RequestException:
        # Start backend
        backend_process = start_backend()
        if not backend_process:
            print("❌ Failed to start backend")
            return False
    
    try:
        # Test the backend
        success = test_backend()
        
        if success:
            print("\n🎉 All tests passed!")
            print("✅ Backend is working correctly")
            print("🌐 API is available at http://localhost:8000")
            print("📚 API documentation at http://localhost:8000/docs")
        else:
            print("\n❌ Tests failed!")
            return False
            
    finally:
        # Clean up
        if backend_process:
            print("\n🛑 Stopping backend server...")
            backend_process.terminate()
            backend_process.wait()
            print("✅ Backend server stopped")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
