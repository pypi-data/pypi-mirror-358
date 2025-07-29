# TranslateMcpServer - 国际化工作流MCP服务器

一个用于项目国际化的MCP服务器，提供提取中文、翻译中文、替换文本功能，以及完整的国际化工作流。

## 功能特点

- **提取中文**：从项目文件中提取所有中文字符串
- **翻译中文**：使用阿里云翻译API将中文翻译为英文
- **替换文本**：将项目文件中的中文替换为翻译后的英文
- **完整工作流**：一键完成提取、翻译、替换的完整国际化流程

## 安装

### 从PyPI安装

```bash
pip install translate-mcp-server
```

或者使用pip3：

```bash
pip3 install translate-mcp-server
```

### 从源码安装

1. 克隆仓库

```bash
git clone https://github.com/yourusername/translate-mcp-server.git
cd translate-mcp-server
```

2. 安装依赖

```bash
pip install -r requirements.txt
```

或者直接安装依赖：

```bash
pip install mcp-server aliyun-python-sdk-core aliyun-python-sdk-alimt
```

3. 安装包

```bash
pip install -e .
```

## 使用方法

### 作为命令行工具使用

安装后，可以直接在命令行中启动服务器：

```bash
# 使用标准输入/输出模式启动
translate-mcp-server

# 使用HTTP模式启动
translate-mcp-server --transport http --host 127.0.0.1 --port 8000
```

### 作为Python包使用

```python
from translate_mcp_server.server import run_server

# 使用标准输入/输出模式启动
run_server(transport='stdio')

# 使用HTTP模式启动
run_server(transport='http', host='127.0.0.1', port=8000)
```

### 作为MCP服务器使用

启动服务器后，可以使用MCP客户端连接并调用服务：

```python
from mcp.client import MCPClient

async def main():
    # 连接到MCP服务器
    client = MCPClient("http://localhost:8000")
    await client.connect()
    
    # 调用服务
    result = await client.call("extract_chinese_text", {
        "directory": "/path/to/your/project",
        "file_extensions": [".js", ".jsx", ".ts", ".tsx", ".vue"]
    })
    
    print(result)

# 运行主函数
import asyncio
asyncio.run(main())
```

## 可用的MCP工具

### 1. extract_chinese_text

提取指定目录下所有文件中的中文字符串。

**参数**：
- `directory`：要搜索的目录路径
- `file_extensions`：要处理的文件扩展名列表，例如 `['.js', '.jsx', '.ts', '.tsx', '.vue']`。如果不指定，默认处理所有文本文件。

**返回**：包含所有中文字符串的字典，格式为 `{"中文": "中文"}`

**示例**：

```python
result = await client.call("extract_chinese_text", {
    "directory": "/path/to/your/project",
    "file_extensions": [".js", ".jsx", ".ts", ".tsx", ".vue"]
})
```

### 2. translate_chinese_to_english

将中文翻译为英文。

**参数**：
- `input_file`：包含中文文本的JSON文件路径，格式为 `{"中文": "中文"}`
- `text_dict`：直接提供的中文文本字典，如果提供则优先使用
- `batch_size`：每批处理的文本数量，默认为30，可以根据需要调整以控制翻译速度和进度更新频率
- `retry_count`：翻译失败时的重试次数
- `delay_seconds`：请求之间的延迟秒数
- `access_key_id`：阿里云访问密钥ID，如果不提供则尝试从环境变量获取
- `access_key_secret`：阿里云访问密钥密码，如果不提供则尝试从环境变量获取
- `endpoint`：阿里云翻译服务端点URL
- `api_version`：阿里云翻译API版本

**返回**：包含翻译结果的字典，格式为 `{"中文": "英文"}`

**示例**：

```python
result = await client.call("translate_chinese_to_english", {
    "input_file": "zh.json",
    "access_key_id": "YOUR_ALIYUN_ACCESS_KEY_ID",
    "access_key_secret": "YOUR_ALIYUN_ACCESS_KEY_SECRET"
})
```

### 3. replace_chinese_in_files

使用翻译结果替换文件中的中文。

**参数**：
- `directory`：要处理的目录路径
- `translations_file`：包含翻译结果的JSON文件路径，格式为 `{"中文": "英文"}`
- `file_extensions`：要处理的文件扩展名列表
- `create_backup`：是否创建备份文件

**返回**：处理结果统计

**示例**：

```python
result = await client.call("replace_chinese_in_files", {
    "directory": "/path/to/your/project",
    "translations_file": "translations.json",
    "file_extensions": [".js", ".jsx", ".ts", ".tsx", ".vue"],
    "create_backup": True
})
```

### 4. start_i18n_workflow

启动异步国际化工作流：提取中文、翻译中文、替换文本。

**参数**：
- `source_directory`：源代码目录
- `file_extensions`：要处理的文件扩展名列表
- `create_backup`：是否创建备份文件
- `access_key_id`：阿里云访问密钥ID，如果不提供则尝试从环境变量获取
- `access_key_secret`：阿里云访问密钥密码，如果不提供则尝试从环境变量获取
- `endpoint`：阿里云翻译服务端点URL
- `api_version`：阿里云翻译API版本
- `batch_size`：每批处理的文本数量，默认为30，较小的批量大小可以更频繁地更新进度
- `batch_size`：每批处理的文本数量，默认为30，较小的批量大小可以更频繁地更新进度

**返回**：任务ID和初始状态信息

**示例**：

```python
start_result = await client.call("start_i18n_workflow", {
    "source_directory": "/path/to/your/project",
    "file_extensions": [".js", ".jsx", ".ts", ".tsx", ".vue"],
    "create_backup": True,
    "access_key_id": "YOUR_ALIYUN_ACCESS_KEY_ID",
    "access_key_secret": "YOUR_ALIYUN_ACCESS_KEY_SECRET"
})

task_id = start_result["task_id"]
print(f"工作流已启动，任务ID: {task_id}")
```

### 5. get_i18n_workflow_status

获取国际化工作流的当前状态。

**参数**：
- `task_id`：工作流任务ID，由 start_i18n_workflow 返回

**返回**：工作流的当前状态信息

**示例**：

```python
status = await client.call("get_i18n_workflow_status", {
    "task_id": task_id
})

print(f"当前状态: {status['status']}")
print(f"当前步骤: {status.get('current_step', 'N/A')}")
print(f"进度: {status.get('progress', 0)}%")
print(f"消息: {status.get('message', 'N/A')}")
```

### 6. complete_i18n_workflow

完整的国际化工作流：提取中文、翻译中文、替换文本（同步版本，可能会超时）。

**注意**：此函数会同步执行整个工作流，可能会导致超时。建议使用 start_i18n_workflow 和 get_i18n_workflow_status 函数。

**参数**：
- `source_directory`：源代码目录
- `file_extensions`：要处理的文件扩展名列表
- `create_backup`：是否创建备份文件
- `access_key_id`：阿里云访问密钥ID，如果不提供则尝试从环境变量获取
- `access_key_secret`：阿里云访问密钥密码，如果不提供则尝试从环境变量获取
- `endpoint`：阿里云翻译服务端点URL
- `api_version`：阿里云翻译API版本

**返回**：处理结果统计

**示例**：

```python
result = await client.call("complete_i18n_workflow", {
    "source_directory": "/path/to/your/project",
    "file_extensions": [".js", ".jsx", ".ts", ".tsx", ".vue"],
    "create_backup": True,
    "access_key_id": "YOUR_ALIYUN_ACCESS_KEY_ID",
    "access_key_secret": "YOUR_ALIYUN_ACCESS_KEY_SECRET"
})
```

## 重要说明

### 关于异步API

对于大型项目，国际化工作流可能需要较长时间完成，建议使用异步API：

1. 使用 `start_i18n_workflow` 启动异步工作流，获取任务ID
2. 使用 `get_i18n_workflow_status` 定期查询工作流状态
3. 当状态为 `completed` 时，工作流完成

示例客户端代码可参考项目中的 `example_client.py`。

### 关于阿里云翻译SDK

本项目使用阿里云翻译SDK进行中文到英文的翻译。要使用翻译功能，您需要：

1. 拥有一个有效的阿里云账号
2. 创建访问密钥（AccessKey）
3. 确保您的账号有权限使用机器翻译服务

### 配置阿里云访问密钥

您可以通过以下方式配置阿里云访问密钥：

1. 在代码中直接提供：

```python
result = await client.call("translate_chinese_to_english", {
    "input_file": "zh.json",
    "access_key_id": "YOUR_ALIYUN_ACCESS_KEY_ID",
    "access_key_secret": "YOUR_ALIYUN_ACCESS_KEY_SECRET"
})
```

2. 通过环境变量提供：

```bash
export ALIYUN_ACCESS_KEY_ID="YOUR_ALIYUN_ACCESS_KEY_ID"
export ALIYUN_ACCESS_KEY_SECRET="YOUR_ALIYUN_ACCESS_KEY_SECRET"
```

然后在代码中不需要显式提供这些参数：

```python
result = await client.call("translate_chinese_to_english", {
    "input_file": "zh.json"
})
```

您可以在[阿里云AccessKey管理页面](https://ram.console.aliyun.com/manage/ak)创建和管理您的AccessKey。

## 发布到PyPI

如果您想将此包发布到PyPI，可以使用项目中提供的`publish.sh`脚本：

```bash
./publish.sh
```

脚本会引导您完成构建和发布过程。您可以选择发布到TestPyPI（测试环境）或正式的PyPI。

## 环境要求

- Python 3.7 或更高版本
- 依赖包：
  - mcp-server
  - aliyun-python-sdk-core
  - aliyun-python-sdk-alimt

## 许可证

本项目采用MIT许可证。详情请参阅[LICENSE](LICENSE)文件。
