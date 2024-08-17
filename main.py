import json
import logging

import uvicorn
from starlette.responses import JSONResponse
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Route, WebSocketRoute

from Clients.OpenAIClient import OpenAIClient, OpenAIEndpoints
from Clients.RedisClient import RedisEndpoints, RedisClient
from Clients.SerpapiClient import SerpapiClient
from Schemas.SchemaHelpers import get_entity_class_schema, get_root_class_type
from helpers import extract_json_from_markdown


async def health(request):
    return JSONResponse({"message": "API is running ...."}, 200)


async def get_entity_data(request):
    payload = await request.json()
    entity_name_query = payload['question']

    entity_info = get_root_class_type(entity_name_query)
    if not entity_info['entity_class_name']:
        return JSONResponse({"Message": "Error: Not a well-known Entity nor a Celebrity"}, 404)

    # If we have valid cache data for this search, return that
    redis_client = RedisClient()
    cached_entity = await redis_client.getItem(key=entity_info['entity_name'])

    if cached_entity:
        cached_value = cached_entity['value']
        json_value = json.loads(cached_value)
        return JSONResponse(json_value, 200)

    # If not in cache, continue
    entity_class_schema = get_entity_class_schema(entity_info['entity_class_name'])

    openai_client = OpenAIClient()
    result = openai_client.gptAsk(
                                {'question': entity_info['entity_name'], 'jsonOutput': True},
                                str(entity_class_schema))

    json_string_result = extract_json_from_markdown(result)
    json_result = json.loads(json_string_result)

    # Retrieve and include entity image URLs
    sc = SerpapiClient()
    image_urls = await sc.get_entity_image(entity_info['entity_name'])
    json_result['image_urls'] = image_urls

    await redis_client.setItem(entity_info['entity_name'], json_result)

    return JSONResponse(json_result, 200)


middleware = [
    Middleware(CORSMiddleware, allow_origins=['http://localhost:5173'],
                               allow_methods=['*'],
                               allow_headers=['*'])
]

app = Starlette(debug=True, routes=[
    # REST endpoints
    Route('/', health),
    Route('/redis', RedisEndpoints.redis_get, methods=['GET']),
    Route('/redis', RedisEndpoints.redis_set, methods=['POST']),
    Route('/askgpt', OpenAIEndpoints.askgpt, methods=['POST']),
    Route('/entitydata', get_entity_data, methods=['POST']),

    # Websocket Endpoints
    WebSocketRoute('/askgptstream', OpenAIEndpoints.askGptStream)
], middleware=middleware)


if __name__ == '__main__':

    logging.info("STARTING CelebGPT SERVICE ...")
    uvicorn.run("main:app",  host="0.0.0.0", port=5000, log_level="warning",
                reload=True)