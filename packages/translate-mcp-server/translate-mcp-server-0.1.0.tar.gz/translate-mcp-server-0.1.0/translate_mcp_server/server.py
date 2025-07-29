# server.py
import os
import re
import json
import time
import asyncio
from typing import Dict, List, Optional, Union
from mcp.server.fastmcp import FastMCP

# 初始化FastMCP server，创建一个MCP服务器实例
# mcpserver为服务器名称，用于标识这个MCP服务
mcp = FastMCP("TranslateMcpServer")

# 阿里云翻译API配置默认值
DEFAULT_ALIYUN_ENDPOINT = "https://mt.cn-hangzhou.aliyuncs.com"
DEFAULT_ALIYUN_API_VERSION = "2018-10-12"


@mcp.tool()
async def extract_chinese_text(directory: str, file_extensions: Optional[List[str]] = None) -> Dict[str, str]:
    """提取指定目录下所有文件中的中文字符串
    
    Args:
        directory: 要搜索的目录路径
        file_extensions: 要处理的文件扩展名列表，例如 ['.js', '.jsx', '.ts', '.tsx', '.vue']
                        如果不指定，默认处理所有文本文件
    
    Returns:
        包含所有中文字符串的字典，格式为 {"中文": "中文"}
    """
    if file_extensions is None:
        file_extensions = ['.js', '.jsx', '.ts', '.tsx', '.vue', '.py', '.html', '.css']
    
    all_chinese = {}
    
    # 检查目录是否存在
    if not os.path.exists(directory):
        return {"error": f"目录不存在: {directory}"}
    
    # 递归遍历目录
    for root, _, files in os.walk(directory):
        for file in files:
            # 检查文件扩展名
            if not any(file.endswith(ext) for ext in file_extensions):
                continue
                
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 匹配所有中文字符串
                    chinese_matches = re.findall(r'[\u4e00-\u9fa5]+', content)
                    for match in chinese_matches:
                        # 使用中文作为key
                        all_chinese[match] = match
            except Exception as e:
                print(f"读取文件出错 {file_path}: {e}")
    
    # 将结果写入JSON文件
    output_path = os.path.join(os.path.dirname(directory), "zh.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_chinese, f, ensure_ascii=False, indent=2)
    
    return all_chinese

@mcp.tool()
async def translate_chinese_to_english(
    input_file: str = None, 
    text_dict: Optional[Dict[str, str]] = None,
    batch_size: int = 40,
    retry_count: int = 3,
    delay_seconds: int = 1,
    access_key_id: str = None,
    access_key_secret: str = None,
    endpoint: str = DEFAULT_ALIYUN_ENDPOINT,
    api_version: str = DEFAULT_ALIYUN_API_VERSION
) -> Dict[str, str]:
    """将中文翻译为英文
    
    Args:
        input_file: 包含中文文本的JSON文件路径，格式为 {"中文": "中文"}
        text_dict: 直接提供的中文文本字典，如果提供则优先使用
        batch_size: 每批处理的文本数量
        retry_count: 翻译失败时的重试次数
        delay_seconds: 请求之间的延迟秒数
        access_key_id: 阿里云访问密钥ID，如果不提供则尝试从环境变量获取
        access_key_secret: 阿里云访问密钥密码，如果不提供则尝试从环境变量获取
        endpoint: 阿里云翻译服务端点URL
        api_version: 阿里云翻译API版本
    
    Returns:
        包含翻译结果的字典，格式为 {"中文": "英文"}
    """
    # 尝试导入阿里云SDK
    try:
        from aliyunsdkcore.client import AcsClient
        from aliyunsdkcore.acs_exception.exceptions import ClientException, ServerException
        from aliyunsdkalimt.request.v20181012.TranslateRequest import TranslateRequest
        aliyun_sdk_available = True
    except ImportError as e:
        # 记录具体的导入错误信息
        error_msg = f"阿里云翻译SDK导入失败: {str(e)}\n"
        error_msg += "请安装相关依赖: pip install aliyun-python-sdk-core aliyun-python-sdk-alimt"
        return {"error": error_msg}
    except Exception as e:
        # 捕获其他可能的异常
        return {"error": f"导入阿里云SDK时发生未知错误: {str(e)}"}
    
    # 获取要翻译的文本
    texts_to_translate = {}
    if text_dict is not None:
        texts_to_translate = text_dict
    elif input_file and os.path.exists(input_file):
        with open(input_file, 'r', encoding='utf-8') as f:
            texts_to_translate = json.load(f)
    else:
        return {"error": "未提供有效的输入文件或文本字典"}
    
    # 检查访问密钥是否设置
    # 如果未提供参数，尝试从环境变量获取
    if access_key_id is None:
        access_key_id = os.environ.get('ALIYUN_ACCESS_KEY_ID')
    if access_key_secret is None:
        access_key_secret = os.environ.get('ALIYUN_ACCESS_KEY_SECRET')
    
    if not access_key_id or not access_key_secret:
        return {"error": "阿里云访问密钥未设置，请通过参数提供或设置环境变量 ALIYUN_ACCESS_KEY_ID 和 ALIYUN_ACCESS_KEY_SECRET"}
    
    # 创建翻译客户端
    try:
        # 从endpoint中提取区域ID
        region_id = 'cn-hangzhou'  # 默认区域
        if endpoint:
            # 尝试从endpoint中提取区域，格式通常为 https://mt.cn-hangzhou.aliyuncs.com
            endpoint_parts = endpoint.split('.')
            if len(endpoint_parts) > 1:
                region_part = endpoint_parts[1]
                if region_part.startswith('cn-') or region_part.startswith('ap-'):
                    region_id = region_part
        
        client = AcsClient(
            access_key_id,
            access_key_secret,
            region_id
        )
    except Exception as e:
        return {"error": f"无法创建阿里云翻译客户端: {str(e)}"}
    
    # 翻译结果
    results = {}
    text_items = list(texts_to_translate.items())
    
    # 批量处理翻译
    for i in range(0, len(text_items), batch_size):
        batch = text_items[i:i+batch_size]
        print(f"正在处理第 {i + 1} 到 {min(i + batch_size, len(text_items))} 条...")
        
        for key, value in batch:
            if not value or not re.search(r'[\u4e00-\u9fa5]', value):
                results[key] = value
                continue
            
            # 重试机制
            for attempt in range(retry_count):
                try:
                    # 创建请求
                    request = TranslateRequest()
                    request.set_accept_format('json')
                    request.set_FormatType("text")
                    request.set_SourceLanguage("zh")
                    request.set_TargetLanguage("en")
                    request.set_SourceText(value)
                    request.set_Scene("general")
                    
                    # 设置API版本
                    if api_version:
                        request.set_version(api_version)
                    
                    # 发送请求
                    response = client.do_action_with_exception(request)
                    response_dict = json.loads(response)
                    
                    if response_dict and 'Data' in response_dict and 'Translated' in response_dict['Data']:
                        results[key] = response_dict['Data']['Translated']
                        print(f"翻译成功: {key}")
                        break
                except Exception as e:
                    print(f"翻译失败 {key} (第{attempt+1}次尝试): {str(e)}")
                    if attempt == retry_count - 1:
                        print(f"翻译失败 {key}: 已达到最大重试次数")
                        results[key] = value  # 保留原值
                    else:
                        # 等待后重试
                        await asyncio.sleep(delay_seconds * (attempt + 1))
            
            # 请求间隔
            await asyncio.sleep(delay_seconds)
    
    # 保存翻译结果
    if input_file:
        output_file = os.path.splitext(input_file)[0] + "_translated.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
    
    return results

@mcp.tool()
async def replace_chinese_in_files(
    directory: str, 
    translations_file: str,
    file_extensions: Optional[List[str]] = None,
    create_backup: bool = True
) -> Dict[str, Union[int, List[str]]]:
    """使用翻译结果替换文件中的中文
    
    Args:
        directory: 要处理的目录路径
        translations_file: 包含翻译结果的JSON文件路径，格式为 {"中文": "英文"}
        file_extensions: 要处理的文件扩展名列表
        create_backup: 是否创建备份文件
    
    Returns:
        处理结果统计
    """
    if file_extensions is None:
        file_extensions = ['.js', '.jsx', '.ts', '.tsx', '.vue', '.py', '.html', '.css']
    
    # 检查目录和翻译文件是否存在
    if not os.path.exists(directory):
        return {"error": f"目录不存在: {directory}"}
    
    if not os.path.exists(translations_file):
        return {"error": f"翻译文件不存在: {translations_file}"}
    
    # 加载翻译结果
    with open(translations_file, 'r', encoding='utf-8') as f:
        translations = json.load(f)
    
    # 获取所有需要处理的文件
    files_to_process = []
    for root, _, files in os.walk(directory):
        for file in files:
            if any(file.endswith(ext) for ext in file_extensions):
                files_to_process.append(os.path.join(root, file))
    
    # 处理每个文件
    modified_files = []
    for file_path in files_to_process:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 创建备份
            if create_backup:
                backup_path = file_path + ".bak"
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            # 替换中文（先替换文本长的）
            modified_content = content
            
            # 按中文文本长度降序排序，确保先替换较长的文本
            sorted_translations = sorted(translations.items(), key=lambda x: len(x[0]), reverse=True)
            
            for chinese, english in sorted_translations:
                if chinese in modified_content:
                    modified_content = modified_content.replace(chinese, english)
            
            # 如果内容有变化，写入文件
            if modified_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
                modified_files.append(file_path)
        except Exception as e:
            print(f"处理文件出错 {file_path}: {e}")
    
    return {
        "total_files": len(files_to_process),
        "modified_files": len(modified_files),
        "modified_file_paths": modified_files
    }

@mcp.tool()
async def complete_i18n_workflow(
    source_directory: str,
    file_extensions: Optional[List[str]] = None,
    create_backup: bool = True,
    access_key_id: str = None,
    access_key_secret: str = None,
    endpoint: str = DEFAULT_ALIYUN_ENDPOINT,
    api_version: str = DEFAULT_ALIYUN_API_VERSION
) -> Dict[str, Union[str, int, Dict]]:
    """完整的国际化工作流：提取中文、翻译中文、替换文本
    
    Args:
        source_directory: 源代码目录
        file_extensions: 要处理的文件扩展名列表
        create_backup: 是否创建备份文件
        access_key_id: 阿里云访问密钥ID，如果不提供则尝试从环境变量获取
        access_key_secret: 阿里云访问密钥密码，如果不提供则尝试从环境变量获取
        endpoint: 阿里云翻译服务端点URL
        api_version: 阿里云翻译API版本
    
    Returns:
        处理结果统计
    """
    
    if file_extensions is None:
        file_extensions = ['.js', '.jsx', '.ts', '.tsx', '.vue', '.py', '.html', '.css']
    
    start_time = time.time()
    results = {}
    
    # 步骤1: 提取中文
    print("步骤1: 提取中文...")
    chinese_texts = await extract_chinese_text(source_directory, file_extensions)
    if "error" in chinese_texts:
        return {"error": chinese_texts["error"]}
    
    results["extracted_count"] = len(chinese_texts)
    
    # 保存中文到临时文件
    temp_zh_file = os.path.join(os.path.dirname(source_directory), "zh_temp.json")
    with open(temp_zh_file, 'w', encoding='utf-8') as f:
        json.dump(chinese_texts, f, ensure_ascii=False, indent=2)
    
    # 步骤2: 翻译中文
    print("步骤2: 翻译中文...")
    translations = await translate_chinese_to_english(
        temp_zh_file,
        access_key_id=access_key_id,
        access_key_secret=access_key_secret,
        endpoint=endpoint,
        api_version=api_version
    )
    if "error" in translations:
        return {"error": translations["error"]}
    
    results["translated_count"] = len(translations)
    
    # 保存翻译结果
    translations_file = os.path.join(os.path.dirname(source_directory), "translations.json")
    with open(translations_file, 'w', encoding='utf-8') as f:
        json.dump(translations, f, ensure_ascii=False, indent=2)
    
    # 步骤3: 替换文本
    print("步骤3: 替换文本...")
    replace_results = await replace_chinese_in_files(
        source_directory, 
        translations_file,
        file_extensions,
        create_backup
    )
    if "error" in replace_results:
        return {"error": replace_results["error"]}
    
    # 合并结果
    results.update(replace_results)
    results["execution_time"] = f"{time.time() - start_time:.2f}秒"
    
    # 清理临时文件
    if os.path.exists(temp_zh_file):
        os.remove(temp_zh_file)
    
    return results

# 启动MCP服务器函数
def run_server(transport='stdio', host='127.0.0.1', port=8000):
    """启动MCP服务器
    
    Args:
        transport: 传输方式，可选 'stdio' 或 'http'
        host: HTTP服务器主机地址，仅当 transport=http 时有效
        port: HTTP服务器端口，仅当 transport=http 时有效
    """
    if transport == 'http':
        mcp.run(transport=transport, host=host, port=port)
    else:
        mcp.run(transport=transport)

# 如果直接运行此文件
if __name__ == "__main__":
    # 初始化并运行服务
    run_server(transport='stdio')