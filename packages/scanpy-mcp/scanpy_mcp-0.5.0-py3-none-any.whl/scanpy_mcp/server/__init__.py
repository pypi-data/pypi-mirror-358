from scmcp_shared.mcp_base import BaseMCPManager
from scmcp_shared.server.preset import ScanpyIOMCP
from scmcp_shared.server.preset import ScanpyPreprocessingMCP
from scmcp_shared.server.preset import ScanpyToolsMCP
from scmcp_shared.server.preset import ScanpyPlottingMCP
from .util import ul_mcp
from scmcp_shared.server.auto import auto_mcp
from scmcp_shared.server.code import nb_mcp

class ScanpyMCPManager(BaseMCPManager):
    """Manager class for Scanpy MCP modules."""
    
    def init_mcp(self):
        """Initialize available Scanpy MCP modules."""
        self.available_modules = {
            "io": ScanpyIOMCP().mcp,
            "pp": ScanpyPreprocessingMCP().mcp,
            "tl": ScanpyToolsMCP().mcp,
            "pl": ScanpyPlottingMCP().mcp,
            "ul": ul_mcp,
            "auto": auto_mcp,
            "nb": nb_mcp
        }
