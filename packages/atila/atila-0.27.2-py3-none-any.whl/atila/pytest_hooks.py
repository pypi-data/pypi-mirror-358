import pytest
from . import apidoc
from rs4 import pathtool
import os

def pytest_configure(config):
    config.addinivalue_line (
        "markers", "slow: mark test to run only on --mark-slow"
    )
    config.addinivalue_line (
        "markers", "extern: mark test to run only on --mark-exteranl"
    )

def pytest_addoption (parser):
    parser.addoption (
        "--mark-slow", action="store_true", default=False, help="Run including slow marked tests"
    )
    parser.addoption (
        "--mark-extern", action="store_true", default=False, help="Run including exteranl marked tests"
    )
    parser.addoption (
        "--generate-api-doc", action='store_true', default=False, help="Generate API document at ./"
    )
    parser.addoption (
        "--no-launch", action='store_true', default=False, help="Do not launch server. Launch server with debugger and run pytest with this option"
    )

@pytest.fixture
def dryrun (request):
    return request.config.getoption ("--no-launch")


def pytest_collection_modifyitems (config, items):
    skip_slow = pytest.mark.skip (reason = "need --mark-slow option to run")
    skip_extern = pytest.mark.skip (reason = "need --mark-extern option to run")
    for item in items:
        if not config.getoption ("--mark-slow") and "slow" in item.keywords:
            item.add_marker (skip_slow)
        if not config.getoption ("--mark-extern") and "extern" in item.keywords:
            item.add_marker (skip_extern)

def pytest_sessionstart (session):
    if session.config.getoption ("--generate-api-doc"):
        apidoc.truncate_log_dir ()

def pytest_sessionfinish (session, exitstatus):
    subdname = session.config.args [0]
    if session.config.args [0] == os.getcwd ():
        subdname = 'index'
    if exitstatus == 0 and session.config.getoption ("--generate-api-doc"):
        apidoc.build_doc ('./{}.md'.format (subdname))
