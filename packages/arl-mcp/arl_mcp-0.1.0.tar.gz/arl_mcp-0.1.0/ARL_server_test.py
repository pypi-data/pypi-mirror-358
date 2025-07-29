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
proxies = {
    'http': '127.0.0.1:8080',
    'https': '127.0.0.1:8080'
}


@mcp.tool()
def extract_main_domain(packet: str) -> str:
    """
    从原始 HTTP 数据包中提取主域名。

    参数：
    - packet：包含 Host 字段的原始 HTTP 请求包

    返回：
    - 主域名，例如 'baidu.com'、'dzhsj.cn'。
    """
    match = re.search(r"Host:\s*([^\s:]+)", packet)
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
        response = requests.post(url, headers=headers, json=payload, proxies=proxies, verify=False)
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
def query_task_status(name: str) -> str:
    """
    查询 ARL 扫描任务的当前执行状态，主要用于判断子域名枚举模块是否已经完成。

    参数：
    - name: str
        扫描任务名称，例如 "scan-example.com"。

    返回：
    - dict
        {
            "state": str           # 任务整体状态，可能值包括：
                                  # - "domain_brute_done"：子域名爆破模块已完成（可调用子域名提取）；
                                  # - "done"：所有扫描模块执行完毕；
                                  # - "running"：仍有模块在执行，不能提取；
                                  # - "not_found"：未找到任务；
                                  # - "exception"：请求异常或超时；
            "current_module": str  # 当前正在运行的模块，例如 "port_scan"、"site_identify"；
            "completed_modules": List[str]  # 已完成模块名称列表，例如 ["domain_brute", "alt_dns"]
        }

    推荐用途：
    - LangGraph 条件节点判断：是否允许执行 `get_all_subdomains(domain)`
    - 自动化流程节流控制，避免频繁轮询或提前请求

    合理轮询建议：
    - 若返回状态为 "running"，建议每隔 30～60 秒调用一次该函数（避免 MCP 频繁调用导致递归超限）；
    - 若返回为 "domain_brute_done" 或 "done"，即表示子域名相关数据已可获取；
    - 超过合理等待时间（如 10 分钟）仍未完成，应中止流程并提示用户。

    注意事项：
    - 任务状态并非实时更新，请根据实际任务耗时设置合理间隔；
    - MCP 调用间隔建议通过 sleep 工具辅助节流，如 `sleep_for(60)`
    """
    url = "https://39.105.57.223:5003/api/task/"
    headers = {
        "Token": "7AEwZC3eOJ6A4rLjXqRZ0PVx00L8EfkeVg",
        "Accept": "application/json"
    }
    params = {"name": name,"size":"1"}

    try:
        resp = requests.get(url, headers=headers, params=params, proxies=proxies, verify=False, timeout=10)
        if resp.status_code != 200:
            return {"state": "error", "reason": f"HTTP {resp.status_code}"}

        data = resp.json()
        items = data.get("items", [])
        if not items:
            return {"state": "not_found"}

        item = items[0]
        current_status = item.get("status", "unknown")
        completed_services = [s.get("name") for s in item.get("service", []) if s.get("name")]

        state = "running"
        if "domain_brute" in completed_services:
            state = "domain_brute_done"
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
            response = requests.get(url, headers=headers, params=params, proxies=proxies, verify=False)
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


if __name__ == "__main__":
    print("[+] mcp demo 正在运行11")
    mcp.run(transport="stdio")
