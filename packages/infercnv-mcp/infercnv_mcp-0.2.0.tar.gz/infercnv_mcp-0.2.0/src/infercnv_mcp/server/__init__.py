from scmcp_shared.mcp_base import BaseMCPManager
from scmcp_shared.server.preset import io_mcp
from .preset.tl import tl_mcp
from .preset.util import ul_mcp
from .preset.pl import pl_mcp
from .preset.pp import pp_mcp
from scmcp_shared.server.code import nb_mcp

class InferCNVMCPManager(BaseMCPManager):
    """Manager class for Scanpy MCP modules."""
    
    def init_mcp(self):
        """Initialize available Scanpy MCP modules."""
        self.available_modules = {
            "io": io_mcp,
            "pp": pp_mcp,
            "tl": tl_mcp,
            "pl": pl_mcp,
            "ul": ul_mcp,
            "nb": nb_mcp
        }
