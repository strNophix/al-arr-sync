import typing

AnyDict = typing.Dict[typing.Any, typing.Any]


class DlAutomator(typing.Protocol):

    def lookup_series(self, query: str) -> typing.List[AnyDict]:
        ...

    def add_series(self, *series: AnyDict):
        ...


class MediaTracker(typing.Protocol):

    def currently_watching(self, username: str) -> typing.List[AnyDict]:
        ...
