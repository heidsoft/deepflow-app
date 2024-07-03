from sanic import Sanic
from sanic import Blueprint
from sanic.response import json as Response
from common.utils import json_response, format_response, app_exception, curl_perform
from common.const import API_PREFIX, HTTP_OK

from config import config
from application.l7_flow_tracing import L7FlowTracing
from application.tracing_completion import TracingCompletion
from models.models import FlowLogL7Tracing, TracingCompletionByExternalAppSpans
from config import config
import logging
from logging.handlers import RotatingFileHandler


server = Sanic(__name__)
# 设置日志级别和日志格式
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 创建一个文件处理器，用于输出到文件
file_handler = RotatingFileHandler('app.log', maxBytes=1024*1024, backupCount=5)
file_handler.setLevel(logging.DEBUG)  # 设置文件处理器的日志级别
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# 获取当前模块的日志记录器
log = logging.getLogger(__name__)
log.addHandler(file_handler)  # 将文件处理器添加到日志记录器中


application_app = Blueprint(str(__name__).replace(".", "_"))


@application_app.route(API_PREFIX + '/querier' + '/L7FlowTracing',
                       methods=['POST'])
@app_exception
async def application_log_l7_tracing(request):
    log.debug("application_log_l7_tracing 111111111111")
    args = FlowLogL7Tracing(request.json)
    args.validate()
    log.info("application_log_l7_tracing 22222222222")

    status, response, failed_regions = await L7FlowTracing(
        args, request.headers).query()
    response_dict, code = format_response("Flow_Log_L7_Tracing", status,
                                          response, args.debug, failed_regions)
    return Response(json_response(**response_dict),
                    content_type='application/json; charset=utf-8',
                    status=code)


@application_app.route(API_PREFIX + '/querier' +
                       '/tracing-completion-by-external-app-spans',
                       methods=['POST'])
@app_exception
async def l7_flow_app_tracing(request):
    args = TracingCompletionByExternalAppSpans(request.json)
    args.validate()
    status, response, failed_regions = await TracingCompletion(
        args, request.headers).query()
    response_dict, code = format_response(
        "tracing-completion-by-external-app-spans", status, response,
        args.debug, failed_regions)
    return Response(json_response(**response_dict),
                    content_type='application/json; charset=utf-8',
                    status=code)


@application_app.route(API_PREFIX + '/hello',
                       methods=['GET'])
@app_exception
async def hello(request):
    log.debug("hello world")
    return Response(json_response({"hello":"world"}),
                    content_type='application/json; charset=utf-8',
                    status=200)


server.blueprint(application_app)


@server.middleware('request')
async def request_started(request):
    log.debug(f"Request started: {request.method} {request.url}")


@server.middleware('response')
async def request_finished(request, response):
    log.debug(f"Request finished with status {response.status}")

def init(app: Sanic, request_timeout, response_timeout):
    if app is None:
        return
    app.update_config({
        "REQUEST_TIMEOUT": request_timeout,
        "RESPONSE_TIMEOUT": response_timeout
    })