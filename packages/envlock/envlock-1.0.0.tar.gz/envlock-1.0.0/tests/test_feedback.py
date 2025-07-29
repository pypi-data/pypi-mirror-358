import sys
import types
import pytest
from click.testing import CliRunner
from main import cli


def test_feedback_opens_browser(monkeypatch):
    """
    Test that the feedback command attempts to open the browser and prints the link.
    """
    runner = CliRunner()
    opened = {}
    def fake_open(url):
        opened['url'] = url
        return True
    monkeypatch.setattr('webbrowser.open', fake_open)
    result = runner.invoke(cli, ['feedback'])
    assert result.exit_code == 0
    assert 'feedback/feature request page' in result.output
    assert 'github.com/nikhiljohn10/envlock/issues/new/choose' in result.output
    assert opened['url'].startswith('https://github.com/nikhiljohn10/envlock/issues/new/choose')


def test_feedback_prints_link_on_exception(monkeypatch):
    """
    Test that the feedback command prints the link if webbrowser.open fails.
    """
    runner = CliRunner()
    def fake_open(url):
        raise Exception("Browser failed")
    monkeypatch.setattr('webbrowser.open', fake_open)
    result = runner.invoke(cli, ['feedback'])
    assert result.exit_code == 0
    assert 'Please submit feedback or feature requests at:' in result.output
    assert 'github.com/nikhiljohn10/envlock/issues/new/choose' in result.output
