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

    def test_write_file_creates_file(self, tmp_path):
        target = tmp_path / "output.txt"
        result = execute_tool("write_file", {"path": str(target), "content": "hello"})
        assert "Successfully wrote" in result
        assert target.read_text() == "hello"

    def test_write_file_creates_parent_dirs(self, tmp_path):
        target = tmp_path / "sub" / "dir" / "output.txt"
        result = execute_tool("write_file", {"path": str(target), "content": "nested"})
        assert "Successfully wrote" in result
        assert target.read_text() == "nested"

    def test_write_file_no_parent_dir(self, monkeypatch, tmp_path):
        monkeypatch.chdir(tmp_path)
        result = execute_tool("write_file", {"path": "bare_file.txt", "content": "no parent"})
        assert "Successfully wrote" in result
        assert (tmp_path / "bare_file.txt").read_text() == "no parent"

    def test_write_file_overwrites_existing(self, tmp_path):
        target = tmp_path / "existing.txt"
        target.write_text("old content")
        execute_tool("write_file", {"path": str(target), "content": "new content"})
        assert target.read_text() == "new content"

    def test_run_command_approved(self):
        result = execute_tool("run_command", {"command": "echo hello"}, input_func=lambda _: "y")
        assert "hello" in result

    def test_run_command_rejected(self):
        result = execute_tool("run_command", {"command": "echo hello"}, input_func=lambda _: "n")
        assert "rejected" in result.lower()

    def test_run_command_captures_stderr(self):
        result = execute_tool("run_command", {"command": "echo err >&2"}, input_func=lambda _: "y")
        assert "err" in result
        assert "STDERR" in result

    def test_run_command_timeout(self):
        result = execute_tool("run_command", {"command": "sleep 10", "timeout": 1}, input_func=lambda _: "y")
        assert "timed out" in result.lower()

    def test_run_command_nonzero_exit(self):
        result = execute_tool("run_command", {"command": "exit 1"}, input_func=lambda _: "y")
        assert "Exit code: 1" in result

    def test_unknown_tool(self):
        result = execute_tool("nonexistent_tool", {})
        assert "[error] Unknown tool" in result
