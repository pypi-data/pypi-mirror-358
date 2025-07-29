import pytest
from scmcp_shared.backend import AdataManager
@pytest.fixture
def mcp():
    from scanpy_mcp.server import ScanpyMCPManager
    mcp = ScanpyMCPManager("scanpy-mcp", backend=AdataManager).mcp
    return mcp
