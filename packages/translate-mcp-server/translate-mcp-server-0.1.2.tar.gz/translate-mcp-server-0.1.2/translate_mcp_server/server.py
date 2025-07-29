# mcpserver.py
import os
import re
import json
import time
import uuid
import math
import asyncio
from typing import Dict, List, Optional, Union, Any, Callable
from mcp.server.fastmcp import FastMCP

# 初始化FastMCP server，创建一个MCP服务器实例
# mcpserver为服务器名称，用于标识这个MCP服务
mcp = FastMCP("TranslateMcpServer")

# 存储正在进行的工作流状态
workflow_tasks = {}

# 清理过期任务的时间间隔（秒）
CLEANUP_INTERVAL = 3600  # 1小时

# 任务保留时间（秒）
TASK_RETENTION_PERIOD = 86400  # 24小时

# 清理过期任务
async def cleanup_expired_tasks():
    """定期清理过期的工作流任务"""
    while True:
        await asyncio.sleep(CLEANUP_INTERVAL)
        current_time = time.time()
        expired_tasks = []
        
        for task_id, task_info in workflow_tasks.items():
            # 检查任务是否已完成且超过保留期
            if task_info.get("end_time") and (current_time - task_info["end_time"] > TASK_RETENTION_PERIOD):
                expired_tasks.append(task_id)
        
        # 删除过期任务
        for task_id in expired_tasks:
            del workflow_tasks[task_id]
            print(f"已清理过期任务: {task_id}")

# 清理任务将在服务器启动时启动

# 阿里云翻译API配置默认值
DEFAULT_ALIYUN_ENDPOINT = "https://mt.cn-hangzhou.aliyuncs.com"
DEFAULT_ALIYUN_API_VERSION = "2018-10-12"


# 移除了全局变量ALIYUN_SDK_AVAILABLE

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
    batch_size: int = 20,  # 默认批量大小调整为20，避免超过API限制
    retry_count: int = 3,
    delay_seconds: int = 1,
    access_key_id: str = None,
    access_key_secret: str = None,
    endpoint: str = DEFAULT_ALIYUN_ENDPOINT,
    api_version: str = DEFAULT_ALIYUN_API_VERSION,
    progress_callback: Any = None
) -> Dict[str, str]:
    print(f"开始翻译中文到英文，输入文件: {input_file}, 批量大小: {batch_size}")
    print(f"访问密钥ID: {access_key_id[:4]}*** (隐藏部分)")
    """将中文翻译为英文
    
    Args:
        input_file: 包含中文文本的JSON文件路径，格式为 {"中文": "中文"}
        text_dict: 直接提供的中文文本字典，如果提供则优先使用
        batch_size: 每批处理的文本数量，默认为20（避免超过API限制）
        retry_count: 翻译失败时的重试次数
        delay_seconds: 请求之间的延迟秒数
        access_key_id: 阿里云访问密钥ID，如果不提供则尝试从环境变量获取
        access_key_secret: 阿里云访问密钥密码，如果不提供则尝试从环境变量获取
        endpoint: 阿里云翻译服务端点URL
        api_version: 阿里云翻译API版本
        progress_callback: 进度回调函数，接收三个参数：当前进度百分比、总文本数量和进度消息
    
    Returns:
        包含翻译结果的字典，格式为 {"中文": "英文"}
    """
    # 尝试导入阿里云SDK
    try:
        from aliyunsdkcore.client import AcsClient
        from aliyunsdkcore.acs_exception.exceptions import ClientException, ServerException
        from aliyunsdkalimt.request.v20181012.TranslateRequest import TranslateRequest
        from aliyunsdkalimt.request.v20181012.GetBatchTranslateRequest import GetBatchTranslateRequest
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
    total_items = len(text_items)
    print(f"总共需要翻译 {total_items} 条文本，批量大小: {batch_size}")
    
    # 如果文本数量过多，给出警告
    if total_items > 500:
        print(f"警告: 文本数量较多 ({total_items} 条)，可能需要较长时间处理，建议减小批量大小或分批处理")
    elif total_items > 100:
        print(f"提示: 文本数量较大 ({total_items} 条)，处理可能需要一些时间")
        
    # 记录批量处理信息
    print(f"将使用 {math.ceil(total_items / batch_size)} 个批次进行处理，每批次最多 {batch_size} 条文本")
    
    # 如果批量大小大于30，给出警告
    if batch_size > 30:
        print(f"警告: 批量大小 ({batch_size}) 可能超过API限制，建议设置为30或更小")
    
    for i in range(0, total_items, batch_size):
        batch = text_items[i:i+batch_size]
        current_position = i + 1
        end_position = min(i + batch_size, total_items)
        progress_message = {"status": "processing", "current": current_position, "end": end_position, "total": total_items}
        print(f"正在处理第 {current_position} 到 {end_position} 条，共 {total_items} 条...")
        
        # 如果提供了进度回调函数，则调用它更新进度
        if progress_callback:
            # 计算当前进度百分比（10-90之间，因为整个工作流中翻译是第二步）
            progress_percent = 10 + int((i / total_items) * 80)
            progress_callback(progress_percent, total_items, json.dumps(progress_message))
        
        # 过滤掉不需要翻译的文本（非中文或空文本）
        batch_to_translate = {}
        for key, value in batch:
            if not value or not re.search(r'[\u4e00-\u9fa5]', value):
                results[key] = value
            else:
                batch_to_translate[key] = value
        
        # 如果没有需要翻译的文本，跳过此批次
        if not batch_to_translate:
            continue
        
        # 重试机制
        for attempt in range(retry_count):
            try:
                # 准备批量翻译的JSON格式
                source_text_json = json.dumps(batch_to_translate)
                
                # 创建批量翻译请求
                request = GetBatchTranslateRequest()
                request.set_accept_format('json')
                request.set_FormatType("text")
                request.set_SourceLanguage("zh")
                request.set_TargetLanguage("en")
                request.set_SourceText(source_text_json)
                request.set_Scene("general")
                request.set_ApiType("translate_standard")
                
                # 设置API版本
                if api_version:
                    request.set_version(api_version)
                
                # 发送批量翻译请求
                print(f"发送批量翻译请求，批次大小: {len(batch_to_translate)}")
                try:
                    # 记录请求详情以便调试
                    print(f"请求详情: API版本={api_version}, 源语言=zh, 目标语言=en, 场景=general")
                    response = client.do_action_with_exception(request)
                    # 记录原始响应以便调试
                    print(f"原始响应: {response}")
                    try:
                        response_dict = json.loads(response)
                        print(f"翻译响应: {response_dict}")
                    except json.JSONDecodeError as je:
                        print(f"解析响应JSON失败: {str(je)}，原始响应: {response}")
                        raise
                except Exception as e:
                    print(f"发送批量翻译请求失败: {str(e)}")
                    # 记录更多调试信息
                    print(f"请求参数: {request.get_params()}")
                    print(f"请求头: {request.get_headers()}")
                    raise
                
                # 处理批量翻译结果
                if response_dict and str(response_dict.get('Code')) == '200':
                    # 检查TranslatedList是否存在且不为None
                    if 'TranslatedList' in response_dict and response_dict['TranslatedList'] is not None:
                        translated_list = response_dict['TranslatedList']
                        print(f"TranslatedList类型: {type(translated_list)}, 内容: {translated_list}")
                        
                        # 确保translated_list是一个列表
                        if not isinstance(translated_list, list):
                            print(f"警告: TranslatedList不是列表类型，而是{type(translated_list)}")
                            if isinstance(translated_list, dict):
                                # 尝试从字典中提取翻译结果
                                print(f"尝试从字典中提取翻译结果: {translated_list}")
                                try:
                                    if 'index' in translated_list and 'translated' in translated_list:
                                        key = translated_list['index']
                                        results[key] = translated_list['translated']
                                        print(f"从字典中成功提取一条翻译结果")
                                        break
                                except Exception as e:
                                    print(f"从字典中提取翻译结果失败: {str(e)}")
                            # 如果不是列表也不是可处理的字典，则重试
                            continue
                        
                        # 正常处理列表
                        success_count = 0
                        for item in translated_list:
                            try:
                                if isinstance(item, dict) and 'index' in item and 'translated' in item:
                                    key = item['index']
                                    results[key] = item['translated']
                                    success_count += 1
                                else:
                                    print(f"警告: 翻译项不是字典或缺少index/translated字段: {item}")
                            except Exception as e:
                                print(f"处理翻译项时出错: {str(e)}, 项: {item}")
                        
                        print(f"批量翻译成功: 处理了{len(translated_list)}条文本，成功{success_count}条")
                        break
                    else:
                        # TranslatedList缺失或为None的情况
                        error_message = {"status": "error", "attempt": attempt+1, "message": "翻译响应中缺少TranslatedList或为None"}
                        print(f"批量翻译失败 (第{attempt+1}次尝试): 响应中缺少TranslatedList或为None，响应内容: {response_dict}")
                        # 如果是最后一次尝试，保留原值
                        if attempt == retry_count - 1:
                            print(f"批量翻译失败: 已达到最大重试次数，保留原值")
                            for key, value in batch_to_translate.items():
                                results[key] = value
                        else:
                            # 等待后重试
                            await asyncio.sleep(delay_seconds * (attempt + 1))
                else:
                    error_message = {"status": "error", "attempt": attempt+1, "message": str(response_dict)}
                    print(f"批量翻译失败 (第{attempt+1}次尝试): {response_dict}")
            except Exception as e:
                error_message = {"status": "error", "attempt": attempt+1, "message": str(e)}
                print(f"批量翻译失败 (第{attempt+1}次尝试): {str(e)}")
                if attempt == retry_count - 1:
                    print(f"批量翻译失败: 已达到最大重试次数，保留原值")
                    # 保留原值
                    for key, value in batch_to_translate.items():
                        results[key] = value
                else:
                    # 等待后重试
                    await asyncio.sleep(delay_seconds * (attempt + 1))
        
        # 批次间隔
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

async def _complete_i18n_workflow(
    task_id: str,
    source_directory: str,
    file_extensions: Optional[List[str]] = None,
    create_backup: bool = True,
    access_key_id: str = None,
    access_key_secret: str = None,
    endpoint: str = DEFAULT_ALIYUN_ENDPOINT,
    api_version: str = DEFAULT_ALIYUN_API_VERSION,
    batch_size: int = 20  # 默认批量大小调整为20，避免超过API限制
) -> Dict[str, Any]:
    """内部函数：执行完整的国际化工作流并更新状态"""
    
    if file_extensions is None:
        file_extensions = ['.js', '.jsx', '.ts', '.tsx', '.vue', '.py', '.html', '.css']
    
    start_time = time.time()
    results = {}
    
    try:
        # 更新任务状态
        workflow_tasks[task_id].update({
            "status": "running",
            "current_step": "extracting",
            "progress": 10,
            "message": "正在提取中文文本..."
        })
        
        # 步骤1: 提取中文
        print(f"[任务 {task_id}] 步骤1: 提取中文...")
        chinese_texts = await extract_chinese_text(source_directory, file_extensions)
        if "error" in chinese_texts:
            workflow_tasks[task_id].update({
                "status": "failed",
                "error": chinese_texts["error"],
                "end_time": time.time()
            })
            return workflow_tasks[task_id]
        
        results["extracted_count"] = len(chinese_texts)
        
        # 保存中文到临时文件
        temp_zh_file = os.path.join(os.path.dirname(source_directory), f"zh_temp_{task_id}.json")
        with open(temp_zh_file, 'w', encoding='utf-8') as f:
            json.dump(chinese_texts, f, ensure_ascii=False, indent=2)
        
        # 更新任务状态
        workflow_tasks[task_id].update({
            "current_step": "translating",
            "progress": 10,
            "message": "正在翻译中文文本...",
            "extracted_count": len(chinese_texts)
        })
        
        # 步骤2: 翻译中文
        print(f"[任务 {task_id}] 步骤2: 翻译中文...")
        
        # 定义进度回调函数
        def update_translation_progress(progress, total, message):
            # 尝试解析JSON消息
            try:
                message_obj = json.loads(message) if isinstance(message, str) else message
                workflow_tasks[task_id].update({
                    "progress": progress,
                    "message": json.dumps(message_obj),  # 确保消息是有效的JSON字符串
                    "total_texts": total,
                    "status_details": message_obj  # 保存详细状态信息
                })
            except (json.JSONDecodeError, TypeError):
                # 如果消息不是有效的JSON，则直接使用原始消息
                workflow_tasks[task_id].update({
                    "progress": progress,
                    "message": str(message),  # 确保消息是字符串
                    "total_texts": total
                })
        
        try:
            translations = await translate_chinese_to_english(
                temp_zh_file,
                batch_size=batch_size,  # 使用传入的批量大小参数
                access_key_id=access_key_id,
                access_key_secret=access_key_secret,
                endpoint=endpoint,
                api_version=api_version,
                progress_callback=update_translation_progress
            )
            if "error" in translations:
                workflow_tasks[task_id].update({
                    "status": "failed",
                    "error": translations["error"],
                    "end_time": time.time()
                })
                return workflow_tasks[task_id]
            
            # 检查翻译结果是否为空或无效
            if not translations or len(translations) == 0:
                error_message = "翻译结果为空或无效"
                workflow_tasks[task_id].update({
                    "status": "failed",
                    "error": error_message,
                    "end_time": time.time()
                })
                return workflow_tasks[task_id]
        except Exception as e:
            error_message = f"翻译过程中发生错误: {str(e)}"
            workflow_tasks[task_id].update({
                "status": "failed",
                "error": error_message,
                "end_time": time.time()
            })
            return workflow_tasks[task_id]
        
        results["translated_count"] = len(translations)
        
        # 保存翻译结果
        translations_file = os.path.join(os.path.dirname(source_directory), f"translations_{task_id}.json")
        with open(translations_file, 'w', encoding='utf-8') as f:
            json.dump(translations, f, ensure_ascii=False, indent=2)
        
        # 更新任务状态
        workflow_tasks[task_id].update({
            "current_step": "replacing",
            "progress": 90,
            "message": "正在替换文件中的中文文本...",
            "translated_count": len(translations)
        })
        
        # 步骤3: 替换文本
        print(f"[任务 {task_id}] 步骤3: 替换文本...")
        replace_results = await replace_chinese_in_files(
            source_directory, 
            translations_file,
            file_extensions,
            create_backup
        )
        if "error" in replace_results:
            workflow_tasks[task_id].update({
                "status": "failed",
                "error": replace_results["error"],
                "end_time": time.time()
            })
            return workflow_tasks[task_id]
        
        # 合并结果
        results.update(replace_results)
        execution_time = time.time() - start_time
        results["execution_time"] = f"{execution_time:.2f}秒"
        
        # 清理临时文件
        if os.path.exists(temp_zh_file):
            os.remove(temp_zh_file)
        
        # 更新最终状态
        workflow_tasks[task_id].update({
            "status": "completed",
            "progress": 100,
            "message": "国际化工作流已完成",
            "results": results,
            "end_time": time.time(),
            "execution_time": execution_time
        })
        
        return workflow_tasks[task_id]
    except Exception as e:
        # 捕获所有异常，确保任务状态被正确更新
        error_message = f"执行工作流时发生错误: {str(e)}"
        print(f"[任务 {task_id}] {error_message}")
        
        workflow_tasks[task_id].update({
            "status": "failed",
            "error": error_message,
            "end_time": time.time()
        })
        
        return workflow_tasks[task_id]

@mcp.tool()
async def start_i18n_workflow(
    source_directory: str,
    file_extensions: Optional[List[str]] = None,
    create_backup: bool = True,
    access_key_id: str = None,
    access_key_secret: str = None,
    endpoint: str = DEFAULT_ALIYUN_ENDPOINT,
    api_version: str = DEFAULT_ALIYUN_API_VERSION,
    batch_size: int = 20  # 默认批量大小调整为20，避免超过API限制
) -> Dict[str, Any]:
    """启动异步国际化工作流：提取中文、翻译中文、替换文本
    
    Args:
        source_directory: 源代码目录
        file_extensions: 要处理的文件扩展名列表
        create_backup: 是否创建备份文件
        access_key_id: 阿里云访问密钥ID，如果不提供则尝试从环境变量获取
        access_key_secret: 阿里云访问密钥密码，如果不提供则尝试从环境变量获取
        endpoint: 阿里云翻译服务端点URL
        api_version: 阿里云翻译API版本
        batch_size: 每批处理的文本数量，默认为30
    
    Returns:
        任务ID和初始状态信息
    """
    
    # 生成唯一任务ID
    task_id = str(uuid.uuid4())
    
    # 初始化任务状态
    workflow_tasks[task_id] = {
        "task_id": task_id,
        "status": "pending",
        "current_step": "initializing",
        "progress": 0,
        "message": "正在初始化国际化工作流...",
        "source_directory": source_directory,
        "start_time": time.time(),
        "end_time": None,
        "results": None,
        "error": None
    }
    
    # 异步启动工作流，不等待完成
    asyncio.create_task(_complete_i18n_workflow(
        task_id,
        source_directory,
        file_extensions,
        create_backup,
        access_key_id,
        access_key_secret,
        endpoint,
        api_version,
        batch_size
    ))
    
    # 返回任务ID和初始状态
    return {
        "task_id": task_id,
        "status": "started",
        "message": "国际化工作流已启动，可以使用 get_i18n_workflow_status 查询进度"
    }

@mcp.tool()
async def get_i18n_workflow_status(task_id: str) -> Dict[str, Any]:
    """获取国际化工作流的当前状态
    
    Args:
        task_id: 工作流任务ID，由 start_i18n_workflow 返回
    
    Returns:
        工作流的当前状态信息
    """
    
    if task_id not in workflow_tasks:
        return {
            "status": "not_found",
            "error": f"找不到任务ID: {task_id}"
        }
    
    return workflow_tasks[task_id]

@mcp.tool()
async def complete_i18n_workflow(
    source_directory: str,
    file_extensions: Optional[List[str]] = None,
    create_backup: bool = True,
    access_key_id: str = None,
    access_key_secret: str = None,
    endpoint: str = DEFAULT_ALIYUN_ENDPOINT,
    api_version: str = DEFAULT_ALIYUN_API_VERSION,
    batch_size: int = 30
) -> Dict[str, Union[str, int, Dict]]:
    """完整的国际化工作流：提取中文、翻译中文、替换文本（同步版本，可能会超时）
    
    注意：此函数会同步执行整个工作流，可能会导致超时。建议使用 start_i18n_workflow 和 get_i18n_workflow_status 函数。
    
    Args:
        source_directory: 源代码目录
        file_extensions: 要处理的文件扩展名列表
        create_backup: 是否创建备份文件
        access_key_id: 阿里云访问密钥ID，如果不提供则尝试从环境变量获取
        access_key_secret: 阿里云访问密钥密码，如果不提供则尝试从环境变量获取
        endpoint: 阿里云翻译服务端点URL
        api_version: 阿里云翻译API版本
        batch_size: 每批处理的文本数量，默认为30
    
    Returns:
        处理结果统计
    """
    
    # 启动异步工作流
    start_result = await start_i18n_workflow(
        source_directory,
        file_extensions,
        create_backup,
        access_key_id,
        access_key_secret,
        endpoint,
        api_version,
        batch_size
    )
    
    task_id = start_result["task_id"]
    
    # 等待工作流完成
    while True:
        status = await get_i18n_workflow_status(task_id)
        if status["status"] in ["completed", "failed"]:
            break
        await asyncio.sleep(1)  # 每秒检查一次状态
    
    # 返回最终结果
    if status["status"] == "failed":
        return {"error": status["error"]}
    
    return status["results"]

# 启动MCP服务器
if __name__ == "__main__":
    # 启动清理任务
    # 注意：直接在主线程中启动清理任务
    loop = asyncio.get_event_loop()
    loop.create_task(cleanup_expired_tasks())
    print("已启动任务清理服务")
    
    # 初始化并运行服务
    mcp.run(transport='stdio')