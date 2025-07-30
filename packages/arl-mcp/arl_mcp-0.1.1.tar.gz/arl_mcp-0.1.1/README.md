# ARL MCP Server

A Model Context Protocol (MCP) server for ARL platform integration.

## 简介

ARL MCP Server 是一个基于 Model Context Protocol (MCP) 的服务器，用于与 ARL (Asset Reconnaissance Lighthouse) 平台集成。它提供了一系列工具函数，可以通过 MCP 协议调用 ARL 平台的各种功能。

## 功能特性

- **域名提取**: 从 HTTP 数据包中提取主域名
- **任务管理**: 创建和查询 ARL 平台扫描任务
- **子域名枚举**: 获取指定域名的所有子域名
- **IP 地址发现**: 获取域名对应的 IP 地址列表
- **站点识别**: 获取域名下的所有站点地址
- **文件泄露检测**: 发现潜在的文件泄露链接
- **节流控制**: 内置休眠功能，避免过快轮询

## 安装

### 使用 uvx (推荐)

```bash
# 直接运行（无需安装）
uvx arl-mcp

# 从 GitHub 运行
uvx --from git+https://github.com/WACHI/arl-mcp.git arl-mcp

# 从本地路径运行
uvx --from ./dist/arl_mcp-0.1.0-py3-none-any.whl arl-mcp
```

### 使用 pip

```bash
pip install arl-mcp
```

## 使用方法

### 启动服务器

```bash
arl-mcp
```

### 可用工具函数

1. **extract_main_domain(packet: str)**: 从 HTTP 数据包中提取主域名
2. **extract_domain_or_ip(text: str)**: 从文本中提取域名或 IP
3. **sleep_for(seconds: int)**: 休眠指定秒数
4. **add_scan_task(...)**: 创建 ARL 扫描任务
5. **query_task_status(name: str)**: 查询任务状态
6. **get_all_subdomains(domain: str)**: 获取子域名列表
7. **query_ip_list(domain: str)**: 获取 IP 地址列表
8. **query_site_list(domain: str)**: 获取站点列表
9. **query_fileleak_list(domain: str)**: 获取文件泄露链接

## 配置要求

- Python 3.8+
- ARL 平台访问权限
- 有效的 ARL API Token

## 开发

### 本地开发安装

```bash
git clone https://github.com/WACHI/arl-mcp.git
cd arl-mcp
pip install -e .
```

### 运行测试

```bash
pytest
```

### 构建包

```bash
python -m build
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 注意事项

⚠️ **安全提醒**: 
- 请确保 API Token 的安全性
- 不要在公开代码中暴露敏感信息
- 建议在生产环境中使用环境变量管理配置

## 联系方式

如有问题或建议，请通过 GitHub Issues 联系我们。