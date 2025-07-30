# MCP Web Search Server 基准测试指南

本文档详细介绍了如何对MCP Web Search Server进行性能基准测试。

## 📋 测试工具概览

### 测试脚本

| 脚本名称 | 用途 | 特点 |
|----------|------|------|
| `quick_benchmark.py` | 快速性能测试 | 轻量级，适合日常检查 |
| `benchmark.py` | 完整性能测试 | 全面测试，包含系统监控 |
| `benchmark_report.py` | 报告生成器 | 生成详细的分析报告 |
| `run_benchmark.sh` | 统一启动脚本 | 一键运行各种测试 |

### 配置文件

- `benchmark_config.json` - 测试配置参数
- `benchmark_results.csv` - CSV格式测试结果
- `benchmark_report.md` - Markdown格式详细报告

## 🚀 快速开始

### 1. 环境准备

确保已经设置好MCP服务环境：

```bash
# 创建虚拟环境并安装依赖
./start_server.sh
```

### 2. 运行快速测试

```bash
# 使用统一脚本（推荐）
./run_benchmark.sh --quick

# 或直接运行
source venv/bin/activate
python quick_benchmark.py
```

### 3. 查看结果

测试完成后会自动生成：
- `benchmark_report.md` - 详细报告
- `benchmark_results.csv` - 数据表格
- `quick_benchmark_results.json` - 原始数据

## 📊 测试类型详解

### 快速基准测试

**用途**: 日常性能检查，快速验证服务状态

**测试内容**:
- 搜索功能性能 (8次请求)
- 内容获取性能 (3次请求)
- 并发处理能力 (3个并发请求)

**运行时间**: 约1-2分钟

```bash
./run_benchmark.sh --quick
```

### 完整基准测试

**用途**: 全面性能评估，包含系统资源监控

**测试内容**:
- 顺序性能测试 (30次请求)
- 并发性能测试 (5个worker，每个4次请求)
- 压力测试 (30秒持续请求)
- 系统资源监控 (内存、CPU使用率)

**运行时间**: 约3-5分钟

```bash
./run_benchmark.sh --full
```

### 压力测试

**用途**: 极限性能测试，评估服务稳定性

**测试内容**:
- 持续高频请求 (2分钟)
- 实时系统监控
- 错误率统计

**运行时间**: 约2分钟

```bash
./run_benchmark.sh --stress
```

## 📈 性能指标说明

### 响应时间指标

| 指标 | 说明 |
|------|------|
| 平均响应时间 | 所有请求的平均耗时 |
| 中位数响应时间 | 50%请求的响应时间 |
| 95百分位响应时间 | 95%请求的响应时间 |
| 最大响应时间 | 最慢请求的响应时间 |

### 成功率指标

- **成功率**: 成功请求数 / 总请求数 × 100%
- **错误率**: 失败请求数 / 总请求数 × 100%

### 吞吐量指标

- **QPS**: 每秒查询数 (Queries Per Second)
- **并发处理能力**: 同时处理的请求数量

### 系统资源指标

- **内存使用**: 进程内存占用 (MB)
- **CPU使用率**: 进程CPU占用百分比

## 🎯 性能评级标准

### 搜索功能

| 评级 | 响应时间 | 成功率 | 图标 |
|------|----------|--------|----- |
| 优秀 | ≤ 1.5秒 | ≥ 90% | 🟢 |
| 良好 | ≤ 3秒 | ≥ 75% | 🟡 |
| 可接受 | ≤ 5秒 | ≥ 60% | 🟠 |
| 需要改进 | > 5秒 | < 60% | 🔴 |

### 内容获取

| 评级 | 响应时间 | 成功率 | 图标 |
|------|----------|--------|----- |
| 优秀 | ≤ 2秒 | ≥ 90% | 🟢 |
| 良好 | ≤ 5秒 | ≥ 75% | 🟡 |
| 可接受 | ≤ 10秒 | ≥ 60% | 🟠 |
| 需要改进 | > 10秒 | < 60% | 🔴 |

## 🔧 性能优化建议

### 网络层优化

1. **连接池优化**
   ```python
   # 在server.py中调整连接池大小
   connector = aiohttp.TCPConnector(
       limit=100,  # 总连接数
       limit_per_host=30,  # 每个主机连接数
       ttl_dns_cache=300,  # DNS缓存时间
       use_dns_cache=True
   )
   ```

2. **超时设置**
   ```python
   timeout = aiohttp.ClientTimeout(
       total=30,  # 总超时时间
       connect=10,  # 连接超时
       sock_read=20  # 读取超时
   )
   ```

3. **请求头优化**
   ```python
   headers = {
       'User-Agent': 'MCP-WebSearch/1.0',
       'Accept-Encoding': 'gzip, deflate',
       'Connection': 'keep-alive'
   }
   ```

### 应用层优化

1. **缓存策略**
   - 实现搜索结果缓存
   - 使用Redis或内存缓存
   - 设置合理的缓存过期时间

2. **并发控制**
   ```python
   # 限制并发请求数量
   semaphore = asyncio.Semaphore(10)
   
   async def limited_request():
       async with semaphore:
           # 执行请求
           pass
   ```

3. **错误重试**
   ```python
   # 实现指数退避重试
   for attempt in range(3):
       try:
           result = await make_request()
           break
       except Exception:
           await asyncio.sleep(2 ** attempt)
   ```

### 系统层优化

1. **内存管理**
   - 及时释放大对象
   - 使用生成器处理大数据
   - 监控内存泄漏

2. **CPU优化**
   - 使用异步I/O
   - 避免CPU密集型操作
   - 合理使用多进程

## 📊 报告解读

### Markdown报告结构

```
# MCP Web Search Server 性能基准测试报告

## 📊 测试概览
- 测试结果汇总表格
- 性能评级图标

## 📈 详细分析
- 各测试类型的详细指标
- 性能评估和建议

## 💡 优化建议
- 针对性的改进建议
- 性能调优指南
```

### CSV数据分析

可以将CSV文件导入Excel或其他数据分析工具：

1. **趋势分析**: 对比不同时间的测试结果
2. **性能监控**: 设置性能阈值告警
3. **容量规划**: 基于测试数据规划资源

## 🛠️ 自定义测试

### 修改测试参数

编辑 `benchmark_config.json`：

```json
{
  "test_configurations": {
    "custom_test": {
      "description": "自定义测试配置",
      "search_iterations": 20,
      "content_iterations": 10,
      "concurrent_requests": 5,
      "request_delay": 0.1
    }
  }
}
```

### 添加测试用例

在测试脚本中添加新的查询：

```python
test_queries = [
    "你的自定义查询1",
    "你的自定义查询2",
    # ...
]

test_urls = [
    "https://your-test-site1.com",
    "https://your-test-site2.com",
    # ...
]
```

### 自定义性能阈值

修改 `benchmark_config.json` 中的阈值：

```json
{
  "performance_thresholds": {
    "search_response_time": {
      "excellent": 1000,  # 1秒
      "good": 2000,       # 2秒
      "acceptable": 4000  # 4秒
    }
  }
}
```

## 🔍 故障排除

### 常见问题

1. **测试失败**
   ```bash
   # 检查网络连接
   ping google.com
   
   # 检查依赖
   source venv/bin/activate
   pip list
   ```

2. **响应时间过长**
   - 检查网络延迟
   - 验证目标网站可访问性
   - 调整超时设置

3. **成功率低**
   - 检查User-Agent设置
   - 验证请求频率限制
   - 查看错误日志

### 调试模式

启用详细日志：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 网络诊断

```bash
# 测试DNS解析
nslookup duckduckgo.com

# 测试HTTP连接
curl -I https://duckduckgo.com

# 检查代理设置
echo $http_proxy
echo $https_proxy
```

## 📅 定期测试建议

### 测试频率

- **日常检查**: 每天运行快速测试
- **周度评估**: 每周运行完整测试
- **月度审查**: 每月运行压力测试
- **版本发布**: 每次更新后运行全套测试

### 自动化测试

使用cron定时任务：

```bash
# 每天上午9点运行快速测试
0 9 * * * cd /path/to/mcp_dev && ./run_benchmark.sh --quick

# 每周一上午10点运行完整测试
0 10 * * 1 cd /path/to/mcp_dev && ./run_benchmark.sh --full
```

### 结果归档

```bash
# 创建结果归档目录
mkdir -p benchmark_history/$(date +%Y-%m)

# 归档测试结果
cp benchmark_report.md benchmark_history/$(date +%Y-%m)/report_$(date +%Y%m%d_%H%M).md
```

## 📚 参考资料

- [aiohttp性能优化指南](https://docs.aiohttp.org/en/stable/)
- [Python异步编程最佳实践](https://docs.python.org/3/library/asyncio.html)
- [Web性能测试方法论](https://web.dev/performance/)
- [MCP协议规范](https://modelcontextprotocol.io/)

---

*最后更新: 2024年6月*