from collections import Counter
from collections.abc import Awaitable, Callable, Iterable
from decimal import Decimal
from inspect import Signature, signature
from statistics import mean
from typing import Any, cast


# Name it in this way to mimic as a function
class lazy_call[T: Any]:  # noqa: N801
    __DEFAULT_OBJECT = object()

    def __init__(
        self,
        func: Callable[..., T],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.__func = func
        self.__args = args
        self.__kwargs = kwargs

        self.__object: object | T = self.__DEFAULT_OBJECT

    def __call__(self) -> T:
        if self.__object == self.__DEFAULT_OBJECT:
            self.__object = self.__func(*self.__args, **self.__kwargs)

        return cast("T", self.__object)


# Name it in this way to mimic as a function
class multi_call[T: Any]:  # noqa: N801
    def __init__(
        self,
        times: int,
        agg_func: Callable[[Iterable[T]], T],
    ) -> None:
        self.__times = times
        self.__agg_func = agg_func

    def __call__(
        self,
        func: Callable[..., T],
        *args: Any,
        **kwargs: Any,
    ) -> T:
        results = (
            func(*args, **kwargs)
            for i in range(self.__times)
        )

        return self.__agg_func(results)


# Name it in this way to mimic as a function
class multi_call_for_average[T: int | float | Decimal](multi_call[T]):  # noqa: N801
    def __init__(
        self,
        times: int,
    ) -> None:
        super().__init__(
            times,
            mean,
        )


# Name it in this way to mimic as a function
class multi_call_for_most_common[T: Any](multi_call[T]):  # noqa: N801
    def __init__(
        self,
        times: int,
    ) -> None:
        def most_commmon(results: Iterable[T]) -> T:
            return Counter(results).most_common(1)[0][0]

        super().__init__(
            times,
            most_commmon,
        )


class Intercept[T: Any]:
    def __init__(
        self,
        replacement: Callable[[dict[str, Any]], T],
    ) -> None:
        self.__replacement = replacement

    def __call__[**P](self, f: Callable[P, T]) -> Callable[P, T]:
        sig: Signature = signature(f)

        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            return self.__replacement(
                sig.bind(*args, **kwargs).arguments,
            )

        return wrapper


class InterceptAsync[T: Any]:
    def __init__(
        self,
        replacement: Callable[[dict[str, Any]], Awaitable[T]],
    ) -> None:
        self.__replacement = replacement

    def __call__[**P](self, f: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        sig: Signature = signature(f)

        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            return await self.__replacement(
                sig.bind(*args, **kwargs).arguments,
            )

        return wrapper
