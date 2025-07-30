# MCP Web Search Server

一个无需API key的网页搜索MCP（Model Context Protocol）服务器，支持DuckDuckGo和必应搜索引擎提供网页搜索功能。

## 功能特性

- 🔍 **多引擎搜索**: 支持DuckDuckGo和必应搜索引擎，无需API key
- 📄 **网页内容获取**: 获取指定网页的文本内容
- 🚀 **异步处理**: 基于asyncio的高性能异步处理
- 🛡️ **安全可靠**: 不需要任何外部API密钥，保护隐私
- 🌐 **多种搜索方式**: 支持API和HTML两种搜索方式
- ⚡ **灵活选择**: 可选择单一搜索引擎或组合使用

## 安装方式

### 方式一：通过 PyPI 安装（推荐）

```bash
# 从 PyPI 安装
pip install heventure-search-mcp

# 然后运行
heventure-search-mcp
```

### 方式二：通过 uvx 安装

```bash
# 从 PyPI 运行
uvx heventure-search-mcp

# 或者从 GitHub 运行
uvx --from git+https://github.com/HughesCuit/heventure-search-mcp.git server.py
```

### 方式三：通过 pip 从源码安装

```bash
# 直接从 GitHub 安装
pip install git+https://github.com/HughesCuit/heventure-search-mcp.git

# 然后运行（三种方式任选其一）
heventure-search-mcp                    # 使用命令行工具
python -m server                        # 直接运行模块
python -c "import server; import asyncio; asyncio.run(server.main())"  # 编程方式
```

### 方式四：手动安装依赖

```bash
# 克隆仓库
git clone https://github.com/HughesCuit/heventure-search-mcp.git
cd heventure-search-mcp

# 安装依赖
pip install -r requirements.txt
```

## 使用方法

### 直接运行服务器

```bash
python server.py
```

### 作为MCP服务器使用

在你的MCP客户端配置中添加此服务器：

```json
{
  "mcpServers": {
    "web-search": {
      "command": "python",
      "args": ["/path/to/server.py"]
    }
  }
}
```

### 在Trae AI中使用

在Trae AI中添加此MCP服务器，请使用以下配置：

```json
{
  "mcpServers": {
    "heventure-search-mcp": {
      "command": "uvx",
      "args": [
        "-y",
        "heventure-search-mcp"
      ]
    }
  }
}
```

或者如果你已经本地安装了包：

```json
{
  "mcpServers": {
    "heventure-search-mcp": {
      "command": "python",
      "args": [
        "-m",
        "heventure_search_mcp"
      ]
    }
  }
}
```

## 可用工具

### 1. web_search

搜索网页内容，支持多种搜索引擎

**参数:**
- `query` (string, 必需): 搜索查询词
- `max_results` (integer, 可选): 最大结果数量 (默认: 10, 范围: 1-20)
- `search_engine` (string, 可选): 搜索引擎选择 (默认: "both")
  - `"duckduckgo"`: 仅使用DuckDuckGo搜索
  - `"bing"`: 仅使用必应搜索
  - `"both"`: 同时使用两个搜索引擎

**示例:**
```json
{
  "query": "Python编程教程",
  "max_results": 5,
  "search_engine": "both"
}
```

**使用不同搜索引擎:**
```json
// 仅使用DuckDuckGo
{
  "query": "机器学习算法",
  "search_engine": "duckduckgo"
}

// 仅使用必应
{
  "query": "人工智能发展",
  "search_engine": "bing"
}
```

### 2. get_webpage_content

获取指定网页的文本内容

**参数:**
- `url` (string, 必需): 要获取内容的网页URL

**示例:**
```json
{
  "url": "https://example.com"
}
```

## 技术实现

### 搜索引擎

本服务支持多个搜索引擎，提供更全面的搜索结果：

#### DuckDuckGo
1. **无需API key**: 提供免费的搜索API
2. **隐私保护**: 不跟踪用户搜索历史
3. **即时答案**: 支持即时答案和相关主题
4. **多种接口**: 支持API和HTML两种访问方式

#### 必应搜索
1. **丰富结果**: 提供详细的搜索结果和摘要
2. **高质量**: 微软搜索引擎的高质量结果
3. **HTML解析**: 通过HTML页面解析获取结果
4. **补充搜索**: 与DuckDuckGo形成良好互补

### 搜索策略

1. **DuckDuckGo策略**: 优先使用API，不足时使用HTML解析
2. **必应策略**: 通过HTML页面解析获取搜索结果
3. **组合策略**: 当选择"both"时，合并两个引擎的结果
4. **结果优化**: 自动去重、排序和格式化结果

### 内容提取

- 使用BeautifulSoup解析HTML内容
- 自动移除脚本和样式标签
- 清理和格式化文本内容
- 限制内容长度避免过长响应

## 项目结构

```
mcp_dev/
├── server.py          # 主服务器文件
├── requirements.txt   # 项目依赖
├── README.md         # 项目说明
└── config.json       # MCP配置示例
```

## 配置说明

### 用户代理

服务器使用标准的浏览器用户代理字符串来避免被网站阻止：

```python
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
```

### 超时设置

- 网页内容获取超时: 10秒
- 搜索请求超时: 默认aiohttp超时

### 内容限制

- 网页内容最大长度: 2000字符
- 最大搜索结果数: 20个

## 错误处理

服务器包含完善的错误处理机制：

- 网络请求失败自动重试
- 解析错误优雅降级
- 详细的错误日志记录
- 用户友好的错误消息

## 注意事项

1. **网络依赖**: 需要稳定的网络连接
2. **速率限制**: 请合理使用，避免过于频繁的请求
3. **内容准确性**: 搜索结果来自第三方，请自行验证内容准确性
4. **法律合规**: 请遵守相关法律法规和网站使用条款

## 开发和发布

### 本地开发

```bash
# 克隆仓库
git clone https://github.com/HughesCuit/heventure-search-mcp.git
cd heventure-search-mcp

# 安装开发依赖
pip install -e .
pip install build twine

# 运行测试
python test_server.py

# 运行基准测试
python benchmark.py
```

### 发布到PyPI

项目包含自动化发布脚本：

```bash
# 发布到TestPyPI（测试）
python publish.py test

# 发布到正式PyPI
python publish.py prod

# 仅构建包
python publish.py build

# 清理构建文件
python publish.py clean
```

**发布前准备：**

1. 配置PyPI API Token：
   ```bash
   # 在 ~/.pypirc 中配置
   [pypi]
   username = __token__
   password = your-api-token
   
   [testpypi]
   username = __token__
   password = your-test-api-token
   ```

2. 更新版本号（在 `pyproject.toml` 中）
3. 更新 `CHANGELOG.md`（如果有）
4. 确保所有测试通过

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request来改进这个项目！