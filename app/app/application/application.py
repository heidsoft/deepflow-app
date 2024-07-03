from sanic import Blueprint
from sanic.response import json as Response
from common.utils import json_response, format_response, app_exception, curl_perform
from common.const import API_PREFIX, HTTP_OK

from config import config
from .l7_flow_tracing import L7FlowTracing
from .tracing_completion import TracingCompletion
from models.models import FlowLogL7Tracing, TracingCompletionByExternalAppSpans
import logging


# 获取主应用程序文件中配置的日志对象
log = logging.getLogger(__name__)

