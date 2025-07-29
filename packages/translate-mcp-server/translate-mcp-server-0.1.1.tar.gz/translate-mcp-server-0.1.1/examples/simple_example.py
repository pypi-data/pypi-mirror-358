# simple_example.py

"""
这个示例展示了如何使用国际化工作流MCP服务器的各个功能
"""

import os
import json
import asyncio
from mcp.client import MCPClient

# 连接到MCP服务器
async def connect_to_server():
    """连接到MCP服务器"""
    # 假设服务器已经在本地启动
    client = MCPClient("http://localhost:8000")
    await client.connect()
    return client

# 提取中文示例
async def extract_chinese_example(client, project_dir):
    """提取中文示例"""
    print("\n=== 提取中文示例 ===")
    result = await client.call("extract_chinese_text", {
        "directory": project_dir,
        "file_extensions": [".js", ".jsx", ".ts", ".tsx", ".vue", ".py"]
    })
    
    print(f"共提取到 {len(result)} 个中文字符串")
    return result

# 翻译中文示例
async def translate_chinese_example(client, chinese_dict):
    """翻译中文示例"""
    print("\n=== 翻译中文示例 ===")
    
    # 保存中文到临时文件
    temp_file = "temp_chinese.json"
    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(chinese_dict, f, ensure_ascii=False, indent=2)
    
    # 调用翻译API
    # 注意：需要设置阿里云访问密钥
    result = await client.call("translate_chinese_to_english", {
        "input_file": temp_file,
        "access_key_id": "YOUR_ALIYUN_ACCESS_KEY_ID",  # 替换为你的阿里云访问密钥ID
        "access_key_secret": "YOUR_ALIYUN_ACCESS_KEY_SECRET"  # 替换为你的阿里云访问密钥密码
    })
    
    # 清理临时文件
    if os.path.exists(temp_file):
        os.remove(temp_file)
    
    print(f"共翻译了 {len(result)} 个中文字符串")
    return result

# 替换中文示例
async def replace_chinese_example(client, project_dir, translations):
    """替换中文示例"""
    print("\n=== 替换中文示例 ===")
    
    # 保存翻译结果到临时文件
    translations_file = "temp_translations.json"
    with open(translations_file, "w", encoding="utf-8") as f:
        json.dump(translations, f, ensure_ascii=False, indent=2)
    
    # 调用替换API
    result = await client.call("replace_chinese_in_files", {
        "directory": project_dir,
        "translations_file": translations_file,
        "file_extensions": [".js", ".jsx", ".ts", ".tsx", ".vue", ".py"],
        "create_backup": True
    })
    
    # 清理临时文件
    if os.path.exists(translations_file):
        os.remove(translations_file)
    
    print(f"共处理了 {result['total_files']} 个文件，修改了 {result['modified_files']} 个文件")
    return result

# 完整工作流示例
async def complete_workflow_example(client, project_dir):
    """完整工作流示例"""
    print("\n=== 完整国际化工作流示例 ===")
    
    # 调用完整工作流API
    result = await client.call("complete_i18n_workflow", {
        "source_directory": project_dir,
        "file_extensions": [".js", ".jsx", ".ts", ".tsx", ".vue", ".py"],
        "create_backup": True,
        "access_key_id": "YOUR_ALIYUN_ACCESS_KEY_ID",  # 替换为你的阿里云访问密钥ID
        "access_key_secret": "YOUR_ALIYUN_ACCESS_KEY_SECRET"  # 替换为你的阿里云访问密钥密码
    })
    
    print(f"工作流执行结果: {result}")
    return result

# 主函数
async def main():
    """主函数"""
    # 替换为你的项目目录
    project_dir = "/path/to/your/project"
    
    # 连接到服务器
    client = await connect_to_server()
    
    try:
        # 1. 提取中文
        chinese_dict = await extract_chinese_example(client, project_dir)
        
        # 2. 翻译中文
        translations = await translate_chinese_example(client, chinese_dict)
        
        # 3. 替换中文
        await replace_chinese_example(client, project_dir, translations)
        
        # 4. 完整工作流
        await complete_workflow_example(client, project_dir)
        
    finally:
        # 关闭连接
        await client.close()

# 运行主函数
if __name__ == "__main__":
    asyncio.run(main())