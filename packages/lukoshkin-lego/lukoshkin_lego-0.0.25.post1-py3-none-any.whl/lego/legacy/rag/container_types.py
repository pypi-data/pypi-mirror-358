from typing import DefaultDict, NewType

UseProfiler = NewType("UseProfiler", bool)
ProfilerSessions = NewType(
    "ProfilerSessions", DefaultDict[str, dict[str, float]]
)
