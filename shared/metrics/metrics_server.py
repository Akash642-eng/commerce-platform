from prometheus_client import start_http_server

def start_metrics_server(port: int):

    try:
        start_http_server(port)
        print(f"Metrics server started on port {port}")
    except Exception as e:
        print(f"Error starting metrics server: {e}")