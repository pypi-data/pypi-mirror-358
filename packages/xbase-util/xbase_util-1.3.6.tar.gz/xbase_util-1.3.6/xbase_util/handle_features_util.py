import json
import re
import traceback
from urllib.parse import unquote, urlparse, parse_qs

import pandas as pd

from xbase_util.xbase_constant import regex_patterns


def handle_uri(data, use_tqdm=True):
    def is_valid_url(url):
        if not url or not isinstance(url, str):
            return False
        try:
            parsed = urlparse(url)
            # 判断主机名是否合法（可选）
            if parsed.hostname:
                # 如果需要，校验ipv4/ipv6格式
                pass
            return True
        except Exception:
            return False
    def process_row(row):
        url = row['req_uri']
        if not is_valid_url(url):
            param_count, path_depth, param_length_avg, param_length_max = 0, 0, 0, 0
        else:
            parsed = urlparse(url)
            path = parsed.path.strip('/')
            path_segments = path.split('/') if path else []
            path_depth = len(path_segments)
            query = parsed.query
            params = parse_qs(query)
            param_values = [unquote(v) for vs in params.values() for v in vs]
            param_lengths = [len(v) for v in param_values]
            param_count = len(param_lengths)
            param_length_avg = sum(param_lengths) / param_count if param_count > 0 else 0
            param_length_max = max(param_lengths) if param_lengths else 0

        result = {
            "URI_FEATURES_EXTRA_param_count": param_count,
            "URI_FEATURES_EXTRA_path_depth": path_depth,
            "URI_FEATURES_EXTRA_param_length_avg": param_length_avg,
            "URI_FEATURES_EXTRA_param_length_max": param_length_max,
        }
        for key, value in regex_patterns.items():
            result[f"URI_FEATURES_EXTRA_contains_{key}"] = True if value.search(unquote(url or '')) else False
        return result

    if use_tqdm:
        feature_data = data.progress_apply(process_row, axis=1, result_type="expand")
    else:
        feature_data = data.apply(process_row, axis=1, result_type="expand")
    data = pd.concat([data, feature_data], axis=1)
    return data


def handle_ua(data, use_tqdm=True):
    data['http.useragent'] = data['http.useragent'].fillna('').astype(str)
    # 处理换行符及多余空格
    data['http.useragent'] = data['http.useragent'].str.replace(r'\s+', ' ', regex=True)
    # 常见攻击的 User-Agent 字符串匹配模式，忽略大小写
    attack_patterns = '|'.join([
        r"\bselect\b", r"\bunion\b", r"\binsert\b", r"\bupdate\b", r"\bdelete\b", r"\bdrop\b", r"--", r"#", r" or ",
        r"' or '",
        r"information_schema", r"database\(\)", r"version\(\)",  # SQL注入相关
        r"<script>", r"javascript:", r"onload=", r"onclick=", r"<iframe>", r"src=",  # XSS相关
        r"/etc/passwd", r"/etc/shadow", r"\&\&", r"\|", r"\$\(\)", r"exec", r"system",  # 命令执行相关
        r"\.\./", r"\.\.%2f", r"\.\.%5c", r"%c0%af", r"%252e%252e%252f",  # 路径遍历
        r"\.php", r"\.asp", r"\.jsp", r"\.exe", r"\.sh", r"\.py", r"\.pl",  # 文件扩展名
        r"redirect=", r"url=", r"next=",  # 重定向
        r"%3C", r"%3E", r"%27", r"%22", r"%00", r"%2F", r"%5C", r"%3B", r"%7C", r"%2E", r"%28", r"%29",  # 编码
        r'Googlebot', r'Bingbot', r'Slurp', r'curl', r'wget', r'Nmap',
        r'SQLMap', r'Nikto', r'Dirbuster', r'python-requests', r'Apache-HttpClient',
        r'Postman', r'Burp Suite', r'Fuzzing', r'nessus'
    ])
    # 企业客户端 User-Agent 模式
    enterprise_patterns = '|'.join([
        r'MicroMessenger', r'wxwork', r'QQ/', r'QQBrowser', r'Alipay', r'UCWEB'
    ])
    # 批量检查是否为攻击的 User-Agent，忽略大小写
    data['UserAgent_is_attack'] = data['http.useragent'].str.contains(attack_patterns, case=False, regex=True)
    # 批量检查是否为企业客户端，忽略大小写
    data['UserAgent_is_enterprise'] = data['http.useragent'].str.contains(enterprise_patterns, case=False)
    # 提取浏览器和版本
    data['UserAgent_browser'] = data['http.useragent'].str.extract(r'(Chrome|Firefox|Safari|MSIE|Edge|Opera|Trident)',
                                                                   expand=False, flags=re.IGNORECASE).fillna("Unknown")
    data['UserAgent_browser_version'] = data['http.useragent'].str.extract(
        r'Chrome/([\d\.]+)|Firefox/([\d\.]+)|Version/([\d\.]+).*Safari|MSIE ([\d\.]+)|Edge/([\d\.]+)|Opera/([\d\.]+)|Trident/([\d\.]+)',
        expand=False, flags=re.IGNORECASE).bfill(axis=1).fillna("Unknown").iloc[:, 0]
    # 提取操作系统和版本
    os_info = data['http.useragent'].str.extract(
        r'(Windows NT [\d\.]+|Mac OS X [\d_\.]+|Linux|Android [\d\.]+|iOS [\d_\.]+|Ubuntu|Debian|CentOS|Red Hat)',
        expand=False, flags=re.IGNORECASE)
    data['UserAgent_os'] = os_info.str.extract(r'(Windows|Mac OS X|Linux|Android|iOS|Ubuntu|Debian|CentOS|Red Hat)',
                                               expand=False, flags=re.IGNORECASE).fillna("Unknown")
    data['UserAgent_os_version'] = os_info.str.extract(r'([\d\._]+)', expand=False).fillna("Unknown")
    # 提取设备类型，忽略大小写
    data['UserAgent_device_type'] = data['http.useragent'].str.contains('mobile|android|iphone', case=False).map(
        {True: 'Mobile', False: 'Desktop'})
    # 提取硬件平台，增加对 x64 的匹配
    data['UserAgent_platform'] = data['http.useragent'].str.extract(r'(x86|x86_64|arm|arm64|x64)', expand=False,
                                                                    flags=re.IGNORECASE).fillna('Unknown')
    # 判断是否为爬虫，忽略大小写
    data['UserAgent_is_bot'] = data['http.useragent'].str.contains('bot|crawler|spider|slurp|curl|wget|httpclient',
                                                                   case=False)
    # 提取语言偏好（如果存在），忽略大小写
    data['UserAgent_language'] = data['http.useragent'].str.extract(r'\b([a-z]{2}-[A-Z]{2})\b', expand=False,
                                                                    flags=re.IGNORECASE).fillna("Unknown")
    # 统计 User-Agent 中的特殊字符个数

    if use_tqdm:
        data['UserAgent_special_char_count'] = data['http.useragent'].progress_apply(
            lambda x: len(re.findall(r'[!@#$%^&*\'=:|{}]', x, flags=re.IGNORECASE)))
    else:
        data['UserAgent_special_char_count'] = data['http.useragent'].apply(
            lambda x: len(re.findall(r'[!@#$%^&*\'=:|{}]', x, flags=re.IGNORECASE)))

    # 更新 UserAgent_is_unknown 的计算逻辑
    data['UserAgent_is_unknown'] = data[['UserAgent_browser', 'UserAgent_os', 'UserAgent_platform']].isna().any(
        axis=1).fillna("Unknown")
    return data
