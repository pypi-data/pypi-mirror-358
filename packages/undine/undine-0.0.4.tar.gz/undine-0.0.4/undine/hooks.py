from __future__ import annotations

import dataclasses
from abc import ABC, abstractmethod
from collections.abc import Callable
from contextlib import ExitStack, contextmanager
from functools import wraps
from typing import TYPE_CHECKING, Any, Self, TypeVar

from graphql import ExecutionResult, GraphQLError

if TYPE_CHECKING:
    from collections.abc import Generator

    from graphql import DocumentNode
    from graphql.pyutils import AwaitableOrValue

    from undine.dataclasses import GraphQLHttpParams
    from undine.typing import DjangoRequestProtocol

__all__ = [
    "LifecycleHook",
    "LifecycleHookContext",
    "LifecycleHookManager",
    "use_lifecycle_hooks",
]


@dataclasses.dataclass(slots=True, kw_only=True)
class LifecycleHookContext:
    """Context passed to a lifecycle hook."""

    source: str
    """Source GraphQL document string."""

    document: DocumentNode | None
    """Parsed GraphQL document AST. Available after parsing is complete."""

    variables: dict[str, Any]
    """Variables passed to the GraphQL operation."""

    operation_name: str | None
    """Name of the GraphQL operation."""

    extensions: dict[str, Any]
    """GraphQL operation extensions received from the client."""

    request: DjangoRequestProtocol
    """Django request during which the GraphQL request is being executed."""

    result: AwaitableOrValue[ExecutionResult] | None
    """Execution result of the GraphQL operation. Adding a result here will cause an early exit."""

    @classmethod
    def from_graphql_params(cls, params: GraphQLHttpParams, request: DjangoRequestProtocol) -> Self:
        return cls(
            source=params.document,
            document=None,
            variables=params.variables,
            operation_name=params.operation_name,
            extensions=params.extensions,
            request=request,
            result=None,
        )


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class LifecycleHook(ABC):
    """Base class for lifecycle hooks."""

    context: LifecycleHookContext

    @contextmanager
    def use(self) -> Generator[None, None, None]:
        yield from self.run()

    @abstractmethod
    def run(self) -> Generator[None, None, None]:
        """
        Override this method to define how the hook should be executed.
        Anything before the yield statement will be executed before the hooking point.
        Anything after the yield statement will be executed after the hooking point.
        """
        yield


TLifecycleHook = TypeVar("TLifecycleHook", bound=LifecycleHook)


class LifecycleHookManager(ExitStack):
    """Executes multiple lifecycle hooks at once."""

    def __init__(self, *, hooks: list[type[TLifecycleHook]], context: LifecycleHookContext) -> None:
        self.hooks: list[TLifecycleHook] = [hook(context=context) for hook in hooks]
        super().__init__()

    def __enter__(self) -> Self:
        for hook in self.hooks:
            self.enter_context(hook.use())
        return super().__enter__()


Hookable = Callable[[LifecycleHookContext], None]


def use_lifecycle_hooks(hooks: list[type[TLifecycleHook]]) -> Callable[[Hookable], Hookable]:
    """Run given function using the given lifecycle hooks."""

    def decorator(func: Hookable) -> Hookable:
        @wraps(func)
        def wrapper(context: LifecycleHookContext) -> None:
            with LifecycleHookManager(hooks=hooks, context=context):
                if context.result is not None:
                    return

                try:
                    func(context)
                except GraphQLError as error:
                    context.result = ExecutionResult(errors=[error])
                    return

        return wrapper

    return decorator
