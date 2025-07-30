#!/usr/bin/env python3
"""
Automatic fix for TranscriptionResponse oneOf issue.

This script automatically patches the generated TranscriptionResponse class
to handle the case where TranscriptionDetailed is a superset of TranscriptionOnlyText.

This should be run after OpenAPI code generation.
"""

import os
import sys
import re

def apply_transcription_response_fix():
    """Apply the fix to TranscriptionResponse."""
    
    target_file = "speechall/models/transcription_response.py"
    
    if not os.path.exists(target_file):
        print(f"❌ File not found: {target_file}")
        return False
    
    print(f"🔧 Applying TranscriptionResponse oneOf fix to {target_file}")
    
    # Read the current file
    with open(target_file, 'r') as f:
        content = f.read()
    
    # Check if the fix is already applied
    if "# Parse JSON once to avoid multiple parsing" in content:
        print("✅ Fix already applied - skipping")
        return True
    
    # Replace the from_json method
    old_from_json = r'''    @classmethod
    def from_json\(cls, json_str: str\) -> TranscriptionResponse:
        """Returns the object represented by the json string"""
        instance = TranscriptionResponse\.construct\(\)
        error_messages = \[\]
        match = 0

        # deserialize data into TranscriptionDetailed
        try:
            instance\.actual_instance = TranscriptionDetailed\.from_json\(json_str\)
            match \+= 1
        except \(ValidationError, ValueError\) as e:
            error_messages\.append\(str\(e\)\)
        # deserialize data into TranscriptionOnlyText
        try:
            instance\.actual_instance = TranscriptionOnlyText\.from_json\(json_str\)
            match \+= 1
        except \(ValidationError, ValueError\) as e:
            error_messages\.append\(str\(e\)\)

        if match > 1:
            # more than 1 match
            raise ValueError\("Multiple matches found when deserializing the JSON string into TranscriptionResponse with oneOf schemas: TranscriptionDetailed, TranscriptionOnlyText\. Details: " \+ ", "\.join\(error_messages\)\)
        elif match == 0:
            # no match
            raise ValueError\("No match found when deserializing the JSON string into TranscriptionResponse with oneOf schemas: TranscriptionDetailed, TranscriptionOnlyText\. Details: " \+ ", "\.join\(error_messages\)\)
        else:
            return instance'''

    new_from_json = '''    @classmethod
    def from_json(cls, json_str: str) -> TranscriptionResponse:
        """Returns the object represented by the json string"""
        instance = TranscriptionResponse.construct()
        error_messages = []
        
        # Parse JSON once to avoid multiple parsing
        try:
            json_obj = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {str(e)}")
        
        # Try TranscriptionDetailed first - if it has extra fields beyond id/text, prefer it
        # Check if the JSON contains fields that are specific to TranscriptionDetailed
        has_detailed_fields = any(key in json_obj for key in ['language', 'duration', 'segments', 'words', 'provider_metadata'])
        
        if has_detailed_fields:
            # Definitely should be TranscriptionDetailed
            try:
                instance.actual_instance = TranscriptionDetailed.from_json(json_str)
                return instance
            except (ValidationError, ValueError) as e:
                error_messages.append(f"TranscriptionDetailed validation failed: {str(e)}")
        
        # Try TranscriptionDetailed first (even without extra fields, it might still be the correct type)
        try:
            instance.actual_instance = TranscriptionDetailed.from_json(json_str)
            return instance
        except (ValidationError, ValueError) as e:
            error_messages.append(f"TranscriptionDetailed validation failed: {str(e)}")
        
        # Fall back to TranscriptionOnlyText
        try:
            instance.actual_instance = TranscriptionOnlyText.from_json(json_str)
            return instance
        except (ValidationError, ValueError) as e:
            error_messages.append(f"TranscriptionOnlyText validation failed: {str(e)}")

        # If we get here, neither worked
        raise ValueError("No match found when deserializing the JSON string into TranscriptionResponse with oneOf schemas: TranscriptionDetailed, TranscriptionOnlyText. Details: " + ", ".join(error_messages))'''

    # Replace the validator method
    old_validator = r'''    @validator\('actual_instance'\)
    def actual_instance_must_validate_oneof\(cls, v\):
        instance = TranscriptionResponse\.construct\(\)
        error_messages = \[\]
        match = 0
        # validate data type: TranscriptionDetailed
        if not isinstance\(v, TranscriptionDetailed\):
            error_messages\.append\(f"Error! Input type `\{type\(v\)\}` is not `TranscriptionDetailed`"\)
        else:
            match \+= 1
        # validate data type: TranscriptionOnlyText
        if not isinstance\(v, TranscriptionOnlyText\):
            error_messages\.append\(f"Error! Input type `\{type\(v\)\}` is not `TranscriptionOnlyText`"\)
        else:
            match \+= 1
        if match > 1:
            # more than 1 match
            raise ValueError\("Multiple matches found when setting `actual_instance` in TranscriptionResponse with oneOf schemas: TranscriptionDetailed, TranscriptionOnlyText\. Details: " \+ ", "\.join\(error_messages\)\)
        elif match == 0:
            # no match
            raise ValueError\("No match found when setting `actual_instance` in TranscriptionResponse with oneOf schemas: TranscriptionDetailed, TranscriptionOnlyText\. Details: " \+ ", "\.join\(error_messages\)\)
        else:
            return v'''

    new_validator = '''    @validator('actual_instance')
    def actual_instance_must_validate_oneof(cls, v):
        # Check if it's a valid type for either schema
        if isinstance(v, (TranscriptionDetailed, TranscriptionOnlyText)):
            return v
        
        # If not an instance of either expected type, raise error
        error_messages = [
            f"Error! Input type `{type(v)}` is not `TranscriptionDetailed`",
            f"Error! Input type `{type(v)}` is not `TranscriptionOnlyText`"
        ]
        raise ValueError("No match found when setting `actual_instance` in TranscriptionResponse with oneOf schemas: TranscriptionDetailed, TranscriptionOnlyText. Details: " + ", ".join(error_messages))'''

    # Apply the replacements
    try:
        # Replace from_json method
        content = re.sub(old_from_json, new_from_json, content, flags=re.DOTALL)
        
        # Replace validator method 
        content = re.sub(old_validator, new_validator, content, flags=re.DOTALL)
        
        # Write the fixed content back
        with open(target_file, 'w') as f:
            f.write(content)
        
        print("✅ TranscriptionResponse fix applied successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error applying fix: {e}")
        return False
    
def apply_release_date_fix():
    """Apply the fix to SpeechToTextModel release_date field."""
    
    target_file = "speechall/models/speech_to_text_model.py"
    
    if not os.path.exists(target_file):
        print(f"❌ File not found: {target_file}")
        return False
    
    print(f"🔧 Applying release_date fix to {target_file}")
    
    # Read the current file
    with open(target_file, 'r') as f:
        content = f.read()
    
    # Check if the fix is already applied
    if "from datetime import date, datetime" in content and "Added this to fix the release_date field" in content:
        print("✅ Fix already applied - skipping")
        return True

    old_content = '''from datetime import date'''
    new_content = '''from datetime import date, datetime'''
    
    # Replace the old content with the new content
    content = content.replace(old_content, new_content)

    old_content = '''    @validator('accuracy_tier')
    def accuracy_tier_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in ('basic', 'standard', 'enhanced', 'premium',):
            raise ValueError("must be one of enum values ('basic', 'standard', 'enhanced', 'premium')")
        return value'''
    
    new_content = '''    @validator('accuracy_tier')
    def accuracy_tier_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in ('basic', 'standard', 'enhanced', 'premium',):
            raise ValueError("must be one of enum values ('basic', 'standard', 'enhanced', 'premium')")
        return value

    # Added this to fix the release_date field
    @validator('release_date', pre=True)
    def parse_release_date(cls, value):
        """Parse release_date from various string formats"""
        if value is None or isinstance(value, date):
            return value
        
        if isinstance(value, str):
            # Try common date formats
            date_formats = [
                '%Y-%m-%d',          # ISO format: 2023-12-25
                '%m/%d/%Y',          # US format: 12/25/2023
                '%d/%m/%Y',          # European format: 25/12/2023
                '%Y-%m-%dT%H:%M:%S', # ISO datetime format
                '%Y-%m-%dT%H:%M:%SZ',# ISO datetime with Z
                '%Y-%m-%d %H:%M:%S', # Space separated datetime
            ]
            
            for fmt in date_formats:
                try:
                    parsed_datetime = datetime.strptime(value, fmt)
                    return parsed_datetime.date()
                except ValueError:
                    continue
            
            # If no format works, try to return None to avoid errors
            return None
        
        return value'''
    
    # Replace the old content with the new content
    content = content.replace(old_content, new_content)
    
    # Write the fixed content back
    with open(target_file, 'w') as f:
        f.write(content)
    
    print("✅ Release date fix applied successfully!")
    return True

def main():
    """Main function."""
    if apply_transcription_response_fix():
        print("🎉 Automatic fix completed successfully!")
    else:
        print("❌ Fix failed!")
        sys.exit(1)
    
    if apply_release_date_fix():
        print("🎉 Automatic fix completed successfully!")
    else:
        print("❌ Fix failed!")
        sys.exit(1)
    
    sys.exit(0)

if __name__ == "__main__":
    main() 