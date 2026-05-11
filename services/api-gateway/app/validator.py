from fastapi import Request

async def validate_request(request: Request):
    
    if request.method in ["POST", "PUT", "PATCH"]:
        content_type = request.headers.get("content-type", "")
        
        if "application/json" not in content_type:
            return False, "Invalid Content-Type. Must be application/json"

    return True, None