from typing import Literal

import splunklib.client as client
from splunklib import results

from xbase_util.common_util import date2s
from xbase_util.xbase_constant import waf_exp_file, pa_exp_file, new_pa_exp_file

PA_TYPE=Literal["PA","NEW_PA"]

def get_splunk_pa(start_time, end_time, splunk_host,
                  splunk_port,
                  splunk_username,
                  splunk_password,
                  splunk_scheme="https",
                  count=10000,pa_type:PA_TYPE="PA"):
    """
    获取PA威胁信息

    :param count: 数量限制
    :param dedup: 是否去重
    :param start_time:
    :param end_time:
    :param splunk_host:
    :param splunk_port:
    :param splunk_username:
    :param splunk_password:
    :param splunk_scheme:
    :param pa_type:
    :return:
    """
    service = client.connect(
        host=splunk_host,
        port=splunk_port,
        scheme=splunk_scheme,
        username=splunk_username,
        password=splunk_password
    )

    with open(pa_exp_file if pa_type=="PA" else new_pa_exp_file)as f:
        exp = f.read()
    job = service.jobs.oneshot(exp, **{
        "earliest_time": date2s(start_time, pattern='%Y-%m-%dT%H:%M:%S'),
        "latest_time": date2s(end_time, pattern='%Y-%m-%dT%H:%M:%S'),
        "output_mode": "json",
        "count": count
    })
    return [item for item in results.JSONResultsReader(job) if isinstance(item, dict)]




def get_splunk_waf(start_time,
                   end_time,
                   splunk_host,
                   splunk_port,
                   splunk_username,
                   splunk_password,
                   splunk_scheme="https", count=10000):
    service = client.connect(
        host=splunk_host,
        port=splunk_port,
        scheme=splunk_scheme,
        username=splunk_username,
        password=splunk_password)
    with open(waf_exp_file) as f:
        exp = f.read()
    job = service.jobs.oneshot(
        exp, **{
            "earliest_time": date2s(start_time, pattern='%Y-%m-%dT%H:%M:%S'),
            "latest_time": date2s(end_time, pattern='%Y-%m-%dT%H:%M:%S'),
            "output_mode": "json",
            "count": count
        })
    return [item for item in results.JSONResultsReader(job) if isinstance(item, dict)]
