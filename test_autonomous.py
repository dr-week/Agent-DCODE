#!/usr/bin/env python3
"""
Test script for autonomous agent loop.
Demonstrates continuous planning, execution, and error recovery.
"""

import sys
import json
from autonomous_agent import run_autonomous_agent, AutonomousAgent

def test_basic_task():
    """Test 1: Basic file creation task"""
    print("\n" + "="*60)
    print("TEST 1: Basic File Creation")
    print("="*60)
    
    result = run_autonomous_agent(
        goal="Create a Python script in projects/ that prints 'Hello from Autonomous Agent'",
        project_name="test_basic",
        max_iterations=5
    )
    
    print("\n📊 Result:")
    print(f"  Success: {result['success']}")
    print(f"  Iterations: {result['iterations']}")
    print(f"  Actions: {result['actions_executed']}")
    if result.get('errors'):
        print(f"  Errors: {result['errors']}")
    
    return result['success']


def test_complex_task():
    """Test 2: More complex coding task"""
    print("\n" + "="*60)
    print("TEST 2: Complex Coding Task")
    print("="*60)
    
    result = run_autonomous_agent(
        goal="Create a Python calculator script with add, subtract, multiply, divide functions and a main function that tests all operations",
        project_name="test_calculator",
        max_iterations=7,
        context="The script should have proper error handling and be located in projects/calculator.py"
    )
    
    print("\n📊 Result:")
    print(f"  Success: {result['success']}")
    print(f"  Iterations: {result['iterations']}")
    print(f"  Actions: {result['actions_executed']}")
    if result.get('errors'):
        print(f"  Errors: {result['errors'][:2]}")  # Show first 2 errors
    
    return result['success']


def test_recovery():
    """Test 3: Error detection and recovery"""
    print("\n" + "="*60)
    print("TEST 3: Error Recovery")
    print("="*60)
    
    result = run_autonomous_agent(
        goal="Create and test a Python function that validates email addresses, then fix any errors",
        project_name="test_recovery",
        max_iterations=8,
        context="Use regex for validation. Location: projects/email_validator.py"
    )
    
    print("\n📊 Result:")
    print(f"  Success: {result['success']}")
    print(f"  Iterations: {result['iterations']}")
    print(f"  Plan steps: {len(result.get('plan', []))}")
    if result.get('errors'):
        print(f"  Recovery attempts: {len(result['errors'])}")
    
    return result['success']


def manual_test():
    """Test with custom goal"""
    print("\n" + "="*60)
    print("MANUAL TEST: Custom Goal")
    print("="*60)
    
    goal = input("Enter your goal: ").strip()
    if not goal:
        goal = "Create a simple Python script that adds two numbers"
    
    context = input("Enter context (optional): ").strip()
    iterations = input("Max iterations (default 5): ").strip()
    iterations = int(iterations) if iterations.isdigit() else 5
    
    result = run_autonomous_agent(
        goal=goal,
        project_name="manual_test",
        max_iterations=iterations,
        context=context
    )
    
    print("\n📊 Final Result:")
    print(json.dumps({
        "success": result['success'],
        "iterations": result['iterations'],
        "actions_executed": result['actions_executed'],
        "error_count": len(result.get('errors', [])),
        "goal": result['goal']
    }, indent=2))
    
    return result['success']


if __name__ == "__main__":
    print("\n🤖 Autonomous Agent Loop Tests")
    print("="*60)
    print("Testing continuous planning, execution, and error recovery")
    print("="*60)
    
    if len(sys.argv) > 1:
        test_num = sys.argv[1]
        if test_num == "1":
            success = test_basic_task()
        elif test_num == "2":
            success = test_complex_task()
        elif test_num == "3":
            success = test_recovery()
        elif test_num == "manual":
            success = manual_test()
        else:
            print("Unknown test. Options: 1, 2, 3, manual")
            success = False
    else:
        print("\nAvailable tests:")
        print("  python test_autonomous.py 1       - Basic file creation")
        print("  python test_autonomous.py 2       - Complex coding task")
        print("  python test_autonomous.py 3       - Error recovery")
        print("  python test_autonomous.py manual  - Custom goal")
        print("\nRunning all tests for demo...\n")
        
        test1 = test_basic_task()
        test2 = test_complex_task()
        test3 = test_recovery()
        
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"Test 1 (Basic):    {'✅ PASS' if test1 else '❌ FAIL'}")
        print(f"Test 2 (Complex):  {'✅ PASS' if test2 else '❌ FAIL'}")
        print(f"Test 3 (Recovery): {'✅ PASS' if test3 else '❌ FAIL'}")
        success = test1 or test2 or test3
    
    print("\n" + "="*60)
    sys.exit(0 if success else 1)
