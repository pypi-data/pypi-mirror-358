import pytest
from mapdispatch import Hierarchy, MultiMethod

def test_single_dispatch():
    h = Hierarchy()
    h.derive("lion", "animal")
    h.derive("elephant", "animal")

    feed = MultiMethod(lambda a: a["type"], hierarchy=h)

    results = []

    def lion_feed(a):
        results.append(f"{a['name']} eats meat")

    def elephant_feed(a):
        results.append(f"{a['name']} eats bananas")

    feed.defmethod("lion", lion_feed)
    feed.defmethod("elephant", elephant_feed)

    simba = {"name": "Simba", "type": "lion"}
    dumbo = {"name": "Dumbo", "type": "elephant"}

    feed(simba)
    feed(dumbo)

    assert results == [
        "Simba eats meat",
        "Dumbo eats bananas"
    ]

def test_multiple_dispatch_fallback():
    h = Hierarchy()
    h.derive("lion", "big-cat")
    h.derive("tiger", "big-cat")
    h.derive("big-cat", "animal")

    interact = MultiMethod(lambda a, b: (a["type"], b["type"]), hierarchy=h)

    results = []

    def bigcat_interact(a, b):
        results.append(f"{a['name']} and {b['name']} pounce")

    interact.defmethod(("big-cat", "big-cat"), bigcat_interact)

    simba = {"name": "Simba", "type": "lion"}
    shere = {"name": "Shere Khan", "type": "tiger"}

    interact(simba, shere)

    assert results == ["Simba and Shere Khan pounce"]

def test_method_combinations():
    h = Hierarchy()
    h.derive("lion", "animal")

    events = []

    feed = MultiMethod(lambda a: a["type"], hierarchy=h)

    def lion_feed(a):
        events.append(f"{a['name']} eats meat")

    def before(a):
        events.append(f"Open cage for {a['name']}")

    def after(a):
        events.append(f"Clean cage after {a['name']}")

    def around(inner_fn, a):
        events.append(f"[LOG] Start {a['name']}")
        inner_fn(a)
        events.append(f"[LOG] End {a['name']}")

    feed.defmethod("lion", lion_feed)
    feed.defmethod("lion", before, kind=":before")
    feed.defmethod("lion", after, kind=":after")
    feed.defmethod("lion", around, kind=":around")

    simba = {"name": "Simba", "type": "lion"}
    feed(simba)

    assert events == [
        "Open cage for Simba",
        "[LOG] Start Simba",
        "Simba eats meat",
        "[LOG] End Simba",
        "Clean cage after Simba"
    ]

def test_defmethod_decorator_support():
    h = Hierarchy()
    h.derive("lion", "animal")

    events = []

    feed = MultiMethod(lambda a: a["type"], hierarchy=h)

    @feed.defmethod("lion")
    def lion_feed(a):
        events.append(f"{a['name']} eats meat")

    @feed.defmethod("lion", kind=":before")
    def open_cage(a):
        events.append(f"Open cage for {a['name']}")

    @feed.defmethod("lion", kind=":after")
    def cleanup(a):
        events.append(f"Clean cage after {a['name']}")

    @feed.defmethod("lion", kind=":around")
    def logger(inner_fn, a):
        events.append(f"[LOG] Start {a['name']}")
        inner_fn(a)
        events.append(f"[LOG] End {a['name']}")
        return "OK"

    simba = {"name": "Simba", "type": "lion"}
    result = feed(simba)

    assert result == "OK"
    assert events == [
        "Open cage for Simba",
        "[LOG] Start Simba",
        "Simba eats meat",
        "[LOG] End Simba",
        "Clean cage after Simba"
    ]
