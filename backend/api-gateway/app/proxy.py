import httpx
from fastapi import Request, Response, HTTPException
from fastapi.responses import StreamingResponse
import logging

logger = logging.getLogger(__name__)

# Reusable client pool for better performance
client = httpx.AsyncClient()

async def forward_request(request: Request, target_url: str):
    method = request.method
    headers = dict(request.headers)
    # Remove host header to avoid conflicts when forwarding
    headers.pop("host", None)
    
    body = await request.body()
    
    try:
        url = httpx.URL(target_url)
        req = client.build_request(
            method=method,
            url=url,
            headers=headers,
            content=body,
            params=request.query_params,
        )
        
        response = await client.send(req, stream=True)
        
        # We stream the response back to the client to handle large payloads (like SSE) efficiently
        return StreamingResponse(
            response.aiter_raw(),
            status_code=response.status_code,
            headers=dict(response.headers)
        )
        
    except httpx.RequestError as e:
        logger.error(f"Proxy error when calling {target_url}: {e}")
        raise HTTPException(status_code=502, detail="Bad Gateway")
