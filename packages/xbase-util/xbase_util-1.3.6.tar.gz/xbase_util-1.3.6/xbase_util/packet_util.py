import copy
import re

from xbase_util.xbase_constant import plain_content_type_columns, packetKeyname, src_dst_header, statisticHeader, \
    features_key, plain_body_columns, http_version_pattern, http_req_method_pattern, http_req_path_pattern, \
    res_status_code_pattern, pcap_flow_text_column, abnormal_features_column


def content_type_is_plain(packet):
    """
    从单个包（包括header和body）中获取content-type并判断是否为可见类型
    :param packet:
    :return:
    """
    if ":" not in packet:
        return False
    for item in packet.replace("-", "_").replace(" ", "").lower().splitlines():
        if "content_type" in item:
            if ":" not in item:
                continue
            content_type = item.split(":")[1].replace("\r", "").strip()
            return content_type in plain_content_type_columns
    return False


def get_all_columns(
        contains_packet_column=False,
        contains_src_dst_column=False,
        contains_statistic_column=False,
        contains_features_column=False,
        contains_plain_body_column=False,
        contains_pcap_flow_text=False,
        contains_abnormal_features_column=False,
):
    result_columns = []
    if contains_packet_column:
        result_columns += packetKeyname
    if contains_src_dst_column:
        result_columns += src_dst_header
    if contains_statistic_column:
        result_columns += statisticHeader
    if contains_features_column:
        result_columns += features_key
    if contains_plain_body_column:
        result_columns += plain_body_columns
    if contains_pcap_flow_text:
        result_columns += pcap_flow_text_column
    if contains_abnormal_features_column:
        result_columns += abnormal_features_column
    return result_columns


# req_pattern = re.compile(r"(GET|POST|HEAD|PUT|DELETE|OPTIONS|PATCH) \/[^\s]* HTTP\/\d\.\d[\s\S]*?\r\n\r\n",
#                          re.DOTALL)
# res_pattern = re.compile(r"HTTP/\d\.\d \d{3}.*", re.DOTALL)
# req_body_pattern = re.compile(
#     r"(GET|POST|HEAD|PUT|DELETE|OPTIONS|PATCH) \/[^\s]* HTTP\/\d\.\d[\s\S]*?(?=HTTP/\d\.\d)", re.DOTALL)

# def firstOrZero(param):
#     if type(param).__name__ == 'list':
#         if (len(param)) != 0:
#             return param[0]
#         else:
#             return 0
#     else:
#         return 0


def get_header_value(header_set, value):
    result = [item for item in header_set if value in item]
    if len(result) != 0:
        return result[0].replace(f"{value}:", "").strip()
    else:
        return ""


def get_detail_by_package(publicField, req_header, req_body, res_header, res_body,enable_abnormal_field=True):
    """
    通过pcap的数量分离session并完善相关字段
    :param publicField: 原始的session单条数据
    :param req_header:请求头
    :param req_body:请求体
    :param res_header:响应头
    :param res_body:响应体
    :return: 完整的单条数据
    """
    res_field = copy.deepcopy(publicField)
    res_field["initRTT"] = res_field.get("initRTT", 0)
    res_field["length"] = res_field.get("length", 0)

    http_version_res = http_version_pattern.findall(req_header)
    res_field['http.clientVersion'] = http_version_res[0] if len(http_version_res) > 0 else ""
    http_method = http_req_method_pattern.findall(req_header)
    http_path = http_req_path_pattern.findall(req_header)
    res_field['http.clientVersion'] = http_version_res[0] if len(http_version_res) > 0 else ""
    res_field['http.method'] = http_method[0] if len(http_method) > 0 else ""
    res_field['http.path'] = http_path[0] if len(http_path) > 0 else ""
    request_lines = req_header.splitlines()
    res_field['http.request-referer'] = get_header_value(header_set=request_lines, value="Referer")
    res_field['http.request-content-type'] = get_header_value(header_set=request_lines,
                                                              value="Content-Type")
    res_field['http.hostTokens'] = get_header_value(header_set=request_lines, value="Host")

    res_field['plain_body_src'] = ""
    res_field['plain_body_dst'] = ""
    if content_type_is_plain(req_header):
        res_field['plain_body_src'] = req_body.replace("\r", "").replace("\n", "").replace("\t", "").replace(" ", "")
    if content_type_is_plain(res_header):
        res_field['plain_body_dst'] = res_body.replace("\r", "").replace("\n", "").replace("\t", "").replace(" ", "")

    http_server_version_res = http_version_pattern.findall(res_header)
    res_field['http.serverVersion'] = http_server_version_res[0] if len(http_server_version_res) > 0 else ""

    status_code = res_status_code_pattern.findall(res_header)
    res_field['http.statuscode'] = status_code[0] if len(status_code) > 0 else ""
    response_lines = res_header.splitlines()
    res_field['http.response-server'] = get_header_value(header_set=response_lines, value="Server")
    res_field['http.response-content-type'] = get_header_value(header_set=response_lines,
                                                               value="Content-Type")
    for response in list(set(response_lines + request_lines)):
        key_value = response.replace("\r", "").split(":")
        if len(key_value) == 2:
            key = key_value[0].replace(" ", "").replace("-", "_").lower()
            value = key_value[1].replace(" ", "")
            if f"src_{key}" in src_dst_header:
                res_field[f"src_{key}"] = value
            if f"dst_{key}" in src_dst_header:
                res_field[f"dst_{key}"] = value
    # 注意若非enable_abnormal_field，则 get_all_columns 时候关掉 contains_abnormal_features_column
    if enable_abnormal_field:
        res_field['abnormal_has_xff'] = has_xss_injection([req_body])
        res_field['abnormal_has_dir_penetration'] = has_dir_penetration([req_header, req_body])
        res_field['abnormal_has_templates_injection'] = has_templates_injection([req_header, req_body])
        res_field['abnormal_has_crlf_injection'] = has_crlf_injection([req_header, req_body])
        res_field['abnormal_has_xxe_attack'] = has_xxe_attack([req_header, req_body])
        res_field['abnormal_has_code_injection_or_execute'] = has_code_injection_or_execute([req_header, req_body])
        res_field['abnormal_has_sql_injection'] = has_sql_injection([req_header, req_body])
    return res_field


def str_list_in_list(str_list, features_list):
    for str_item in str_list:
        if len([item for item in features_list if item in str_item]):
            return True
    return False


def has_dir_penetration(str_list):
    return str_list_in_list(str_list, features_list=["../", "/..", "..", "%2e%2e", "%2F..","..%2f",".%2e/","/.%2e"])


def has_sql_injection(str_list):
    return str_list_in_list(str_list, features_list=['%20union%20select', '--', ' union select'])


def has_xss_injection(str_list):
    pattern = re.compile(r"<script>alert.*?onerror=alert.*?<script>prompt.*?alert\(")
    for str_item in str_list:
        if pattern.search(str_item):
            return True
    return False


def has_templates_injection(str_list):
    return str_list_in_list(str_list, features_list=["{{", "}}"])


def has_crlf_injection(str_list):
    return str_list_in_list(str_list, features_list=["%0D%0A"])


def has_xxe_attack(str_list):
    return str_list_in_list(str_list, features_list=['"SYSTEM "'])


def has_code_injection_or_execute(str_list):
    return str_list_in_list(str_list, features_list=['command', 'var_dump', 'execute(', 'md5(','unlink('])
