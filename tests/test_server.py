#!/usr/bin/env python3
"""Test suite for GROMACS MCP server functionality."""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from server import mcp
from utils import validate_input_file, setup_output_directory, format_tool_result

class TestMCPServer:
    """Test MCP server functionality."""

    def setup_method(self):
        """Setup for each test method."""
        self.test_data_dir = Path(__file__).parent.parent / "examples" / "data"
        self.sample_tpr = self.test_data_dir / "sample.tpr"

    def test_server_info(self):
        """Test server information tool."""
        # This would normally use mcp.call_tool() but we'll test the function directly
        from server import get_server_info
        result = get_server_info()

        assert result["status"] == "success"
        assert "server_name" in result
        assert result["server_name"] == "gromacs-2025.4"
        assert "capabilities" in result

    def test_list_commands(self):
        """Test command listing tool."""
        from server import list_available_commands
        result = list_available_commands()

        assert result["status"] == "success"
        assert "sync_tools" in result
        assert "submit_tools" in result
        assert "analyze_tpr" in result["sync_tools"]
        assert "submit_md_simulation" in result["submit_tools"]

    def test_validate_input_file(self):
        """Test input file validation utility."""
        # Test valid file
        result = validate_input_file(str(self.sample_tpr), ".tpr")
        assert result["valid"] is True
        assert "file_size" in result

        # Test nonexistent file
        result = validate_input_file("/nonexistent/file.tpr", ".tpr")
        assert result["valid"] is False
        assert "not found" in result["error"]

        # Test wrong extension
        result = validate_input_file(str(self.sample_tpr), ".gro")
        assert result["valid"] is False
        assert "Expected .gro" in result["error"]

    def test_setup_output_directory(self):
        """Test output directory setup utility."""
        # Test with custom directory
        result = setup_output_directory("test_output", "default")
        assert result["success"] is True
        assert "output_dir" in result

        # Test with file path
        result = setup_output_directory("test_output/result.txt", "default")
        assert result["success"] is True
        assert result["output_file"] is not None

    def test_format_tool_result(self):
        """Test result formatting utility."""
        # Test success result
        result = format_tool_result(True, {"key": "value"}, output_files=["file1.txt"])
        assert result["status"] == "success"
        assert result["key"] == "value"
        assert result["output_files"] == ["file1.txt"]

        # Test error result
        result = format_tool_result(False, error_message="Test error")
        assert result["status"] == "error"
        assert result["error"] == "Test error"

    def test_analyze_tpr_validation(self):
        """Test TPR analysis input validation."""
        from server import analyze_tpr

        # Test with nonexistent file
        result = analyze_tpr("/nonexistent/file.tpr")
        assert result["status"] == "error"
        assert "not found" in result["error"]

    def test_submit_md_simulation_validation(self):
        """Test MD simulation submission validation."""
        from server import submit_md_simulation

        # Test with nonexistent file
        result = submit_md_simulation("/nonexistent/file.tpr")
        assert result["status"] == "error"
        assert "not found" in result["error"]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])