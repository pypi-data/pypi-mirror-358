# rrule

RRULE library for Python backed by [rust-rrule](https://github.com/fmeringdal/rust-rrule).

## Fork

This library is a fork from https://pypi.org/project/rrule/.

It adds protection against ill formatted recurrence rules by returning None,
instead of throwing an uncatchable PanicException.
