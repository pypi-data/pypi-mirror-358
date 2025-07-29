from functools import partial

import pytest
from rich import print as rprint

from wujing.llm.oai_client import llm_call


@pytest.mark.skip()
def test_llm_call(api_key, api_base, model, messages, response_model, context, guided_backend):
    resp = llm_call(
        api_key=api_key,
        api_base=api_base,
        model=model,
        messages=messages,
        response_model=response_model,
        context=context,
        guided_backend=guided_backend,
        cache_enabled=False,
    )

    rprint(f"{type(resp)=}, {resp=}")


def test_max_tokens(api_key, api_base, model, messages, response_model, context, guided_backend):
    resp = llm_call(
        max_tokens=4096,
        api_key=api_key,
        api_base=api_base,
        cache_enabled=False,
        messages=messages,
        model=model,
    )

    rprint(f"{type(resp)=}, {resp=}")


def test_max_tokens_with_partial(api_key, api_base, model, messages, response_model, context, guided_backend):
    req_with_oai = partial(
        llm_call,
        max_tokens=4096,
        api_key=api_key,
        api_base=api_base,
        cache_enabled=False,
        model=model,
    )

    rprint(
        req_with_oai(
            messages=messages,
            model=model,
        )
    )
