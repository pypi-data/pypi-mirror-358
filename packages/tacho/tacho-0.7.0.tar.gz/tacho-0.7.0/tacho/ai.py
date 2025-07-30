import time

import litellm

BENCHMARK_PROMPT = """Generate a ~2000 word summary of the history of the USA."""
VALIDATION_PROMPT = "Do you have time to help? (yes/no)"


async def llm(model: str, prompt: str, tokens: int | None = None):
    messages = [{"role": "user", "content": prompt}]
    return await litellm.acompletion(model, messages, max_tokens=tokens)


async def ping_model(model: str, console) -> bool:
    try:
        await llm(model, VALIDATION_PROMPT, 1)
        console.print(f"[green]✓[/green] {model}")
        return True
    except Exception as e:
        console.print(f"[red]✗[/red] {model} - {str(e)}")
        return False


async def bench_model(model: str, max_tokens: int) -> tuple[float, int]:
    """Measure inference time for a single run and return time and tokens"""
    start_time = time.time()
    res = await llm(model, BENCHMARK_PROMPT, max_tokens)
    duration = time.time() - start_time

    tokens = res.usage.completion_tokens
    if (
        hasattr(res.usage, "completion_tokens_details")
        and res.usage.completion_tokens_details
    ):
        if hasattr(res.usage.completion_tokens_details, "reasoning_tokens"):
            tokens += res.usage.completion_tokens_details.reasoning_tokens

    return duration, tokens
