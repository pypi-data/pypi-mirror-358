from __future__ import annotations

from asyncio import ensure_future, iscoroutinefunction
from functools import wraps
from http import HTTPStatus
from inspect import isawaitable
from typing import TYPE_CHECKING, Any, overload

from graphql import ExecutionContext, ExecutionResult, GraphQLError, execute, is_non_null_type, parse, validate

from undine.exceptions import (
    GraphQLAsyncNotSupportedError,
    GraphQLErrorGroup,
    GraphQLNoExecutionResultError,
    GraphQLUnexpectedError,
)
from undine.hooks import LifecycleHookContext, use_lifecycle_hooks
from undine.settings import undine_settings
from undine.utils.graphql.utils import validate_get_request_operation
from undine.utils.graphql.validation_rules import get_validation_rules

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from graphql import GraphQLOutputType
    from graphql.pyutils import AwaitableOrValue

    from undine.dataclasses import GraphQLHttpParams
    from undine.typing import DjangoRequestProtocol, P

__all__ = [
    "execute_graphql_async",
    "execute_graphql_sync",
]


class UndineExecutionContext(ExecutionContext):
    """Custom GraphQL execution context class."""

    def handle_field_error(self, error: GraphQLError, return_type: GraphQLOutputType) -> None:
        if not isinstance(error.original_error, GraphQLErrorGroup):
            return super().handle_field_error(error, return_type)

        error.original_error.located_by(error)

        if is_non_null_type(return_type):
            raise error.original_error

        for err in error.original_error.flatten():
            self.handle_field_error(err, return_type)

        return None

    @staticmethod
    def build_response(data: dict[str, Any] | None, errors: list[GraphQLError]) -> ExecutionResult:
        for error in errors:
            error.extensions.setdefault("status_code", HTTPStatus.BAD_REQUEST)  # type: ignore[union-attr]
        return ExecutionContext.build_response(data, errors)


@overload
def raised_exceptions_as_execution_results(
    func: Callable[P, ExecutionResult],
) -> Callable[P, ExecutionResult]: ...


@overload
def raised_exceptions_as_execution_results(
    func: Callable[P, Awaitable[ExecutionResult]],
) -> Callable[P, Awaitable[ExecutionResult]]: ...


def raised_exceptions_as_execution_results(
    func: Callable[P, AwaitableOrValue[ExecutionResult]],
) -> Callable[P, AwaitableOrValue[ExecutionResult]]:
    """Wraps raised exceptions as GraphQL ExecutionResults if they happen in `execute_graphql`."""
    if iscoroutinefunction(func):

        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> ExecutionResult:
            try:
                return await func(*args, **kwargs)

            except GraphQLError as error:
                return ExecutionResult(errors=[error])

            except GraphQLErrorGroup as error:
                return ExecutionResult(errors=list(error.flatten()))

            except Exception as error:  # noqa: BLE001
                return ExecutionResult(errors=[GraphQLUnexpectedError(message=str(error))])

    else:

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> ExecutionResult:
            try:
                return func(*args, **kwargs)  # type: ignore[return-value]

            except GraphQLError as error:
                return ExecutionResult(errors=[error])

            except GraphQLErrorGroup as error:
                return ExecutionResult(errors=list(error.flatten()))

            except Exception as error:  # noqa: BLE001
                return ExecutionResult(errors=[GraphQLUnexpectedError(message=str(error))])

    return wrapper


@raised_exceptions_as_execution_results
def execute_graphql_sync(params: GraphQLHttpParams, request: DjangoRequestProtocol) -> ExecutionResult:
    """
    Executes a GraphQL query received from an HTTP request synchronously.
    Assumes that the schema has been validated (e.g. created using `undine.schema.create_schema`).

    :param params: GraphQL request parameters.
    :param request: The Django request object to use as the GraphQL execution context value.
    """
    context = LifecycleHookContext.from_graphql_params(params=params, request=request)

    _run_operation(context)
    if context.result is None:  # pragma: no cover
        raise GraphQLNoExecutionResultError

    if isawaitable(context.result):
        ensure_future(context.result).cancel()
        raise GraphQLAsyncNotSupportedError

    return context.result


@raised_exceptions_as_execution_results
async def execute_graphql_async(params: GraphQLHttpParams, request: DjangoRequestProtocol) -> ExecutionResult:
    """
    Executes a GraphQL query received from an HTTP request asynchronously.
    Assumes that the schema has been validated (e.g. created using `undine.schema.create_schema`).

    :param params: GraphQL request parameters.
    :param request: The Django request object to use as the GraphQL execution context value.
    """
    context = LifecycleHookContext.from_graphql_params(params=params, request=request)

    _run_operation(context)
    if context.result is None:  # pragma: no cover
        raise GraphQLNoExecutionResultError

    if isawaitable(context.result):
        return await context.result

    return context.result


@use_lifecycle_hooks(hooks=undine_settings.OPERATION_HOOKS)
def _run_operation(context: LifecycleHookContext) -> None:
    _parse_source(context)
    if context.result is not None:
        return

    _validate_document(context)
    if context.result is not None:
        return

    _execute_request(context)


@use_lifecycle_hooks(hooks=undine_settings.PARSE_HOOKS)
def _parse_source(context: LifecycleHookContext) -> None:
    if context.document is not None:
        return

    context.document = parse(
        source=context.source,
        no_location=undine_settings.NO_ERROR_LOCATION,
        max_tokens=undine_settings.MAX_TOKENS,
    )


@use_lifecycle_hooks(hooks=undine_settings.VALIDATION_HOOKS)
def _validate_document(context: LifecycleHookContext) -> None:
    if context.request.method == "GET":
        validate_get_request_operation(
            document=context.document,  # type: ignore[arg-type]
            operation_name=context.operation_name,
        )

    validation_errors = validate(
        schema=undine_settings.SCHEMA,
        document_ast=context.document,  # type: ignore[arg-type]
        rules=get_validation_rules(),
        max_errors=undine_settings.MAX_ERRORS,
    )
    if validation_errors:
        context.result = ExecutionResult(errors=validation_errors)


@use_lifecycle_hooks(hooks=undine_settings.EXECUTION_HOOKS)
def _execute_request(context: LifecycleHookContext) -> None:
    context.result = execute(
        schema=undine_settings.SCHEMA,
        document=context.document,  # type: ignore[arg-type]
        root_value=undine_settings.ROOT_VALUE,
        context_value=context.request,
        variable_values=context.variables,
        operation_name=context.operation_name,
        middleware=undine_settings.MIDDLEWARE,
        execution_context_class=undine_settings.EXECUTION_CONTEXT_CLASS,
    )
