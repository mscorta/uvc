import openai
import asyncio
import dotenv
import os
from openai.types.chat.chat_completion_user_message_param import (
    ChatCompletionUserMessageParam,
)
from typing import List, Optional
from openai.types.chat.chat_completion import ChatCompletion, Choice
import time


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


def main():
    chatter: Chatter = Chatter()
    n: int = 10
    start: int = time.time_ns()
    for _ in range(n):
        s: str = asyncio.run(chatter.get_openai_response())
        print(s)

    took: float = (time.time_ns() - start) / 1000000000
    reqs: float = float(n) / took
    print(f"Took {took:.2f} s {reqs:.2f} req/s")


if __name__ == "__main__":
    main()
