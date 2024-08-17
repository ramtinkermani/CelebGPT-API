import json
import logging
from openai import OpenAI
from starlette.responses import JSONResponse
from starlette.websockets import WebSocket, WebSocketState

from helpers import extract_json_from_markdown


class OpenAIClient():
    def __init__(self, model="gpt-4o", temperature=0):
        self.model = model
        self.temperature = temperature

    async def gptAskStream(self, message):
        client = OpenAI()
        message = json.loads(message)
        question = message['question']
        jsonOutput = message['jsonOutput']

        stream = client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content":
                        f"""You will be asked a question. Do not make up answers if you don't know it. 
                            Say 'I don't have an answer for that' if you don't know. 
                            {"Respond only in JSON." if jsonOutput else ""}"""},
                {"role": "user", "content": question}
            ],
            stream=True,
            temperature=self.temperature
        )
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                print(chunk.choices[0].delta.content, end="")
                yield chunk.choices[0].delta.content

    def gptAsk(self, message, schema='{}'):
        client = OpenAI()
        question = message['question']
        jsonOutput = message['jsonOutput']

        result = client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content":
                        f"""You will be asked a question. Do not make up answers if you don't know it. 
                            Say 'I don't have an answer for that' if you don't know. 
                            {f"Respond only in JSON with this schema: ```{schema}```." if jsonOutput else ""}"""},
                {"role": "user", "content": question}
            ],
            stream=False,
            temperature=self.temperature
        )

        if result.choices[0].message.content is not None:
            return result.choices[0].message.content


class OpenAIEndpoints:
    @staticmethod
    async def askgpt(request):
        payload = await request.json()
        openai_client = OpenAIClient()
        result = await openai_client.gptAsk(payload)
        if payload['jsonOutput']:
            jsonResult = json.loads(extract_json_from_markdown(result))
            return JSONResponse(jsonResult, 200)
        return JSONResponse({"result": result}, 200)

    @staticmethod
    async def askGptStream(websocket: WebSocket):
        await websocket.accept()
        try:
            message = await websocket.receive_text()
            openai_client = OpenAIClient()
            async for message in openai_client.gptAskStream(message):
                await websocket.send_text(message)
        except Exception as e:
            logging.error(f"Error in WebSocket connection: {e}")
        finally:
            if not websocket.client_state == WebSocketState.DISCONNECTED:
                await websocket.close()
