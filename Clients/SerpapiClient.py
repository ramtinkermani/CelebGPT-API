import os
from serpapi import GoogleSearch

from Clients.RedisClient import RedisClient


class SerpapiClient:
    def __init__(self):
        self.serpapi_api_key = os.environ["SERPAPI_API_KEY"]

    async def get_entity_image(self, entity_to_search, thumbnail=True):
        redis_client = RedisClient()
        cached_image_item = await redis_client.getItem(key=f"SERPAPI.IMAGES.{entity_to_search}")

        if cached_image_item:
            cached_image_url = cached_image_item['value']
            return cached_image_url

        params = {
            "engine": "google_images",
            "q": entity_to_search,
            "api_key": self.serpapi_api_key
        }

        search = GoogleSearch(params)
        results = search.get_dict()

        # Retrieve, Cache and return the top 10 thumbnail images URLS
        image_urls = {"thumbnails": [], "originals": []}
        for i in range(10):
            thumbnail_url = results['images_results'][i]['thumbnail']
            image_urls["thumbnails"].append(thumbnail_url)
            # Also Cache and return the top 10 original image URLS
            original_image_url = results['images_results'][i]['original']
            image_urls["originals"].append(original_image_url)

        expiration_timeout = 1 * 30 * 24 * 3600
        await redis_client.setItem(key=f"SERPAPI.IMAGES.{entity_to_search}", value=image_urls, ex=expiration_timeout)
        return image_urls