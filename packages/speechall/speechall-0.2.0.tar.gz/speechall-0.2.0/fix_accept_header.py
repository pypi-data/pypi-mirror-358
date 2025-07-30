#!/usr/bin/env python3
"""
Automatic fix for Accept header handling.

This script automatically patches the generated ApiClient class
to use '*/*' for Accept headers instead of prioritizing JSON.

This should be run after OpenAPI code generation.
"""

import os
import sys
import re

def apply_accept_header_fix():
    """Apply the fix to ApiClient select_header_accept method."""
    
    target_file = "speechall/api_client.py"
    
    if not os.path.exists(target_file):
        print(f"❌ File not found: {target_file}")
        return False
    
    print(f"🔧 Applying Accept header fix to {target_file}")
    
    # Read the current file
    with open(target_file, 'r') as f:
        content = f.read()
    
    # Check if the fix is already applied
    if "# Accept any content type instead of prioritizing JSON" in content:
        print("✅ Accept header fix already applied - skipping")
        return True
    
    # Pattern to match the original select_header_accept method
    old_method = r'''    def select_header_accept\(self, accepts\):
        """Returns `Accept` based on an array of accepts provided\.

        :param accepts: List of headers\.
        :return: Accept \(e\.g\. application/json\)\.
        """
        if not accepts:
            return

        for accept in accepts:
            if re\.search\('json', accept, re\.IGNORECASE\):
                return accept

        return accepts\[0\]'''

    new_method = '''    def select_header_accept(self, accepts):
        """Returns `Accept` based on an array of accepts provided.

        :param accepts: List of headers.
        :return: Accept (e.g. */*).
        """
        if not accepts:
            return

        # Accept any content type instead of prioritizing JSON
        return '*/*' '''

    # Apply the replacement
    try:
        content = re.sub(old_method, new_method, content, flags=re.DOTALL)
        
        # Check if replacement was successful
        if "# Accept any content type instead of prioritizing JSON" not in content:
            print("❌ Failed to apply replacement - method pattern may have changed")
            return False
        
        # Write the fixed content back
        with open(target_file, 'w') as f:
            f.write(content)
        
        print("✅ Accept header fix applied successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error applying fix: {e}")
        return False

def main():
    """Main function."""
    print("🔧 Starting Accept header automatic fixes...")
    
    success = True
    
    # Apply the accept header fix
    if not apply_accept_header_fix():
        success = False
    
    if success:
        print("✅ All Accept header fixes applied successfully!")
        sys.exit(0)
    else:
        print("❌ Some fixes failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 