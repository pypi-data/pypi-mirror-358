import inspect
import re
import sys
from datetime import date, datetime, time, timedelta
from typing import Any, Dict, List, Optional, Sequence, Union

import click
import click.shell_completion

if sys.version_info < (3, 9):
    try:
        from backports import zoneinfo
    except ImportError:
        zoneinfo = None  # type: ignore
else:
    import zoneinfo

try:
    import pytz
except ImportError:
    pytz = None  # type: ignore


class Date(click.DateTime):
    name = "date"

    def __init__(self, formats: Optional[Sequence[str]] = None):
        super().__init__(formats or ["%Y-%m-%d"])

    def _try_to_convert_date(self, value: Any, format: str) -> Optional[date]:  # type: ignore[override]
        try:
            return datetime.strptime(value, format).date()
        except ValueError:
            return None

    def __repr__(self) -> str:
        return "Date"


class Time(click.DateTime):
    name = "time"

    def __init__(self, formats: Optional[Sequence[str]] = None):
        super().__init__(formats or ["%H:%M", "%H:%M:%S"])

    def _try_to_convert_date(self, value: Any, format: str) -> Optional[time]:  # type: ignore[override]
        try:
            return datetime.strptime(value, format).time()
        except ValueError:
            return None

    def __repr__(self) -> str:
        return "Time"


class ZoneInfo(click.ParamType):
    name = "timezone"

    def to_info_dict(self) -> Dict[str, Any]:
        info_dict = super().to_info_dict()
        info_dict["available_timezones"] = zoneinfo.available_timezones()
        return info_dict

    def convert(
        self,
        value: Any,
        param: Optional[click.Parameter],
        ctx: Optional[click.Context],
    ) -> Any:
        if isinstance(value, zoneinfo.ZoneInfo):
            return value
        try:
            return zoneinfo.ZoneInfo(value)
        except zoneinfo.ZoneInfoNotFoundError:
            self.fail(f"Unknown timezone {value}", param, ctx)

    def __repr__(self) -> str:
        return "ZoneInfo"


class PytzTimezone(click.ParamType):
    name = "timezone"

    def to_info_dict(self) -> Dict[str, Any]:
        info_dict = super().to_info_dict()
        info_dict["available_timezones"] = list(pytz.all_timezones)
        return info_dict

    def convert(
        self,
        value: Any,
        param: Optional[click.Parameter],
        ctx: Optional[click.Context],
    ) -> Any:
        if isinstance(value, pytz.BaseTzInfo):
            return value
        try:
            return pytz.timezone(value)
        except pytz.UnknownTimeZoneError:
            try:
                offset = int(value)
            except ValueError:
                self.fail(f"Unknown timezone or bad offset: {value}", param, ctx)
            else:
                return pytz.FixedOffset(offset)

    def __repr__(self) -> str:
        return "PytzTimezone"


class TimeDelta(click.ParamType):
    name = "timedelta"

    def convert(
        self,
        value: Any,
        param: Optional[click.Parameter],
        ctx: Optional[click.Context],
    ) -> Any:
        if isinstance(value, timedelta):
            return value
        if not isinstance(value, str) or not value.strip():
            self.fail(str(value), param, ctx)

        # Handle Python serialisation
        if ":" in value:
            if ", " in value:
                days_and_text, hours_minutes_seconds = value.split(", ")
                days, text = days_and_text.split(" ")
                if text not in ("day", "days"):
                    self.fail(str(text), param, ctx)
            else:
                days = "0"
                hours_minutes_seconds = value
            try:
                hours, minutes, seconds = hours_minutes_seconds.split(":")
            except ValueError:
                self.fail(f"expected HH:MM:SS in {value!r}", param, ctx)
            if "." in seconds:
                seconds, microseconds = seconds.split(".")
            else:
                microseconds = "000000"
            return timedelta(
                days=int(days),
                hours=int(hours),
                minutes=int(minutes),
                seconds=int(seconds),
                microseconds=int(microseconds),
            )

        # Handle human-friendly serialisation
        possible_names = {
            "weeks": "weeks",
            "week": "weeks",
            "w": "weeks",
            "days": "days",
            "day": "days",
            "d": "days",
            "hours": "hours",
            "hour": "hours",
            "hrs": "hours",
            "hr": "hours",
            "h": "hours",
            "minutes": "minutes",
            "minute": "minutes",
            "mins": "minutes",
            "min": "minutes",
            "m": "minutes",
            "seconds": "seconds",
            "second": "seconds",
            "secs": "seconds",
            "sec": "seconds",
            "s": "seconds",
            "microseconds": "microseconds",
            "microsecond": "microseconds",
            "us": "microseconds",
            "milliseconds": "milliseconds",
            "millisecond": "milliseconds",
            "ms": "millisecond",
        }
        kwargs = {}
        parts = [
            x.group() for x in re.finditer(r"([+-]?\d+)|[a-zA-Z, ]+", value.strip())
        ]
        if len(parts) % 2 == 1:
            self.fail(f"{value} is not a sequence of value-unit pairs", param, ctx)
        for part_str_value, part_name in zip(parts[::2], parts[1::2]):
            part_value: Union[int, float]
            try:
                part_value = int(part_str_value)
            except ValueError:
                try:
                    part_value = float(part_str_value)
                except ValueError:
                    self.fail(
                        f"{part_str_value!r} in {value!r} is not a number", param, ctx
                    )
            clean_name = part_name.lower().strip(", ")
            if clean_name not in possible_names:
                self.fail(
                    f"{clean_name!r} in {value!r} is not a valid unit", param, ctx
                )
            kwarg = possible_names[clean_name]
            if kwarg in kwargs:
                self.fail(f"{kwarg} in {value!r} are given more than once", param, ctx)
            kwargs[kwarg] = part_value
        return timedelta(**kwargs)

    def __repr__(self) -> str:
        return "TimeDelta"


class OrParam(click.ParamType):
    def __init__(self, param_types: Sequence[click.ParamType]):
        self.param_types = param_types
        self.name = "_or_".join(param_type.name for param_type in self.param_types)

    def to_info_dict(self) -> Dict[str, Any]:
        return {
            param_type.name: param_type.to_info_dict()
            for param_type in self.param_types
        }

    def convert(
        self,
        value: Any,
        param: Optional[click.Parameter],
        ctx: Optional[click.Context],
    ) -> Any:
        errors = []
        for param_type in self.param_types:
            try:
                return param_type.convert(value, param, ctx)
            except click.BadParameter as e:
                errors.append(e.message.rstrip("."))
        errors_str = "; ".join(errors)
        self.fail(f"No conversions succeeded: {errors_str}.", param, ctx)

    def get_metavar(
        self,
        param: click.Parameter,
        ctx: Optional[click.Context] = None,
    ) -> Optional[str]:
        metavars = []
        for param_type in self.param_types:
            if "ctx" in inspect.signature(param_type.get_metavar).parameters:
                # Click >= 8.2
                assert ctx is not None
                metavars.append(param_type.get_metavar(param, ctx))
            else:
                # Click < 8.2
                metavars.append(param_type.get_metavar(param))  # type: ignore[call-arg]
        return "|".join(
            metavar or param_type.name.upper()
            for metavar, param_type in zip(metavars, self.param_types)
        )

    def shell_complete(
        self,
        ctx: click.Context,
        param: click.Parameter,
        incomplete: str,
    ) -> List[click.shell_completion.CompletionItem]:
        completions = [
            param_type.shell_complete(ctx, param, incomplete)
            for param_type in self.param_types
        ]
        if not incomplete and not all(completions):
            return []
        return [item for items in completions for item in items]

    def __repr__(self) -> str:
        return "_OR_".join(repr(param_type) for param_type in self.param_types)
