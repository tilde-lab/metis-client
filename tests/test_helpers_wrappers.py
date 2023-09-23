"Test method wrappers"

from contextlib import nullcontext

import pytest

from metis_client.exc import MetisError
from metis_client.helpers import raise_on_metis_error, raise_on_metis_error_in_event
from tests.test_helpers_type_guards import (
    IS_METIS_ERROR_DTO_PAMAMS,
    IS_METIS_ERRORS_EVT_DTO_PARAMS,
)


def mk_async_fun(x):
    "Async echo"

    async def run():
        return x

    return run


@pytest.mark.parametrize("x,expected", IS_METIS_ERROR_DTO_PAMAMS)
async def test_helpers_wrapper_raise_on_metis_error(x, expected):
    "Test raise_on_metis_error"

    raises = pytest.raises(MetisError) if expected else nullcontext()

    with raises:
        await raise_on_metis_error(mk_async_fun(x))()


@pytest.mark.parametrize("x,expected", IS_METIS_ERRORS_EVT_DTO_PARAMS)
async def test_helpers_wrapper_raise_on_metis_error_in_event(x, expected):
    "Test raise_on_metis_error_in_event"

    raises = pytest.raises(MetisError) if expected else nullcontext()

    with raises:
        await raise_on_metis_error_in_event(mk_async_fun(x))()
