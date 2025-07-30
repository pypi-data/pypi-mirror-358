#!/usr/bin/env python3
"""
Automatic fix for dual-format responses (JSON and plain text).

This script automatically patches the generated code to handle both
application/json and text/plain responses based on Content-Type header,
while maintaining a consistent interface.

This should be run after OpenAPI code generation.
"""

import os
import sys
import re

def apply_api_client_dual_format_fix():
    """Apply the dual-format response fix to ApiClient."""
    
    target_file = "speechall/api_client.py"
    
    if not os.path.exists(target_file):
        print(f"❌ File not found: {target_file}")
        return False
    
    print(f"🔧 Applying dual-format response fix to {target_file}")
    
    # Read the current file
    with open(target_file, 'r') as f:
        content = f.read()
    
    # Check if the fix is already applied
    if "# Check for dual-format responses (JSON or plain text)" in content:
        print("✅ Dual-format response fix already applied to ApiClient - skipping")
        return True
    
    # Pattern to match the original response handling code in __call_api method
    old_pattern = r'''          # deserialize response data
          if response_type == "bytearray":
              return_data = response_data\.data
          elif response_type:
              return_data = self\.deserialize\(response_data, response_type\)
          else:
              return_data = None'''

    new_pattern = '''          # deserialize response data
          if response_type == "bytearray":
              return_data = response_data.data
          elif response_type:
              # Check for dual-format responses (JSON or plain text)
              content_type = response_data.getheader('content-type')
              if content_type and 'text/plain' in content_type.lower():
                  # For text/plain responses, create a consistent wrapper
                  return_data = self._create_text_response_wrapper(response_data.data, response_type)
              else:
                  # For JSON responses, deserialize normally
                  return_data = self.deserialize(response_data, response_type)
          else:
              return_data = None'''

    # Apply the replacement
    try:
        content = re.sub(old_pattern, new_pattern, content, flags=re.DOTALL)
        
        # Check if replacement was successful
        if "# Check for dual-format responses (JSON or plain text)" not in content:
            print("❌ Failed to apply replacement - method pattern may have changed")
            return False
        
        # Add the helper method for creating text response wrappers
        helper_method = '''
    def _create_text_response_wrapper(self, text_data, response_type):
        """
        Create a wrapper object for text responses that provides the same interface
        as JSON responses for consistent UX.
        
        :param text_data: The plain text response data
        :param response_type: The expected response type (e.g., "TranscriptionResponse")
        :return: A wrapper object with consistent interface
        """
        # Import the response class dynamically
        if response_type == "TranscriptionResponse":
            from speechall.models.transcription_response import TranscriptionResponse
            from speechall.models.transcription_only_text import TranscriptionOnlyText
            
            # Create a minimal TranscriptionOnlyText instance
            text_instance = TranscriptionOnlyText(
                id="text-response",
                text=text_data
            )
            
            # Wrap it in a TranscriptionResponse
            wrapper = TranscriptionResponse(actual_instance=text_instance)
            return wrapper
        else:
            # For other response types, return the text data as-is
            return text_data'''
        
        # Insert the helper method before the deserialize method
        deserialize_pattern = r'(\s+def deserialize\(self, response, response_type\):)'
        content = re.sub(deserialize_pattern, helper_method + r'\1', content)
        
        # Write the fixed content back
        with open(target_file, 'w') as f:
            f.write(content)
        
        print("✅ Dual-format response fix applied successfully to ApiClient!")
        return True
        
    except Exception as e:
        print(f"❌ Error applying fix to ApiClient: {e}")
        return False

def apply_transcription_response_enhancement():
    """Add convenience properties to TranscriptionResponse for better UX."""
    
    target_file = "speechall/models/transcription_response.py"
    
    if not os.path.exists(target_file):
        print(f"❌ File not found: {target_file}")
        return False
    
    print(f"🔧 Adding convenience properties to {target_file}")
    
    # Read the current file
    with open(target_file, 'r') as f:
        content = f.read()
    
    # Check if the enhancement is already applied
    if "@property" in content and "def text(self)" in content:
        print("✅ TranscriptionResponse enhancement already applied - skipping")
        return True
    
    # Add convenience properties at the end of the class, before the one_of_schemas field
    enhancement_code = '''
    # Convenience properties for consistent UX across response formats
    @property
    def text(self) -> str:
        """Get the transcribed text regardless of response format."""
        if hasattr(self.actual_instance, 'text'):
            return self.actual_instance.text
        return str(self.actual_instance)
    
    @property
    def is_detailed(self) -> bool:
        """Check if this is a detailed response with structured data."""
        from speechall.models.transcription_detailed import TranscriptionDetailed
        return isinstance(self.actual_instance, TranscriptionDetailed)
    
    @property
    def segments(self):
        """Get segments if available (detailed responses only)."""
        if self.is_detailed and hasattr(self.actual_instance, 'segments'):
            return self.actual_instance.segments
        return None
    
    @property
    def words(self):
        """Get words if available (detailed responses only)."""
        if self.is_detailed and hasattr(self.actual_instance, 'words'):
            return self.actual_instance.words
        return None
    
    @property
    def language(self):
        """Get language if available (detailed responses only)."""
        if self.is_detailed and hasattr(self.actual_instance, 'language'):
            return self.actual_instance.language
        return None
    
    @property
    def duration(self):
        """Get duration if available (detailed responses only)."""
        if self.is_detailed and hasattr(self.actual_instance, 'duration'):
            return self.actual_instance.duration
        return None

'''
    
    # Find a good place to insert the properties - before the Config class
    class_config_pattern = r'(\s+class Config:)'
    
    try:
        content = re.sub(class_config_pattern, enhancement_code + r'\1', content)
        
        # Check if enhancement was applied
        if "@property" not in content or "def text(self):" not in content:
            print("❌ Failed to apply TranscriptionResponse enhancement")
            return False
        
        # Write the enhanced content back
        with open(target_file, 'w') as f:
            f.write(content)
        
        print("✅ TranscriptionResponse enhancement applied successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error applying TranscriptionResponse enhancement: {e}")
        return False

def main():
    """Main function."""
    print("🔧 Starting dual-format response automatic fixes...")
    
    success = True
    
    # Apply the API client fix
    if not apply_api_client_dual_format_fix():
        success = False
    
    # Apply TranscriptionResponse enhancements
    if not apply_transcription_response_enhancement():
        success = False
    
    if success:
        print("✅ All dual-format response fixes applied successfully!")
        print("\n📖 Usage after fixes:")
        print("# Always works - consistent interface")
        print("result = api.transcribe(model=model, body=audio, output_format=format)")
        print("text = result.text  # Always available")
        print("if result.is_detailed:")
        print("    segments = result.segments")
        print("    language = result.language")
        sys.exit(0)
    else:
        print("❌ Some dual-format response fixes failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
