import asyncio
import html2text
import json
import time
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from DrissionPage import ChromiumPage
from DrissionPage.common import Keys

app = FastAPI()


def html_to_markdown(html_content):
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = False
    return h.handle(html_content)


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]
    stream: bool
    model: str
    temperature: float
    presence_penalty: float
    frequency_penalty: float
    top_p: float


def format_chat_messages(messages):
    formatted_messages = []
    for msg in messages:
        if msg.role == "system":
            formatted_messages.append(f"System: {msg.content}")
        elif msg.role == "user":
            formatted_messages.append(f"Human: {msg.content}")
        elif msg.role == "assistant":
            formatted_messages.append(f"Assistant: {msg.content}")
    return "\n\n".join(formatted_messages)


async def chat_stream(request: ChatRequest):
    page = ChromiumPage()
    page.get('https://lambda.chat/chatui/')

    text_areas = page.eles('tag:textarea')

    page.listen.start('https://lambda.chat/chatui/conversation')

    if text_areas:
        text_areas[0].click()
        formatted_messages = format_chat_messages(request.messages)
        text_areas[0].input(formatted_messages)
        text_areas[0].input(Keys.ENTER)
    else:
        yield "data: " + json.dumps({"error": "没有找到textarea"}) + "\n\n"
        return

    total_markdown = ''
    start_time = time.time()
    message_id = f"chatcmpl-{int(start_time)}"

    yield "data: " + json.dumps({
        "id": message_id,
        "object": "chat.completion.chunk",
        "created": int(start_time),
        "model": request.model,
        "choices": [{"delta": {"role": "assistant"}, "index": 0}]
    }) + "\n\n"
    await asyncio.sleep(1)
    while True:
        # 检查停止按钮是否可见
        stop_button = page.ele('css:.btn.flex.h-8.rounded-lg.border.bg-white.px-3.py-1.shadow-sm.transition-all', timeout=1)
        if not stop_button or not stop_button.states.is_displayed:
            # 如果停止按钮不可见，说明对话已经结束
            yield "data: " + json.dumps({
                "id": message_id,
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": request.model,
                "choices": [{"delta": {}, "index": 0, "finish_reason": "stop"}]
            }) + "\n\n"
            yield "data: [DONE]\n\n"
            break
        removeImgs = page.eles('css:img[src="https://huggingface.co/avatars/2edb18bd0206c16b433841a47f53fa8e.svg"]')
        if removeImgs:
            for removeImg in removeImgs:
                page.remove_ele(removeImg)
        removeEles = page.eles('css:[title="Copy to clipboard"]')
        if removeEles:
            for removeEle in removeEles:
                page.remove_ele(removeEle)
        elements = page.eles('css:.group.relative.justify-start')
        if elements:
            new_total_html = elements[-1].html
            new_total_markdown = html_to_markdown(new_total_html)

            if new_total_markdown != total_markdown:
                if total_markdown:
                    delta = new_total_markdown[len(total_markdown):]
                else:
                    delta = new_total_markdown

                yield "data: " + json.dumps({
                    "id": message_id,
                    "object": "chat.completion.chunk",
                    "created": int(time.time()),
                    "model": request.model,
                    "choices": [{"delta": {"content": delta}, "index": 0}]
                }) + "\n\n"

                total_markdown = new_total_markdown

        await asyncio.sleep(0.1)


@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest):
    if request.stream:
        return StreamingResponse(chat_stream(request), media_type="text/event-stream")
    else:
        full_response = ""
        async for chunk in chat_stream(request):
            if chunk.startswith("data: "):
                try:
                    data = json.loads(chunk[6:])
                    if "choices" in data and data["choices"] and "delta" in data["choices"][0]:
                        delta = data["choices"][0]["delta"]
                        if "content" in delta:
                            full_response += delta["content"]
                except json.JSONDecodeError:
                    # 如果不是有效的 JSON，跳过这个 chunk
                    continue
            elif chunk.strip() == "data: [DONE]":
                break

        return {
            "id": f"chatcmpl-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": request.model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": full_response
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 0,  # 这里需要实际计算
                "completion_tokens": 0,  # 这里需要实际计算
                "total_tokens": 0  # 这里需要实际计算
            }
        }
@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest):
    if request.stream:
        return StreamingResponse(chat_stream(request), media_type="text/event-stream")
    else:
        full_response = ""
        async for chunk in chat_stream(request):
            if chunk.startswith("data: "):
                try:
                    data = json.loads(chunk[6:])
                    if "choices" in data and data["choices"] and "delta" in data["choices"][0]:
                        delta = data["choices"][0]["delta"]
                        if "content" in delta:
                            full_response += delta["content"]
                except json.JSONDecodeError:
                    # 如果不是有效的 JSON，跳过这个 chunk
                    continue
            elif chunk.strip() == "data: [DONE]":
                break

        return {
            "id": f"chatcmpl-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": request.model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": full_response
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 0,  # 这里需要实际计算
                "completion_tokens": 0,  # 这里需要实际计算
                "total_tokens": 0  # 这里需要实际计算
            }
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
