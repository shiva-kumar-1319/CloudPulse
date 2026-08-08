import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# Prometheus metrics definitions
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests received",
    ["service", "method", "endpoint", "status_code"]
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["service", "endpoint"]
)

ERROR_COUNT = Counter(
    "http_requests_errors_total",
    "Total HTTP request errors",
    ["service", "endpoint", "status_code"]
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """
    Middleware to automatically record request counts, latencies, and error rates.
    """
    def __init__(self, app, service_name: str):
        super().__init__(app)
        self.service_name = service_name

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        endpoint = request.url.path
        
        try:
            response: Response = await call_next(request)
            status_code = str(response.status_code)
            duration = time.time() - start_time
            
            REQUEST_COUNT.labels(
                service=self.service_name,
                method=request.method,
                endpoint=endpoint,
                status_code=status_code
            ).inc()
            
            REQUEST_LATENCY.labels(
                service=self.service_name,
                endpoint=endpoint
            ).observe(duration)

            if response.status_code >= 400:
                ERROR_COUNT.labels(
                    service=self.service_name,
                    endpoint=endpoint,
                    status_code=status_code
                ).inc()

            return response
        except Exception as exc:
            duration = time.time() - start_time
            REQUEST_COUNT.labels(
                service=self.service_name,
                method=request.method,
                endpoint=endpoint,
                status_code="500"
            ).inc()
            
            REQUEST_LATENCY.labels(
                service=self.service_name,
                endpoint=endpoint
            ).observe(duration)

            ERROR_COUNT.labels(
                service=self.service_name,
                endpoint=endpoint,
                status_code="500"
            ).inc()
            raise exc


def get_metrics_response() -> Response:
    """
    Generate Prometheus metrics HTTP response.
    """
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
