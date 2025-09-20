#!/usr/bin/env python3

import json

def test_local_quiz_data():
    """Test loading local quiz data"""
    try:
        with open('quiz_answers.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            answers = data.get('answers', {})
            
        print("=== LOCAL QUIZ DATA TEST ===")
        print(f"✅ Successfully loaded quiz data")
        print(f"📊 Total questions available: {len(answers)}")
        print(f"📋 Available question numbers: {sorted(answers.keys())}")
        
        print("\n=== QUESTION DETAILS ===")
        for question_num in sorted(answers.keys()):
            answer_data = answers[question_num]
            answer = answer_data['answer'].upper()
            blink_counts = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5}
            blink_count = blink_counts.get(answer, 0)
            print(f"Question {question_num}: Answer {answer} = {blink_count} blink{'s' if blink_count != 1 else ''}")
        
        # Test specific question
        if '1' in answers:
            answer = answers['1']['answer'].upper()
            blink_counts = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5}
            blink_count = blink_counts.get(answer, 0)
            print(f"\n=== TESTING QUESTION 1 ===")
            print(f"Answer: {answer}")
            print(f"Expected blinks: {blink_count}")
            
    except Exception as e:
        print(f"❌ Error loading quiz data: {e}")

if __name__ == "__main__":
    test_local_quiz_data()
