import pytest

@pytest.fixture
def mcp():
    from infercnv_mcp.server import InferCNVMCPManager
    from scmcp_shared.backend import AdataManager
    mcp = InferCNVMCPManager("infercnv-mcp", backend=AdataManager).mcp
    return mcp
