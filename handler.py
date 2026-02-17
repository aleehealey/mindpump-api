"""
AWS Lambda handler: wraps Django ASGI app with Mangum for API Gateway / Lambda.
Set AWS_LAMBDA_FUNCTION_HANDLER=handler.handler in the Lambda config.
"""
from mangum import Mangum
from mindpump.asgi import application

# lifespan="off" avoids ASGI lifespan events Django doesn't use; recommended for Django
handler = Mangum(application, api_gateway_base_path="/default/mindpump-api", lifespan="off")
