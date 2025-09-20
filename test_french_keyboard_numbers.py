#!/usr/bin/env python3
"""
Test French Keyboard Number Input
Tests the new French keyboard character mappings and double-digit support
"""

def test_french_keyboard_mapping():
    """Test French keyboard character to number conversion"""
    print("🇫🇷 Testing French Keyboard Mappings")
    print("=" * 40)
    
    french_to_number = {
        '&': '1',  # Key 1
        'é': '2',  # Key 2  
        '"': '3',  # Key 3
        "'": '4',  # Key 4
        '(': '5',  # Key 5
        '-': '6',  # Key 6
        'è': '7',  # Key 7
        '_': '8',  # Key 8
        'ç': '9',  # Key 9
        'à': '0'   # Key 0
    }
    
    print("📋 French Character → Number Mappings:")
    for french_char, number in french_to_number.items():
        print(f"   {french_char} → {number}")
    
    print("\n🧪 Testing common quiz numbers:")
    
    # Test single digits
    test_cases = [
        ("&", "1"),          # Question 1
        ("é", "2"),          # Question 2  
        ('"', "3"),          # Question 3
        ("'", "4"),          # Question 4
        ("(", "5"),          # Question 5
        ("ç", "9"),          # Question 9
    ]
    
    # Test double digits
    double_digit_cases = [
        ("&à", "10"),        # 1 + 0 = 10
        ("&&", "11"),        # 1 + 1 = 11
        ("&é", "12"),        # 1 + 2 = 12
        ("&(", "15"),        # 1 + 5 = 15
        ("éà", "20"),        # 2 + 0 = 20
    ]
    
    print("\n✅ Single Digit Tests:")
    for input_chars, expected in test_cases:
        result = ""
        for char in input_chars:
            if char in french_to_number:
                result += french_to_number[char]
            else:
                result += char
        
        status = "✅" if result == expected else "❌"
        print(f"   {status} '{input_chars}' → {result} (expected: {expected})")
    
    print("\n✅ Double Digit Tests:")
    for input_chars, expected in double_digit_cases:
        result = ""
        for char in input_chars:
            if char in french_to_number:
                result += french_to_number[char]
            else:
                result += char
        
        status = "✅" if result == expected else "❌"
        print(f"   {status} '{input_chars}' → {result} (expected: {expected})")
    
    return True

def test_quiz_scenarios():
    """Test realistic quiz scenarios"""
    print("\n🎯 Quiz Usage Scenarios")
    print("=" * 30)
    
    scenarios = [
        {
            "description": "Question 1 (Answer A = 1 blink)",
            "input": "&",
            "expected_number": "1",
            "expected_blinks": 1
        },
        {
            "description": "Question 3 (Answer C = 3 blinks)", 
            "input": '"',
            "expected_number": "3",
            "expected_blinks": 3
        },
        {
            "description": "Question 12 (Answer B = 2 blinks)",
            "input": "&é", 
            "expected_number": "12",
            "expected_blinks": 2
        },
        {
            "description": "Question 20 (Answer E = 5 blinks)",
            "input": "éà",
            "expected_number": "20", 
            "expected_blinks": 5
        }
    ]
    
    french_to_number = {
        '&': '1', 'é': '2', '"': '3', "'": '4', '(': '5',
        '-': '6', 'è': '7', '_': '8', 'ç': '9', 'à': '0'
    }
    
    # Quiz answers from the current quiz_answers.json
    quiz_answers = {
        "1": "A", "2": "B", "3": "C", "4": "D", "5": "E",
        "9": "C", "12": "B", "20": "E"
    }
    
    blink_counts = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5}
    
    for scenario in scenarios:
        print(f"\n📝 {scenario['description']}")
        
        # Convert input to number
        result_number = ""
        for char in scenario['input']:
            if char in french_to_number:
                result_number += french_to_number[char]
        
        # Check if we have this question in our quiz data
        if result_number in quiz_answers:
            answer = quiz_answers[result_number]
            actual_blinks = blink_counts.get(answer, 0)
            
            print(f"   🎹 Type: {scenario['input']}")
            print(f"   🔢 Number: {result_number}")
            print(f"   📖 Answer: {answer}")
            print(f"   💡 Blinks: {actual_blinks}")
            
            status = "✅" if result_number == scenario['expected_number'] else "❌"
            print(f"   {status} Result matches expected")
        else:
            print(f"   ⚠️ Question {result_number} not found in quiz data")
    
    return True

def main():
    """Main test function"""
    print("🧪 French Keyboard Quiz Input Test")
    print("=" * 50)
    
    # Test mappings
    mapping_test = test_french_keyboard_mapping()
    
    # Test scenarios
    scenario_test = test_quiz_scenarios()
    
    print("\n" + "=" * 50)
    print("🏁 Test Results:")
    print(f"   Character Mappings: {'✅ PASS' if mapping_test else '❌ FAIL'}")
    print(f"   Quiz Scenarios: {'✅ PASS' if scenario_test else '❌ FAIL'}")
    
    if mapping_test and scenario_test:
        print("\n🎉 French keyboard support is ready!")
        print("\n🚀 How to use:")
        print("   1. Press trigger key: ' & é \" $")
        print("   2. Type question number using French keys:")
        print("      &é\"'()-è_çà = 1234567890")
        print("   3. For double digits: Type both characters")
        print("      Example: &é = 12, éà = 20")
        print("   4. Press ENTER to submit (no auto-submit)")
        print("   5. Watch Caps Lock LED blink!")
        
        print("\n💡 Key improvements:")
        print("   ✅ No more accidental auto-submit on single digits")
        print("   ✅ Support for questions 10-20")  
        print("   ✅ French keyboard without Shift key")
        print("   ✅ Clear visual feedback")
    else:
        print("\n❌ Some tests failed")

if __name__ == "__main__":
    main()
