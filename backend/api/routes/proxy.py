import httpx
import logging
from fastapi import APIRouter, HTTPException, Query, Response
from urllib.parse import unquote

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/proxy", tags=["proxy"])

@router.get("/image")
async def proxy_image(url: str = Query(..., description="The URL of the image to proxy")):
    target_url = unquote(url)
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                target_url, 
                follow_redirects=True,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
            )
            if resp.status_code == 200:
                # Remove CORS limit headers if they exist from the remote
                headers = dict(resp.headers)
                headers.pop("cross-origin-resource-policy", None)
                headers.pop("content-security-policy", None)

                return Response(
                    content=resp.content,
                    status_code=200,
                    media_type=resp.headers.get("content-type", "image/png"),
                    headers={"Cross-Origin-Resource-Policy": "cross-origin"} # Explicitly allow cross-origin loads for webmail
                )
            else:
                logger.warning(f"Proxy failed for {target_url} with status {resp.status_code}")
                return Response(status_code=404, content=b"")
    except Exception as e:
        logger.error(f"Proxy exception for {target_url}: {e}")
        # Ignore external broken links
        return Response(status_code=404, content=b"")
