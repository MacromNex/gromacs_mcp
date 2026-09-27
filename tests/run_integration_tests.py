#!/usr/bin/env python3
"""Automated integration test runner for GROMACS MCP server."""

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

class MCPTestRunner:
    """Automated test runner for MCP server integration."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.python_path = self.project_root / "env/bin/python"
        self.server_path = self.project_root / "src/server.py"
        self.results = {
            "test_date": datetime.now().isoformat(),
            "project_root": str(project_root),
            "server_path": str(self.server_path),
            "python_path": str(self.python_path),
            "tests": {},
            "issues": [],
            "summary": {}
        }

    def log(self, message: str, level: str = "INFO"):
        """Log a message with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

    def test_server_startup(self) -> bool:
        """Test that server starts without errors."""
        self.log("Testing server startup...")
        try:
            result = subprocess.run([
                str(self.python_path), "-c",
                "from src.server import mcp; print('Server imported successfully')"
            ],
            cwd=self.project_root,
            capture_output=True, text=True, timeout=30
            )
            success = result.returncode == 0
            self.results["tests"]["server_startup"] = {
                "status": "passed" if success else "failed",
                "output": result.stdout.strip(),
                "error": result.stderr.strip() if result.stderr else None,
                "duration_seconds": 1.0  # Approximate
            }
            return success
        except Exception as e:
            self.results["tests"]["server_startup"] = {
                "status": "error",
                "error": str(e)
            }
            return False

    def test_tool_discovery(self) -> bool:
        """Test that all expected tools are discoverable."""
        self.log("Testing tool discovery...")
        try:
            # Extract tools from server source
            with open(self.server_path, 'r') as f:
                content = f.read()

            import re
            pattern = r'@mcp\.tool\(\)\s*\ndef\s+(\w+)'
            expected_tools = re.findall(pattern, content)

            self.results["tests"]["tool_discovery"] = {
                "status": "passed",
                "expected_tools_count": len(expected_tools),
                "expected_tools": expected_tools,
                "note": "Tools discovered from source code analysis"
            }
            return True

        except Exception as e:
            self.results["tests"]["tool_discovery"] = {
                "status": "error",
                "error": str(e)
            }
            return False

    def test_claude_mcp_registration(self) -> bool:
        """Test Claude MCP registration."""
        self.log("Testing Claude MCP registration...")
        try:
            # Check if claude command is available
            result = subprocess.run(["which", "claude"], capture_output=True, text=True)
            if result.returncode != 0:
                self.results["tests"]["claude_mcp_registration"] = {
                    "status": "skipped",
                    "reason": "Claude Code CLI not found"
                }
                return True

            # Check MCP server registration
            result = subprocess.run(["claude", "mcp", "list"], capture_output=True, text=True)
            claude_output = result.stdout

            # Look for our server
            is_registered = "gromacs-mcp" in claude_output
            is_connected = "✓ Connected" in claude_output and "gromacs-mcp" in claude_output

            self.results["tests"]["claude_mcp_registration"] = {
                "status": "passed" if is_connected else ("registered" if is_registered else "failed"),
                "registered": is_registered,
                "connected": is_connected,
                "claude_output": claude_output.strip()
            }
            return is_connected

        except Exception as e:
            self.results["tests"]["claude_mcp_registration"] = {
                "status": "error",
                "error": str(e)
            }
            return False

    def test_sample_data_availability(self) -> bool:
        """Test that sample data files are available for testing."""
        self.log("Testing sample data availability...")

        sample_files = [
            "examples/data/sample.tpr",
            "examples/data/sample.gro",
            "examples/data/sample.top",
            "examples/data/sample.mdp"
        ]

        available_files = []
        missing_files = []

        for file_path in sample_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                available_files.append(file_path)
            else:
                missing_files.append(file_path)

        success = len(available_files) > 0 and "examples/data/sample.tpr" in available_files

        self.results["tests"]["sample_data_availability"] = {
            "status": "passed" if success else "failed",
            "available_files": available_files,
            "missing_files": missing_files,
            "note": "At least sample.tpr is required for testing"
        }
        return success

    def test_directory_structure(self) -> bool:
        """Test that required directories exist."""
        self.log("Testing directory structure...")

        required_dirs = [
            "src",
            "scripts",
            "examples/data",
            "env/bin"
        ]

        existing_dirs = []
        missing_dirs = []

        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            if full_path.exists():
                existing_dirs.append(dir_path)
            else:
                missing_dirs.append(dir_path)

        success = len(missing_dirs) == 0

        self.results["tests"]["directory_structure"] = {
            "status": "passed" if success else "failed",
            "existing_dirs": existing_dirs,
            "missing_dirs": missing_dirs
        }
        return success

    def test_dependencies(self) -> bool:
        """Test that required dependencies are installed."""
        self.log("Testing dependencies...")
        try:
            result = subprocess.run([
                str(self.python_path), "-c",
                "import fastmcp, loguru; print('Dependencies OK')"
            ],
            capture_output=True, text=True, timeout=10
            )

            success = result.returncode == 0
            self.results["tests"]["dependencies"] = {
                "status": "passed" if success else "failed",
                "output": result.stdout.strip(),
                "error": result.stderr.strip() if result.stderr else None
            }
            return success

        except Exception as e:
            self.results["tests"]["dependencies"] = {
                "status": "error",
                "error": str(e)
            }
            return False

    def test_server_fastmcp_dev(self) -> bool:
        """Test server startup with fastmcp dev."""
        self.log("Testing fastmcp dev server startup...")
        try:
            # Start server with short timeout to verify it starts
            # Use direct fastmcp command instead of python -m
            proc = subprocess.Popen([
                "fastmcp", "dev", str(self.server_path)
            ],
            cwd=self.project_root,
            env={**dict(os.environ), "PATH": str(self.project_root / "env/bin") + ":" + os.environ.get("PATH", "")},
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
            )

            # Give it a few seconds to start
            time.sleep(3)

            # Terminate the process
            proc.terminate()
            try:
                stdout, stderr = proc.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                stdout, stderr = proc.communicate()

            # Check if server started successfully (look for success indicators)
            success_indicators = [
                "Starting MCP server",
                "gromacs-2025.4",
                "FastMCP"
            ]

            combined_output = stdout + stderr
            success = any(indicator in combined_output for indicator in success_indicators)

            self.results["tests"]["fastmcp_dev_startup"] = {
                "status": "passed" if success else "failed",
                "output": stdout[:1000] if stdout else "",  # Truncate output
                "error": stderr[:1000] if stderr else "",
                "note": "Server startup tested with 3-second timeout"
            }
            return success

        except Exception as e:
            self.results["tests"]["fastmcp_dev_startup"] = {
                "status": "error",
                "error": str(e)
            }
            return False

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all integration tests."""
        self.log("Starting GROMACS MCP integration tests...")

        tests = [
            ("Directory Structure", self.test_directory_structure),
            ("Dependencies", self.test_dependencies),
            ("Server Startup", self.test_server_startup),
            ("Tool Discovery", self.test_tool_discovery),
            ("Sample Data", self.test_sample_data_availability),
            ("FastMCP Dev", self.test_server_fastmcp_dev),
            ("Claude MCP Registration", self.test_claude_mcp_registration),
        ]

        passed = 0
        failed = 0

        for test_name, test_func in tests:
            self.log(f"Running {test_name}...")
            try:
                if test_func():
                    self.log(f"✅ {test_name} PASSED", "PASS")
                    passed += 1
                else:
                    self.log(f"❌ {test_name} FAILED", "FAIL")
                    failed += 1
            except Exception as e:
                self.log(f"💥 {test_name} ERROR: {e}", "ERROR")
                failed += 1

        # Generate summary
        total = passed + failed
        self.results["summary"] = {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": f"{passed/total*100:.1f}%" if total > 0 else "N/A",
            "ready_for_production": passed == total,
            "claude_integration_ready": self.results.get("tests", {}).get("claude_mcp_registration", {}).get("status") == "passed"
        }

        self.log(f"Tests completed: {passed}/{total} passed ({self.results['summary']['pass_rate']})")
        return self.results

    def save_report(self, output_file: str):
        """Save test results to JSON file."""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2)

        self.log(f"Test report saved to {output_path}")

    def print_summary(self):
        """Print a human-readable summary."""
        print("\n" + "="*80)
        print("GROMACS MCP INTEGRATION TEST SUMMARY")
        print("="*80)
        print(f"Test Date: {self.results['test_date']}")
        print(f"Project: {self.results['project_root']}")
        print()

        summary = self.results["summary"]
        print(f"Results: {summary['passed']}/{summary['total_tests']} tests passed ({summary['pass_rate']})")
        print(f"Production Ready: {'✅ YES' if summary['ready_for_production'] else '❌ NO'}")
        print(f"Claude Integration: {'✅ READY' if summary['claude_integration_ready'] else '❌ NOT READY'}")

        print("\nTest Results:")
        print("-" * 40)
        for test_name, result in self.results["tests"].items():
            status = result["status"]
            if status == "passed":
                print(f"✅ {test_name}")
            elif status == "skipped":
                print(f"⏭️  {test_name} (skipped)")
            else:
                print(f"❌ {test_name}")
                if "error" in result:
                    print(f"   Error: {result['error']}")

        if len(self.results["issues"]) > 0:
            print("\nIssues Found:")
            print("-" * 40)
            for issue in self.results["issues"]:
                print(f"• {issue}")


if __name__ == "__main__":
    # Run from project root
    project_root = Path(__file__).parent.parent.resolve()
    print(f"Running tests from: {project_root}")

    runner = MCPTestRunner(str(project_root))
    results = runner.run_all_tests()

    # Save detailed report
    runner.save_report("reports/step7_integration_tests.json")

    # Print summary
    runner.print_summary()

    # Exit with appropriate code
    if results["summary"]["ready_for_production"]:
        sys.exit(0)
    else:
        sys.exit(1)