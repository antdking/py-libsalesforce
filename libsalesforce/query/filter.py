from typing import List, Optional, Any, Callable, TypeVar, Union
import datetime


T = TypeVar('T', bound='FilterBuilder')


def _comparison(operator: str) -> Callable[[T, Any], T]:
    def inner(filter_builder: T, value: Any) -> T:
        # We can only compare when we know what we're comparing against.
        # Also, SOQL does not support comparing a field against another field.
        assert filter_builder.current_attribute, "Can't do a comparison without a field being referenced"

        # If there's more than 1 operation, we should have been doing a join
        assert len(filter_builder.current_operation_stack) < 2, "Already have 2 comparisons in the chain, you should be using AND or OR"

        filter_builder.current_operation_stack.append(
            BinaryOp(operator, filter_builder.current_attribute, value)
        )
        # the current field reference is consumed, so remove it.
        filter_builder.current_attribute = None

        return filter_builder

    return inner


def _join(operator: str) -> Callable[[T, 'BinaryOp'], T]:
    def inner(filter_builder: T, other: 'BinaryOp') -> T:
        # We should have consumed the current field by now
        assert not filter_builder.current_attribute, "Attempting to join while still referencing a field"

        # We should have 2 operations on the stack doing a join. No more, No less.
        assert len(filter_builder.current_operation_stack) == 2, "Attempting to join, when only one comparison has been done"

        lh_operation, rh_operation = filter_builder.current_operation_stack

        # Our Right-Hand operation should be the same as our current filter_builder
        assert other is filter_builder, "Using multiple filter builders, what are you doing?"

        # Join the stack, and populate with a single operation.
        filter_builder.current_operation_stack = [
            JoinOp(operator, lh_operation, rh_operation)
        ]
        return filter_builder

    return inner


class FilterBuilder:
    current_attribute: Optional[str]
    current_operation_stack: List[Union['BinaryOp', 'JoinOp']]

    __slots__ = (
        'current_attribute',
        'current_operation_stack',
    )

    def __init__(self):
        self.current_attribute = None
        self.current_operation_stack = []

    def __getattr__(self: T, name: str) -> T:
        if self.current_attribute:
            self.current_attribute += f".{name}"
        else:
            self.current_attribute = name

        return self

    def render(self):
        # If our stack has more than one entry, we haven't done a join yet, so blow up!
        assert len(self.current_operation_stack) < 2, "Looks like more than 1 conditional is in the pipeline. Did you miss a '&' or '|'?"

        if not self.current_operation_stack:
            return ""

        return self.current_operation_stack[0].render()

    # annoyingly, Salesforce uses '=' instead of '==' for the comparisons
    __eq__ = _comparison('=')  # type: ignore

    __ne__ = _comparison('!=')  # type: ignore
    __lt__ = _comparison('<')
    __le__ = _comparison('<=')
    __gt__ = _comparison('>')
    __ge__ = _comparison('>=')

    __and__ = _join('AND')
    __or__ = _join('OR')


class BinaryOp:
    __slots__ = (
        'operator',
        'lhs',
        'rhs'
    )

    operator: str
    lhs: str
    rhs: Any

    def __init__(self, operator: str, field_ref: str, value: Any):
        self.operator = operator
        self.lhs = field_ref
        self.rhs = value

    def render(self):
        rhs = self.rhs

        if isinstance(rhs, str):
            # We need to quote the strings
            # Note, the escaping done here is to avoid syntax errors, and only passively guards
            # against injection.
            # That being said, SOQL is simple enough that this passive guard should prevent any malicious
            # attacks, however no promises given.
            rhs = f"'{escape_soql_value(rhs)}'"

        elif isinstance(rhs, datetime.date):
            rhs = rhs.strftime('%Y-%m-%d')
        elif isinstance(rhs, datetime.datetime):
            rhs = construct_datetime_str(rhs)
        elif rhs is True:
            rhs = 'TRUE'
        elif rhs is False:
            rhs = 'FALSE'
        elif rhs is None:
            rhs = 'NULL'

        return f"{self.lhs} {self.operator} {rhs}"


class JoinOp:
    __slots__ = (
        'operator',
        'lhs',
        'rhs'
    )

    operator: str
    lhs: Union['BinaryOp', 'JoinOp']
    rhs: Union['BinaryOp', 'JoinOp']

    def __init__(self, operator: str, lhs: Union['BinaryOp', 'JoinOp'], rhs: Union['BinaryOp', 'JoinOp']):
        self.operator = operator
        self.lhs = lhs
        self.rhs = rhs

    def render(self):
        lhs = self.lhs.render()
        rhs = self.rhs.render()
        return f"({lhs}) {self.operator} ({rhs})"


def construct_datetime_str(dt: datetime.datetime):
    # Salesforce doesn't support taking seconds, and must have a colon `:` in the timezone
    # offset. This means we have to construct our own.

    offset = dt.utcoffset()
    if offset is None:
        # assume UTC, so take the easy route out.
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    # are we behind or ahead of UTC
    if offset > datetime.timedelta(0):
        sign = '+'
    else:
        sign = '-'

    # How far are we offset, in hours + minutes
    hours, remaining = divmod(offset, datetime.timedelta(hours=1))
    minutes = remaining // datetime.timedelta(minutes=1)

    # We need to pad the string with '0's
    hours_str = str(hours).rjust(2, '0')
    minutes_str = str(minutes).rjust(2, '0')

    offset_str = f"{sign}{hours_str}:{minutes_str}"

    return dt.strftime(f"%Y-%m-%dT%H:%M:%S{offset_str}")


# https://developer.salesforce.com/docs/atlas.en-us.soql_sosl.meta/soql_sosl/sforce_api_calls_soql_select_quotedstringescapes.htm
_escape_table = str.maketrans({
    "'": "\\'",
    '"': '\\"',
    "\\": '\\\\',
})


def escape_soql_value(value: str) -> str:
    return value.translate(_escape_table)
