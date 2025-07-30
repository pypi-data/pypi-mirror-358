import aiohttp
from .exceptions import EOLTrackerAPIError
from typing import List, Dict

class EOLClient:
    def __init__(self, session):
        self._session = session

    async def fetch_release_data(self, uri: str) -> dict:
        try:
            async with self._session.get(uri) as release_resp:
                if release_resp.status != 200:
                    raise EOLTrackerAPIError(
                        f"Failed to fetch release data from {uri}",
                        status_code=release_resp.status,
                        payload={"uri": uri}
                    )
                return (await release_resp.json()).get("result", {})
        except aiohttp.ClientError as e:
            raise EOLTrackerAPIError(
                f"HTTP error while fetching release data: {e}",
                payload={"uri": uri}
            )

    async def fetch_product_data(self, uri: str) -> dict:
        base_uri = "/".join(uri.strip("/").split("/")[:-2])
        try:
            async with self._session.get(base_uri) as product_resp:
                if product_resp.status != 200:
                    raise EOLTrackerAPIError(
                        f"Failed to fetch product data from {base_uri}",
                        status_code=product_resp.status,
                        payload={"uri": base_uri}
                    )
                return (await product_resp.json()).get("result", {})
        except aiohttp.ClientError as e:
            raise EOLTrackerAPIError(
                f"HTTP error while fetching product data: {e}",
                payload={"uri": base_uri}
            )

    async def fetch_all(self, uri: str) -> dict:
        release_data = await self.fetch_release_data(uri)
        product_data = await self.fetch_product_data(uri)
        return {
            "release": release_data,
            "product": product_data
        }

    async def fetch_all_products(self) -> List[dict]:
        uri = "https://endoflife.date/api/v1/products"
        async with self._session.get(uri) as resp:
            if resp.status != 200:
                raise EOLTrackerAPIError(
                    "Failed to fetch products",
                    status_code=resp.status,
                    payload={"uri": uri}
                )

            return (await resp.json()).get("result", [])

    async def fetch_product_versions(self, product_name: str) -> Dict[str, str]:
        uri = f"https://endoflife.date/api/v1/products/{product_name}"
        async with self._session.get(uri) as resp:
            if resp.status != 200:
                raise EOLTrackerAPIError(
                    f"Failed to fetch product versions for {product_name}",
                    status_code=resp.status,
                    payload={"uri": uri}
                )
            data = await resp.json()
            releases = data.get("result", {}).get("releases", [])
            return {
                release.get("label"): release.get("name")
                for release in releases if release.get("label") and release.get("name")
            }

    async def close(self):
        await self._session.close()