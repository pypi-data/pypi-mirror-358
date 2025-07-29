# src/file_reader_mcp/server.py
from mcp.server.fastmcp import FastMCP
import os

# Create an MCP server
mcp = FastMCP("file-reader")

# 預設允許的根目錄，可以透過環境變數覆蓋
ALLOWED_ROOT = os.getenv("FILE_READER_ROOT", "D:\\data")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool()
def read_file(path: str) -> str:
    """
    讀取檔案/查看檔案/讀取
    """
    if not path.startswith(ALLOWED_ROOT):
        return "存取拒絕,這個路徑不在允許目錄內"

    # 增加安全检查（可选）
    if not os.path.isfile(path):
        return f"沒有發現檔案: {path}"
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

@mcp.tool()
def list_directory_tree(path: str) -> str:
    """
    列出目錄/列出可讀取目錄
    """
    # 檢查路徑是否在允許範圍內
    if not path.startswith(ALLOWED_ROOT):
        return "存取拒絕,這個路徑不在允許目錄內"
    
    try:
        def generate_tree(path, indent=0):
            tree = ""
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                tree += "  " * indent + item + "\n"
                if os.path.isdir(item_path):
                    tree += generate_tree(item_path, indent + 1)
            return tree

        return generate_tree(path)
    except Exception as e:
        return f"Error listing directory tree: {str(e)}"

def main():
    """主要執行函數"""
    print(f"File Reader MCP Server starting...")
    print(f"Allowed root directory: {ALLOWED_ROOT}")
    mcp.run()

if __name__ == "__main__":
    main()