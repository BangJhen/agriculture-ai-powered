#!/usr/bin/env python3
"""
Test script for the Indonesian Agricultural Chatbot
"""

import sys
import os
# Add parent directory to path to import agricultural_chatbot
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agricultural_chatbot import (
    initialize_openai_client,
    get_ai_response,
    analyze_parameters,
    search_knowledge_base,
    USER_ROLES,
    AGRICULTURAL_PARAMETERS,
    SUSTAINABLE_AGRICULTURE_KNOWLEDGE
)

def test_basic_functionality():
    """Test basic functionality of the chatbot"""
    print("🌾 Testing Indonesian Agricultural Chatbot System")
    print("=" * 50)
    
    # Test 1: Check if roles are loaded
    print("\n1. Testing User Roles:")
    print(f"   Available roles: {len(USER_ROLES)}")
    for role, description in list(USER_ROLES.items())[:3]:
        print(f"   - {role}: {description[:50]}...")
    
    # Test 2: Check sustainable agriculture knowledge
    print("\n2. Testing Sustainable Agriculture Knowledge:")
    print(f"   Categories: {list(SUSTAINABLE_AGRICULTURE_KNOWLEDGE.keys())}")
    agroecology = SUSTAINABLE_AGRICULTURE_KNOWLEDGE['agroecological_methods']
    print(f"   Agroecological methods: {list(agroecology.keys())}")
    
    # Test 3: Test parameter system
    print("\n3. Testing Parameter System:")
    print(f"   Parameter categories: {list(AGRICULTURAL_PARAMETERS.keys())}")
    
    # Create sample parameters
    sample_parameters = {
        "edaphic": {
            "ph_level": 5.0,  # Below optimal for most crops
            "n_content": 0.10,  # Below optimal
            "organic_matter": 4.0  # Good level
        },
        "hydrologic": {
            "rainfall": 100.0,  # Low rainfall
            "water_table": 60.0  # Moderate depth
        },
        "atmospheric": {
            "air_temperature": 32.0,  # High temperature
            "humidity": 85.0  # High humidity
        }
    }
    
    analysis = analyze_parameters(sample_parameters, "padi")
    print(f"   Parameter analysis status:")
    print(f"   - Edaphic: {analysis['edaphic']['status']}")
    print(f"   - Hydrologic: {analysis['hydrologic']['status']}")
    print(f"   - Atmospheric: {analysis['atmospheric']['status']}")
    
    # Test 4: Test knowledge base search
    print("\n4. Testing Knowledge Base Search:")
    search_results = search_knowledge_base("padi")
    print(f"   Search results for 'padi': {len(search_results)} items found")
    if search_results:
        print(f"   First result: {search_results[0]['item']}")
    
    # Test 5: Test OpenAI client initialization
    print("\n5. Testing OpenAI Client:")
    try:
        client = initialize_openai_client()
        print("   ✅ OpenAI client initialized successfully")
    except Exception as e:
        print(f"   ❌ OpenAI client initialization failed: {e}")
        return False
    
    # Test 6: Test AI response (with mock data to avoid API call)
    print("\n6. Testing AI Response System:")
    try:
        # This is a dry run - we'll test the prompt generation
        from agricultural_chatbot import get_role_specific_prompt
        
        test_prompt = get_role_specific_prompt(
            "Petani Konservasi",
            "Bagaimana mengatasi pH tanah yang terlalu asam?",
            "Jawa Barat"
        )
        
        print("   ✅ Role-specific prompt generated successfully")
        print(f"   Prompt length: {len(test_prompt)} characters")
        
        # Check if the prompt contains key elements
        required_elements = [
            "Forecasting Recovery",
            "LLM-Based Suggestions", 
            "Sustainable Problem-Solving",
            "Edafik",
            "Hidrologik",
            "Atmosferik"
        ]
        
        missing_elements = []
        for element in required_elements:
            if element not in test_prompt:
                missing_elements.append(element)
        
        if missing_elements:
            print(f"   ⚠️  Missing elements in prompt: {missing_elements}")
        else:
            print("   ✅ All required prompt elements present")
            
    except Exception as e:
        print(f"   ❌ AI response system test failed: {e}")
        return False
    
    print("\n✅ All basic functionality tests passed!")
    return True

def test_parameter_analysis_details():
    """Test detailed parameter analysis"""
    print("\n" + "=" * 50)
    print("🔬 Testing Parameter Analysis Details")
    print("=" * 50)
    
    # Test with suboptimal parameters for padi
    suboptimal_params = {
        "edaphic": {
            "ph_level": 4.5,  # Too acidic
            "n_content": 0.08,  # Too low
            "p_content": 0.05,  # Too low
            "organic_matter": 1.5  # Too low
        },
        "hydrologic": {
            "rainfall": 50.0,  # Too low for padi
            "water_table": 30.0,  # Too deep for padi
        },
        "atmospheric": {
            "air_temperature": 38.0,  # Too high
            "humidity": 95.0  # Too high
        }
    }
    
    print("\nTesting with suboptimal parameters for padi:")
    analysis = analyze_parameters(suboptimal_params, "padi")
    
    for category, results in analysis.items():
        print(f"\n{category.upper()} Analysis:")
        print(f"  Status: {results['status']}")
        if results['issues']:
            print("  Issues:")
            for issue in results['issues']:
                print(f"    - {issue}")
        if results['recommendations']:
            print("  Recommendations:")
            for rec in results['recommendations']:
                print(f"    - {rec}")
    
    return True

def main():
    """Main test function"""
    print("🚀 Starting Indonesian Agricultural Chatbot Tests")
    
    try:
        # Run basic functionality tests
        if not test_basic_functionality():
            print("❌ Basic functionality tests failed!")
            return 1
        
        # Run parameter analysis tests
        if not test_parameter_analysis_details():
            print("❌ Parameter analysis tests failed!")
            return 1
        
        print("\n🎉 All tests completed successfully!")
        print("\nTo start the chatbot application, run:")
        print("streamlit run agricultural_chatbot.py")
        
        return 0
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
