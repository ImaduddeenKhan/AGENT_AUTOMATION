#!/usr/bin/env python3
"""
Test script for Raptor Event Scout
Run this to test your setup without the scheduler
"""

import asyncio
import os
import sys
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


async def test_scout():
    """Test the scout system"""
    print("🧪 Testing Raptor Event Scout...")

    # Load environment
    load_dotenv()

    # Check essential variables
    required = ['GROQ_API_KEY', 'SUPABASE_URL', 'SUPABASE_KEY']
    missing = [var for var in required if not os.getenv(var)]

    if missing:
        print("❌ Missing environment variables:")
        for var in missing:
            print(f"   - {var}")
        print("\n📝 Please check your .env file")
        return False

    print("✅ Environment variables check passed")

    try:
        # Import after environment check
        from main import RaptorEventScout

        # Initialize scout
        print("🚀 Initializing Raptor Event Scout...")
        scout = RaptorEventScout()

        # Run one complete cycle
        print("🔍 Starting test run...")
        success = await scout.run_weekly_scout()

        if success:
            print("✅ Test completed successfully!")
        else:
            print("❌ Test completed with errors")

        return success

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("📦 Make sure all dependencies are installed: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🔧 Raptor Event Scout - Test Mode")
    print("=" * 50)

    result = asyncio.run(test_scout())

    print("=" * 50)
    if result:
        print("🎉 All tests passed! You can now run: python main.py --now")
        sys.exit(0)
    else:
        print("💥 Tests failed. Please check the errors above.")
        sys.exit(1)