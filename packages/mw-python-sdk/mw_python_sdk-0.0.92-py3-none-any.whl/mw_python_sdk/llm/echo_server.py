import asyncio
import time

from fastapi import FastAPI
from starlette.responses import StreamingResponse

from mw_python_sdk.llm.model import (
    CreateChatCompletionRequest,
    ChatCompletionResponseMessage,
    CreateChatCompletionResponse,
    CreateChatCompletionStreamResponse,
    Choice3,  # for stream completion  message
    Choice1,  # for chat completion message
    FinishReason1,
    Object2,
    Object5,
    Role6,
    Role2,
    ServiceTier1,
    Logprobs2,
    TopLogprob,
    ChatCompletionTokenLogprob,
    ChatCompletionStreamResponseDelta,
    CompletionUsage,
)

app = FastAPI(title="OpenAI-compatible API")


def now() -> int:
    # ts stores the time in seconds
    ts = time.time()
    # print the current timestamp
    return int(ts)


async def _resp_async_generator(text_resp: str):
    # let's pretend every word is a token and return it over time
    tokens = text_resp.split(" ")
    for i, token in enumerate(tokens):
        chunk = CreateChatCompletionStreamResponse(
            id="12345",
            model="blah",
            choices=[
                Choice3(
                    index=i,
                    delta=ChatCompletionStreamResponseDelta(
                        role=Role6.assistant,
                        content=token + "",
                        function_call=None,
                        refusal="",
                    ),
                    logprobs=Logprobs2(content=[], refusal=[]),
                    finish_reason=FinishReason1.stop,
                )
            ],
            system_fingerprint="fp_44709d6fcb",  # this is a fake system finterprint
            created=now(),
            object=Object5.chat_completion_chunk,
            service_tier=ServiceTier1.default,
            usage=None,
        )
        yield f"data: {chunk.model_dump_json(exclude_unset=True)}\n\n"
        await asyncio.sleep(0.001)
    final_chunk = CreateChatCompletionStreamResponse(
        id="12345",
        model="blah",
        choices=[
            Choice3(
                index=1,
                delta=ChatCompletionStreamResponseDelta(
                    role=Role6.assistant,
                    content="",
                    function_call=None,
                    refusal="",
                ),
                logprobs=Logprobs2(content=[], refusal=[]),
                finish_reason=FinishReason1.stop,
            )
        ],
        system_fingerprint="fp_44709d6fcb",  # this is a fake system finterprint
        created=now(),
        object=Object5.chat_completion_chunk,
        service_tier=ServiceTier1.default,
        usage=CompletionUsage(
            prompt_tokens=100, completion_tokens=100, total_tokens=200
        ),
    )
    yield f"data: {final_chunk.model_dump_json(exclude_unset=True)}\n\n"
    yield "data: [DONE]\n\n"


@app.post("/v1/chat/completions")
async def chat_completions(request: CreateChatCompletionRequest):
    if request.messages:
        resp_content = (
            "As a mock AI Assitant, I can only echo your last message:"
            + request.messages[0].root.content
        )
    else:
        resp_content = "As a mock AI Assitant, I can only echo your last message, but there were no messages!"
    if request.stream:
        return StreamingResponse(
            _resp_async_generator(resp_content), media_type="application/x-ndjson"
        )
    return CreateChatCompletionResponse(
        id="12345",
        model=str(request.model),
        choices=[
            Choice1(
                index=0,
                message=ChatCompletionResponseMessage(
                    role=Role2.assistant,
                    content=resp_content,
                    refusal="",
                    function_call=None,
                ),
                logprobs=Logprobs2(
                    content=[
                        ChatCompletionTokenLogprob(
                            token="As",
                            logprob=-0.1,
                            bytes=[2],
                            top_logprobs=[
                                TopLogprob(token="As", logprob=-0.1, bytes=[2])
                            ],
                        )
                    ],
                    refusal=[],
                ),
                finish_reason=FinishReason1.length,
            )
        ],
        object=Object2.chat_completion,
        service_tier=ServiceTier1.default,
        created=now(),
        system_fingerprint="fp_44709d6fcb",
        usage=CompletionUsage(
            prompt_tokens=100, completion_tokens=100, total_tokens=200
        ),
    )
