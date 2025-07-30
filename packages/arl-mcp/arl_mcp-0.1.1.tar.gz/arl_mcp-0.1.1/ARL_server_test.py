# ARL_server.py
import re
import time
import requests
import tldextract
import urllib3
from mcp.server.fastmcp import FastMCP

# 初始化 MCP 服务，命名为 Math，可根据业务场景自定义名称
mcp = FastMCP("Math")

# 关闭 urllib3 的 HTTPS 不安全请求警告（用于测试阶段）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# BurpSuite 或其他代理配置（用于调试）
# proxies = {
#     'http': '127.0.0.1:8080',
#     'https': '127.0.0.1:8080'
# }


@mcp.tool()
def extract_main_domain(RequestBody: str) -> str:
    """
    从原始 HTTP 数据包中提取主域名。

    参数：
    - RequestBody：包含 Host 字段的原始 HTTP 请求包

    返回：
    - 主域名，例如 'baidu.com'、'dzhsj.cn'。
    """
    match = re.search(r"Host:\s*([^\s:]+)", RequestBody)
    if not match:
        return "host not found"

    host = match.group(1).strip()
    extracted = tldextract.extract(host)
    if extracted.domain and extracted.suffix:
        return f"{extracted.domain}.{extracted.suffix}"
    return host  # fallback，当 tldextract 无法正确提取时


@mcp.tool()
def sleep_for(seconds: int) -> str:
    """
    LangGraph 节流工具节点：阻塞流程指定秒数，用于控制过快轮询。

    参数：
    - seconds: int，休眠时长（秒）

    返回：
    - 提示信息字符串，如 "slept for 60 seconds"
    """
    time.sleep(seconds)
    return f"slept for {seconds} seconds"

@mcp.tool()
def extract_domain_or_ip(text: str) -> str:
    """
    功能：从纯文本中提取主域名、IP 地址或 IP 段（自动判断）。

    参数：
    - text: str，用户输入，如 www.baidu.com、1.1.1.1、192.168.0.0/24

    返回：
    - str：提取出的主域名或 IP 内容。
    """
    if "/" in text or re.match(r"^\d+\.\d+\.\d+\.\d+", text):
        return text.strip()
    else:
        extracted = tldextract.extract(text)
        if extracted.domain and extracted.suffix:
            return f"{extracted.domain}.{extracted.suffix}"
        return text

@mcp.tool()
def add_scan_task(
    name: str,
    target: str,
    domain_brute: bool,
    alt_dns: bool,
    dns_query_plugin: bool,
    arl_search: bool,
    port_scan: bool,
    skip_scan_cdn_ip: bool,
    site_identify: bool,
    search_engines: bool,
    site_spider: bool,
    file_leak: bool,
    findvhost: bool
):
    """
    根据传入的参数，先创建一个 ARL 平台的扫描任务。

    参数：
    - name: 任务名称（建议唯一），如 "scan-baidu.com"
    - target: str，扫描目标（域名/IP/IP段）
    - 其余参数均为布尔值，表示是否启用对应模块，如子域名爆破、端口扫描等

    返回：
    - 包含任务提交状态和响应内容的字典
    """
    url = "https://39.105.57.223:5003/api/task/"
    headers = {
        "Content-Type": "application/json",
        "Token": "7AEwZC3eOJ6A4rLjXqRZ0PVx00L8EfkeVg",
        "Accept": "application/json"
    }

    payload = {
        "name": name,
        "target": target,
        "domain_brute_type": "big",
        "port_scan_type": "top1000",
        "domain_brute": domain_brute,
        "alt_dns": alt_dns,
        "dns_query_plugin": dns_query_plugin,
        "arl_search": arl_search,
        "port_scan": port_scan,
        "service_detection": False,
        "os_detection": False,
        "ssl_cert": False,
        "skip_scan_cdn_ip": skip_scan_cdn_ip,
        "site_identify": site_identify,
        "search_engines": search_engines,
        "site_spider": site_spider,
        "site_capture": False,
        "file_leak": file_leak,
        "findvhost": findvhost,
        "nuclei_scan": False
    }
    try:
        # response = requests.post(url, headers=headers, json=payload, proxies=proxies, verify=False)
        response = requests.post(url, headers=headers, json=payload,verify=False)
        try:
            return {
                "status_code": response.status_code,
                "response": response.json()
            }
        except Exception:
            return {
                "status_code": response.status_code,
                "response": response.text
            }
    except Exception as e:
        return {"status_code": -1, "error": str(e)}


@mcp.tool()
def query_task_status(name: str) -> dict:
    """
    先创建任务,再查询 ARL 扫描任务的当前执行状态，支持判断多个模块是否执行完毕：
    - 子域名获取：domain_brute
    - IP 信息提取：port_scan
    - 站点识别：site_identify
    - 文件泄露：file_leak

    参数：
    - name: str，任务名称，如 'scan-example.com'

    返回：
    - dict 格式：
      {
        "state": str，状态关键词，可为：
            - "domain_brute_done"：域名枚举完成；
            - "ip_done"：IP 提取相关模块完成；
            - "site_done"：站点探测完成；
            - "fileleak_done"：文件泄露探测完成；
            - "done"：所有模块已执行完成；
            - "running"：任务执行中；
            - "not_found"：找不到任务；
            - "exception"：出现异常；
        "current_module": str，当前正在执行的模块（如 port_scan）
        "completed_modules": list[str]，已完成模块名称
      }

    推荐用途：
    - LangGraph 条件节点判断是否允许调用具体查询函数（如 get_all_subdomains）
    - 配合 sleep 节流避免 MCP 递归过快触发 RecursionError

    节流建议：
    - 若返回 running 状态，请间隔 30~60 秒调用；
    - 若状态为 *_done 或 done，即可安全执行后续步骤；
    - 超过 10 分钟未完成应终止流程并提示。
    """
    url = "https://39.105.57.223:5003/api/task/"
    headers = {
        "Token": "7AEwZC3eOJ6A4rLjXqRZ0PVx00L8EfkeVg",
        "Accept": "application/json"
    }
    params = {"name": name, "size": "1"}

    try:

        # resp = requests.get(url, headers=headers, params=params, proxies=proxies, verify=False, timeout=10)
        resp = requests.get(url, headers=headers, params=params, verify=False, timeout=10)
        if resp.status_code != 200:
            return {"state": "error", "reason": f"HTTP {resp.status_code}"}

        data = resp.json()
        items = data.get("items", [])
        if not items:
            return {"state": "not_found"}

        item = items[0]
        current_status = item.get("status", "unknown")
        completed_services = [s.get("name") for s in item.get("service", []) if s.get("name")]

        # 默认状态
        state = "running"

        # 子域名已完成
        if "arl_search" in completed_services:
            state = "domain_brute_done"

        # IP 扫描已完成
        if "port_scan" in completed_services:
            state = "ip_done"

        # 站点识别完成
        if "site_spide" in completed_services:
            state = "site_done"

        # 文件泄露扫描完成
        if "file_leak" in completed_services:
            state = "fileleak_done"

        # 全部完成
        if current_status == "done":
            state = "done"

        return {
            "state": state,
            "current_module": current_status,
            "completed_modules": completed_services
        }

    except Exception as e:
        return {"state": "exception", "reason": str(e)}


@mcp.tool()
def get_all_subdomains(domain: str) -> list[str]:
    """

    工具名称：get_all_subdomains
    功能：创建ARL 平台的扫描任务后，根据任务完成状态，获取指定主域名的子域名信息。

    参数：
    - domain: 主域名，例如 'baidu.com'

    返回：
    - 子域名列表，例如 ['a.baidu.com', 'b.baidu.com', ...]
    """
    url = "https://39.105.57.223:5003/api/domain/"
    headers = {
        "Token": "7AEwZC3eOJ6A4rLjXqRZ0PVx00L8EfkeVg"
    }
    page = 1
    size = 100
    subdomains = []

    try:
        while True:
            params = {
                "domain": domain,
                "page": page,
                "size": size
            }
            # response = requests.get(url, headers=headers, params=params, proxies=proxies, verify=False)
            response = requests.get(url, headers=headers, params=params, verify=False)
            if response.status_code != 200:
                return [f"Request failed: {response.status_code}"]

            json_data = response.json()
            items = json_data.get("items", [])
            if not items:
                break

            subdomains += [item.get("domain") for item in items if item.get("domain")]

            if len(items) < size:
                break

            page += 1

        return list(set(subdomains))
    except Exception as e:
        return [f"Error: {str(e)}"]


@mcp.tool()
def query_ip_list(domain: str) -> list[str]:
    """
    功能：创建ARL 平台的扫描任务后，根据任务完成状态，获取指定主域名的 IP 地址信息。

    参数：
    - domain: 主域名，例如 'dzhsj.cn'

    返回：
    - IP 地址列表
    """
    url = "https://39.105.57.223:5003/api/ip/"
    headers = {"Token": "7AEwZC3eOJ6A4rLjXqRZ0PVx00L8EfkeVg"}
    page, size = 1, 100
    all_ips = []

    try:
        while True:
            params = {"domain": domain, "page": page, "size": size}
            # resp = requests.get(url, headers=headers, params=params, proxies=proxies, verify=False, timeout=10)
            resp = requests.get(url, headers=headers, params=params, verify=False, timeout=10)
            data = resp.json()
            items = data.get("items", [])
            all_ips.extend([item.get("ip") for item in items if item.get("ip")])
            if len(items) < size:
                break
            page += 1
        return all_ips
    except Exception as e:
        return [f"Error: {str(e)}"]


@mcp.tool()
def query_site_list(domain: str) -> list[str]:
    """
    功能：创建ARL 平台的扫描任务后，根据任务完成状态，获取指定主域名下的站点地址。

    参数：
    - domain: 主域名，例如 'dzhsj.cn'

    返回：
    - 站点 URL 列表
    """
    url = "https://39.105.57.223:5003/api/site/"
    headers = {"Token": "7AEwZC3eOJ6A4rLjXqRZ0PVx00L8EfkeVg"}
    page, size = 1, 100
    all_sites = []

    try:
        while True:
            params = {"site": domain, "page": page, "size": size}
            # resp = requests.get(url, headers=headers, params=params, proxies=proxies, verify=False, timeout=10)
            resp = requests.get(url, headers=headers, params=params,verify=False, timeout=10)
            data = resp.json()
            items = data.get("items", [])
            all_sites.extend([item.get("site") for item in items if item.get("site")])
            if len(items) < size:
                break
            page += 1
        return all_sites
    except Exception as e:
        return [f"Error: {str(e)}"]


@mcp.tool()
def query_fileleak_list(domain: str) -> list[str]:
    """
    功能：创建ARL 平台的扫描任务后，根据任务完成状态，获取指定主域名下的文件泄露链接。

    参数：
    - domain: 主域名，例如 'baidu.com'

    返回：
    - 泄露链接列表
    """
    url = "https://39.105.57.223:5003/api/fileleak/"
    headers = {"Token": "7AEwZC3eOJ6A4rLjXqRZ0PVx00L8EfkeVg"}
    page, size = 1, 100
    all_urls = []

    try:
        while True:
            params = {"url": domain, "page": page, "size": size}
            # resp = requests.get(url, headers=headers, params=params, proxies=proxies, verify=False, timeout=10)
            resp = requests.get(url, headers=headers, params=params, verify=False, timeout=10)
            data = resp.json()
            items = data.get("items", [])
            all_urls.extend([item.get("url") for item in items if item.get("url")])
            if len(items) < size:
                break
            page += 1
        return all_urls
    except Exception as e:
        return [f"Error: {str(e)}"]


if __name__ == "__main__":
    print("[+] mcp demo 正在运行11")
    mcp.run(transport="stdio")
