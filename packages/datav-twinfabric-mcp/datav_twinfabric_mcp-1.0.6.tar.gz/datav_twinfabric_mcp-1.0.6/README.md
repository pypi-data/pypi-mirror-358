# DTF MCP server

Python bridge for interacting with Unreal Engine 5.2 using the Model Context Protocol (MCP).

## Setup

1. Make sure Python 3.10+ is installed
2. Install `uv` if you haven't already:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
3. Create and activate a virtual environment:
   ```bash
   cd Python
   uv venv
   source .venv/bin/activate  # On Unix/macOS
   # or
   .venv\Scripts\activate     # On Windows
   ```
4. Install dependencies:
   ```bash
   uv pip install -e .
   ```

At this point, you can configure your MCP Client (Claude Desktop, Cursor, Windsurf) to use the Unreal MCP Server as per the [Configuring your MCP Client](README.md#configuring-your-mcp-client).

## Test on Cherry Studio

1. Add MCP server in Settings.
- Type: ```stdio```
- Command: ```uv```
- Arguments: 
```
--directory
absolute/path/to/this/repository/Python
run
twinfabric_mcp_server.py
```
- Environment Variables:
```
DASHSCOPE_API_KEY=your/dashscope/api/key
LOCATION_APP_ID=095e3f5c21f44dd78f3e97e9be858341
LOG_DIR = D:/, // directory of log
TwinFabricHost = 30.232.92.111 // public IP address of the host where the TwinFabric client is located
```
or in json format
```
{
  "mcpServers": {
    "twinfabric_mcp_server": {
      "name": "DataV.TwinFabric-MCP",
      "command": "uvx",
      "args": [
        "datav-twinfabric-mcp"
      ],
      "env": {
        "DASHSCOPE_API_KEY": "sk-aab3831be22b454590f6e7fa98685f19",
        "LOCATION_APP_ID": "095e3f5c21f44dd78f3e97e9be858341",
        "LOG_DIR": "D:/",
        "TwinFabricHost": "30.232.92.111"
      }
    }
  }
}
```

Note: You can get your DASHSCOPE_API_KEY according to [阿里云百炼-账号设置-获取 API Key](https://bailian.console.aliyun.com/?spm=5176.12818093_47.console-base_search-panel.dtab-product_sfm.5adc2cc9tnY5Tm&scm=20140722.S_sfm._.ID_sfm-RL_%E7%99%BE%E7%82%BC-LOC_console_console-OR_ser-V_4-P0_0&tab=doc#/doc/?type=model&url=https%3A%2F%2Fhelp.aliyun.com%2Fdocument_detail%2F2840915.html&renderType=iframe).

2. Save and Start the server.
3. Switch to the default assistant page, add MCP server at the bottom, and start your conversations.
