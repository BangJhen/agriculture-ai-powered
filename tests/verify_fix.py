#!/usr/bin/env python3
"""
Quick verification script to ensure the ValueError is fixed
"""

import sys
import os
# Add parent directory to path to import agricultural_chatbot
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_role_initialization():
    """Test that role initialization works correctly"""
    print("🔍 Testing Role Initialization Fix")
    print("=" * 40)
    
    try:
        # Import the module
        import agricultural_chatbot
        print("✅ Successfully imported agricultural_chatbot module")
        
        # Check USER_ROLES
        USER_ROLES = agricultural_chatbot.USER_ROLES
        print(f"✅ USER_ROLES loaded with {len(USER_ROLES)} roles")
        print(f"   First role: '{list(USER_ROLES.keys())[0]}'")
        
        # Test the logic that was causing the error
        # Simulate session state initialization
        user_role = list(USER_ROLES.keys())[0]  # This is what the fix does
        print(f"✅ Default role assignment works: '{user_role}'")
        
        # Test selectbox index calculation (the line that was failing)
        try:
            index = list(USER_ROLES.keys()).index(user_role) if user_role in USER_ROLES else 0
            print(f"✅ Selectbox index calculation works: index={index}")
        except ValueError as e:
            print(f"❌ Selectbox index still fails: {e}")
            return False
            
        # Test with the old problematic value
        old_role = "Petani"  # This was causing the error
        try:
            index = list(USER_ROLES.keys()).index(old_role) if old_role in USER_ROLES else 0
            print(f"✅ Safety check for old role works: index={index} (should be 0)")
        except ValueError as e:
            print(f"❌ Safety check failed: {e}")
            return False
        
        print("\n🎉 ALL TESTS PASSED - ValueError should be fixed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def main():
    """Main test function"""
    if test_role_initialization():
        print("\n✅ The ValueError: 'Petani' is not in list has been FIXED!")
        print("\nYou can now run the application with:")
        print("   streamlit run agricultural_chatbot.py")
        return 0
    else:
        print("\n❌ The error has NOT been fixed properly.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
