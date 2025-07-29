# PyClosure

A minimalist library to bring Clojure-style multimethods, method combinations, and tag-based polymorphism into Python — **without using classes**.

## Features

- Single and multiple argument dispatch  
- Hierarchical dispatch using `derive` and `isa`  
- Extensible method registration with `defmethod`  
- Compositional hooks with `:before`, `:after`, and `:around`  
- Class-free, functional programming style

---

## Installation

Just clone or copy the `pyclosure/` folder into your project.

```
# if you still use `pip`:
pip install pyclosure

# but we highly recommend to use `uv`:
uv add pyclosure

# and after installation via uv you can run the examples by:
pyclosure-zoo

```


---

## Quickstart

### Define animals as dictionaries

```python
simba = {"name": "Simba", "type": "lion"}
dumbo = {"name": "Dumbo", "type": "elephant"}
```

### Create a hierarchy

```python
from pyclosure import Hierarchy, MultiMethod

h = Hierarchy()
h.derive("lion", "big-cat")
h.derive("big-cat", "animal")
h.derive("elephant", "animal")
```

### Define a multimethod

```python
feed = MultiMethod(lambda a: a["type"], hierarchy=h)
```

### Register methods

```python
def lion_feed(a):
    print(f"{a['name']} eats meat")

def elephant_feed(a):
    print(f"{a['name']} eats bananas")

feed.defmethod("lion", lion_feed)
feed.defmethod("elephant", elephant_feed)
```

### Use it

```python
feed(simba)   # Simba eats meat
feed(dumbo)   # Dumbo eats bananas
```

---

## Real Multiple Dispatch

You can dispatch on multiple arguments by making the dispatch function return a tuple:

```python
interact = MultiMethod(lambda a, b: (a["type"], b["type"]), hierarchy=h)

def lion_vs_elephant(a, b):
    print(f"{a['name']} chases {b['name']}")

interact.defmethod(("lion", "elephant"), lion_vs_elephant)

interact(simba, dumbo)  # Simba chases Dumbo
```

---

## Method Combinations

### `:before` – run logic before the main method

```python
def open_cage(a):
    print(f"Opening cage for {a['name']}")

feed.defmethod("lion", open_cage, kind=":before")
```

### `:after` – run logic after the main method

```python
def cleanup(a):
    print(f"Cleaning up after {a['name']}")

feed.defmethod("lion", cleanup, kind=":after")
```

### `:around` – wrap the primary method

```python
def log_feed(inner_fn, a):
    print(f"[LOG] Start {a['name']}")
    result = inner_fn(a)
    print(f"[LOG] End {a['name']}")
    return result

feed.defmethod("lion", log_feed, kind=":around")
```
---


## Method Registration via Decorators

You can also define methods using decorators instead of manual registration.

### Primary method:

```python
@feed.defmethod("lion")
def lion_feed(a):
    print(f"{a['name']} eats meat")
```
### With hooks:

```python
@feed.defmethod("lion", kind=":before")
def open_cage(a):
    print(f"Opening cage for {a['name']}")

@feed.defmethod("lion", kind=":after")
def cleanup(a):
    print(f"Cleaning cage after {a['name']}")

@feed.defmethod("lion", kind=":around")
def logger(inner_fn, a):
    print("[LOG] Start")
    result = inner_fn(a)
    print("[LOG] End")
    return result
```

this is fully equivalent to manually registering via feed.defmethod(...) 
and is great for organizeing logic clearly and idiomatically.

---

## Why PyClosure?

This library helps you:

- Write open, extensible, polymorphic code
- Avoid deep class hierarchies
- Dispatch based on dynamic rules
- Cleanly separate data from behavior

Inspired by:
- [Clojure’s multimethods](https://clojure.org/reference/multimethods)
- [Common Lisp Object System (CLOS)](https://clos-mop.hexstreamsoft.com/)

---

## Example Output

```text
Opening cage for Simba
[LOG] Start Simba
Simba eats meat
[LOG] End Simba
Cleaning up after Simba
```

---

## Coming Soon

- Decorator-based syntax (`@defmethod`)
- Predicate-based dispatch
- Package on PyPI
- Integration with dataclasses or Pydantic (optional)

---

## Philosophy

> “Data is just data. Behavior is just behavior. Dispatch is glue.”  
> – Not Rich Hickey, but close enough.

---

