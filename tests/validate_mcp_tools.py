#!/usr/bin/env python3
"""Direct validation of MCP tools functionality."""

import json
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

def test_tool_import_and_basic_functionality():
    """Test that we can import and call MCP tools directly."""
    print("Testing MCP tool import and basic functionality...")

    try:
        # Import the server module
        from src.server import mcp
        print("✅ Successfully imported MCP server")

        # Test tool discovery by examining the decorated functions
        import inspect
        import src.server as server_module

        # Find all functions in the module
        functions = inspect.getmembers(server_module, inspect.isfunction)
        tool_functions = []

        for name, func in functions:
            # Check if function has the right characteristics for an MCP tool
            if hasattr(func, '__annotations__') and hasattr(func, '__doc__') and func.__doc__:
                tool_functions.append(name)

        print(f"✅ Found {len(tool_functions)} potential tool functions")

        # Test specific tools by calling them directly
        test_results = {}

        # Test 1: get_server_info (should always work)
        try:
            result = server_module.get_server_info()
            if result.get("success"):
                test_results["get_server_info"] = "✅ PASS"
                print("✅ get_server_info works correctly")
            else:
                test_results["get_server_info"] = f"❌ FAIL: {result.get('error_message', 'Unknown error')}"
        except Exception as e:
            test_results["get_server_info"] = f"❌ ERROR: {e}"

        # Test 2: list_available_commands
        try:
            result = server_module.list_available_commands()
            if result.get("success"):
                test_results["list_available_commands"] = "✅ PASS"
                print("✅ list_available_commands works correctly")
            else:
                test_results["list_available_commands"] = f"❌ FAIL: {result.get('error_message', 'Unknown error')}"
        except Exception as e:
            test_results["list_available_commands"] = f"❌ ERROR: {e}"

        # Test 3: analyze_tpr with sample data
        sample_tpr = project_root / "examples" / "data" / "sample.tpr"
        if sample_tpr.exists():
            try:
                result = server_module.analyze_tpr(
                    input_file=str(sample_tpr),
                    output_format="json"
                )
                if result.get("success"):
                    test_results["analyze_tpr"] = "✅ PASS"
                    print("✅ analyze_tpr works with sample data")
                else:
                    test_results["analyze_tpr"] = f"❌ FAIL: {result.get('error_message', 'Unknown error')}"
            except Exception as e:
                test_results["analyze_tpr"] = f"❌ ERROR: {e}"
        else:
            test_results["analyze_tpr"] = "⏭️ SKIP: No sample.tpr file"

        # Test 4: list_jobs (job management)
        try:
            result = server_module.list_jobs()
            if result.get("success") or "jobs" in result:
                test_results["list_jobs"] = "✅ PASS"
                print("✅ list_jobs works correctly")
            else:
                test_results["list_jobs"] = f"❌ FAIL: {result.get('error_message', 'Unknown error')}"
        except Exception as e:
            test_results["list_jobs"] = f"❌ ERROR: {e}"

        # Test 5: Error handling with invalid input
        try:
            result = server_module.analyze_tpr(input_file="/nonexistent/file.tpr")
            if not result.get("success") and "error_message" in result:
                test_results["error_handling"] = "✅ PASS"
                print("✅ Error handling works correctly")
            else:
                test_results["error_handling"] = "❌ FAIL: Should have returned error for invalid file"
        except Exception as e:
            test_results["error_handling"] = f"❌ ERROR: {e}"

        # Summary
        total_tests = len(test_results)
        passed_tests = sum(1 for result in test_results.values() if result.startswith("✅"))

        print(f"\n{'='*60}")
        print(f"MCP TOOL VALIDATION SUMMARY")
        print(f"{'='*60}")
        print(f"Tests run: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Pass rate: {passed_tests/total_tests*100:.1f}%")
        print()

        for tool_name, result in test_results.items():
            print(f"{result} {tool_name}")

        print(f"\n{'='*60}")

        # Return success if all critical tests passed
        critical_tools = ["get_server_info", "list_available_commands", "error_handling"]
        critical_passed = all(test_results.get(tool, "").startswith("✅") for tool in critical_tools)

        if critical_passed:
            print("🎉 ALL CRITICAL TESTS PASSED - MCP server is ready for use!")
            return True
        else:
            print("❌ Some critical tests failed - see results above")
            return False

    except Exception as e:
        print(f"❌ FATAL ERROR: Failed to import or test MCP server: {e}")
        return False

if __name__ == "__main__":
    success = test_tool_import_and_basic_functionality()
    sys.exit(0 if success else 1)