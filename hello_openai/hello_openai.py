import openai
import asyncio
import dotenv
import os
import sys

from openai.types.chat.chat_completion_user_message_param import (
    ChatCompletionUserMessageParam,
)
from typing import List, Optional, ClassVar
from openai.types.chat.chat_completion import ChatCompletion, Choice
import time
import uvicorn
import uvloop


class Chatter:
    def __init__(self) -> None:
        dotenv.load_dotenv()
        key: str = os.getenv("OPENAI_API_KEYS", "")
        self.client: openai.AsyncOpenAI = openai.AsyncOpenAI(
            api_key=key,
        )

    async def get_openai_response(self) -> str:
        # Define the messages for a conversation
        msg: List[ChatCompletionUserMessageParam] = [
            ChatCompletionUserMessageParam(
                content="What is the capital of France?", role="user"
            )
        ]

        response: ChatCompletion = await self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=msg,
            max_tokens=10,
        )

        # print("Assistant's response:", response)

        choice: Choice = response.choices[0]
        content: Optional[str] = choice.message.content
        result: str = ""
        if content:
            result = content

        return result


class Client:
    client: ClassVar[Chatter] = Chatter()


async def app(scope, receive, send):
    # assert scope["type"] == "http"
    # path: str = scope.get("path", "/")
    status: int = 200
    result: str = "ok"
    try:
        result = await Client.client.get_openai_response()
    except Exception as e:
        status = 500
        result = str(e)

    await send(
        {
            "type": "http.response.start",
            "status": status,
            "headers": [
                [b"content-type", b"text/plain"],
            ],
        }
    )
    await send(
        {
            "type": "http.response.body",
            "body": result.encode(),
        }
    )


def run():
    chatter: Chatter = Chatter()
    n: int = 10
    start: int = time.time_ns()
    for _ in range(n):
        s: str = asyncio.run(chatter.get_openai_response())
        print(s)

    took: float = (time.time_ns() - start) / 1000000000
    reqs: float = float(n) / took
    print(f"Took {took:.2f} s {reqs:.2f} req/s")


def start_uvicorn():
    # Call the model and print the result
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    uvicorn.run(
        "hello_openai:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="error",
    )


if __name__ == "__main__":
    if len(sys.argv) > 1:
        mode: str = sys.argv[1]
        if mode == "uvicorn":
            start_uvicorn()
        else:
            run()
    else:
        run()
