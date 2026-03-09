import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY") or os.getenv("TMBD_API_KEY")
TMDB_BASE = "https://api.themoviedb.org/3"

async def tmdb_get(path: str, params: dict):
    q = dict(params)
    q["api_key"] = TMDB_API_KEY
    try:
        transport = httpx.AsyncHTTPTransport(retries=3)
        async with httpx.AsyncClient(transport=transport, timeout=20, verify=False, limits=httpx.Limits(max_keepalive_connections=5, max_connections=20)) as client:
            print(f"GET {TMDB_BASE}{path} with {q}")
            r = await client.get(f"{TMDB_BASE}{path}", params=q)
            print("Status:", r.status_code)
            return r.json()
    except Exception as e:
        print("ERROR:", type(e), e)

async def main():
    await tmdb_get("/search/movie", {
        "query": "Avengers",
        "include_adult": "false",
        "language": "en-US",
        "page": 1,
    })
    await tmdb_get("/trending/movie/day", {"language": "en-US"})

if __name__ == "__main__":
    asyncio.run(main())
