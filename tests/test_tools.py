import os
import tempfile
import pytest
from src.agent.tools import execute_tool, TOOL_DEFINITIONS as tools


class TestToolDefinitions:
    def test_read_file_tool_exists(self):
        tool_names = [t["name"] for t in tools]
        assert "read_file" in tool_names

    def test_read_file_schema_has_required_path(self):
        read_file_tool = next(t for t in tools if t["name"] == "read_file")
        assert "path" in read_file_tool["input_schema"]["required"]

    def test_read_file_schema_has_description(self):
        read_file_tool = next(t for t in tools if t["name"] == "read_file")
        assert read_file_tool["description"]


class TestExecuteTool:
    def test_read_file_returns_contents(self, tmp_path):
        test_file = tmp_path / "test.txt"
        test_file.write_text("hello world")
        result = execute_tool("read_file", {"path": str(test_file)})
        assert result == "hello world"

    def test_read_file_not_found(self):
        result = execute_tool("read_file", {"path": "/nonexistent/file.txt"})
        assert "Error: File not found" in result

    def test_read_file_permission_denied(self, tmp_path):
        test_file = tmp_path / "noperm.txt"
        test_file.write_text("secret")
        test_file.chmod(0o000)
        result = execute_tool("read_file", {"path": str(test_file)})
        assert "Error: Permission denied" in result
        test_file.chmod(0o644)  # restore for cleanup

    def test_unknown_tool(self):
        result = execute_tool("nonexistent_tool", {})
        assert "[error] Unknown tool" in result
