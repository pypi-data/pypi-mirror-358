#!/usr/bin/env python3
"""
Test script to verify that swagger client imports are working correctly.
This script will:
1. Try to import various modules from the swagger client
2. Create instances of some model classes
3. Print success/failure for each test
"""

import sys
from pathlib import Path
import importlib
import re

# Add the src directory to the Python path
src_path = Path(__file__).parent.parent / 'src'
sys.path.append(str(src_path))

def read_apis_from_justfile():
    """Read the APIs list from the Justfile"""
    justfile_path = Path("Justfile")
    if not justfile_path.exists():
        raise FileNotFoundError("Justfile not found")
    
    with open(justfile_path, 'r') as f:
        content = f.read()
    
    # Extract the apis_list value using regex
    match = re.search(r'apis_list\s*:=\s*"([^"]+)"', content)
    if not match:
        raise ValueError("Could not find apis_list in Justfile")
    
    return match.group(1).split()

def test_import(module_path, expected_class=None):
    """Test importing a module and optionally a specific class"""
    try:
        module = importlib.import_module(module_path)
        if expected_class:
            if hasattr(module, expected_class):
                print(f"✅ Successfully imported {module_path}.{expected_class}")
            else:
                print(f"❌ Failed to import {module_path}.{expected_class} : Class not found")
                return False
        else:
            print(f"✅ Successfully imported {module_path}")
        return True
    except ImportError as e:
        print(f"❌ Failed to import {module_path} : {e}")
        return False
    except Exception as e:
        print(f"❌ Error importing {module_path} : {e}")
        return False

def get_sample_model_for_api(api_name):
    """Get a sample model name for testing each API"""
    # This is a mapping of API names to likely model names
    # We'll try to find a model that exists in each API
    model_mapping = {
        "work": "WorkResponse",
        "reporting": "PermitReportingResponse", 
        "lookup": "StreetResponse",
        "geojson": "WorkFeature",
        "party": "OrganisationResponse",
        "data-export": "WorkResponse",  # Assuming similar to work API
        "event": "WorkUpdateResponse",
        "sampling": "SampleInspectionTargetResponse"  # Assuming this exists
    }
    return model_mapping.get(api_name, "DefaultApi")

def main():
    print("Testing Street Manager API imports...")
    print("=" * 50)
    
    # Read APIs from Justfile
    apis = read_apis_from_justfile()
    print(f"Testing {len(apis)} APIs: {', '.join(apis)}")
    print()
    
    success_count = 0
    total_tests = 0
    
    for api in apis:
        print(f"Testing {api} API:")
        
        # Test basic module import
        module_path = f"streetmanager.{api}.swagger_client"
        if test_import(module_path):
            success_count += 1
        total_tests += 1
        
        # Test API client import
        api_client_path = f"streetmanager.{api}.swagger_client.api_client"
        if test_import(api_client_path, "ApiClient"):
            success_count += 1
        total_tests += 1
        
        # Test DefaultApi import
        default_api_path = f"streetmanager.{api}.swagger_client.api.default_api"
        if test_import(default_api_path, "DefaultApi"):
            success_count += 1
        total_tests += 1
        
        # Test a sample model (this might fail for some APIs)
        sample_model = get_sample_model_for_api(api)
        model_path = f"streetmanager.{api}.swagger_client.models"
        # We'll try to import the models module first, then a specific model
        if test_import(model_path):
            success_count += 1
            total_tests += 1
            
            # Try to import a specific model (this might not exist for all APIs)
            try:
                # Convert model name to snake_case for file name
                model_file = ''.join(['_'+c.lower() if c.isupper() else c for c in sample_model]).lstrip('_')
                specific_model_path = f"streetmanager.{api}.swagger_client.models.{model_file}"
                if test_import(specific_model_path, sample_model):
                    success_count += 1
                total_tests += 1
            except:
                print(f"⚠️  Could not test specific model for {api} API")
        
        print()
    
    print("=" * 50)
    print(f"Test Results: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 All imports working correctly!")
    else:
        print("⚠️  Some imports failed - check the output above for details")

if __name__ == "__main__":
    main() 