from collections import defaultdict

class Hierarchy:
    def __init__(self):
        self.parents = defaultdict(set)
        self.preferences = defaultdict(set)

    def derive(self, child, parent):
        self.parents[child].add(parent)

    def isa(self, child, ancestor):
        if child == ancestor:
            return True
        return any(self.isa(p, ancestor) for p in self.parents.get(child, []))

    def prefer(self, a, b):
        self.preferences[a].add(b)

    def is_preferred(self, a, b):
        return b in self.preferences.get(a, set())

def tuple_isa(hierarchy, child_tuple, ancestor_tuple):
    if not isinstance(child_tuple, tuple) or not isinstance(ancestor_tuple, tuple):
        return hierarchy.isa(child_tuple, ancestor_tuple)
    return all(hierarchy.isa(c, a) for c, a in zip(child_tuple, ancestor_tuple))

class MultiMethod:
    def __init__(self, dispatch_fn, hierarchy=None):
        self.dispatch_fn = dispatch_fn
        self.hierarchy = hierarchy or Hierarchy()
        self.primary = {}
        self.before = defaultdict(list)
        self.after = defaultdict(list)
        self.around = defaultdict(list)
        self._cache = {}

    def defmethod(self, dispatch_val, fn=None, *, kind="primary"):
        if fn is None:
            # Decorator form: @defmethod("lion")
            def decorator(actual_fn):
                self._register(dispatch_val, actual_fn, kind)
                return actual_fn
            return decorator
        else:
            # Direct registration: defmethod("lion", fn)
            self._register(dispatch_val, fn, kind)

    def _register(self, dispatch_val, fn, kind):
        if kind == "primary":
            self.primary[dispatch_val] = fn
        elif kind == ":before":
            self.before[dispatch_val].append(fn)
        elif kind == ":after":
            self.after[dispatch_val].append(fn)
        elif kind == ":around":
            self.around[dispatch_val].append(fn)
        else:
            raise ValueError(f"Unknown method kind: {kind}")
    
    def __call__(self, *args, **kwargs):
        dispatch_val = self.dispatch_fn(*args, **kwargs)
        method = self._resolve_method(dispatch_val)

        for key in self._sorted_matches(dispatch_val):
            for f in self.before[key]:
                f(*args, **kwargs)

        wrapped = method
        for key in reversed(self._sorted_matches(dispatch_val)):
            for a in self.around[key]:
                wrapped = self._wrap_around(a, wrapped)

        result = wrapped(*args, **kwargs)

        for key in reversed(self._sorted_matches(dispatch_val)):
            for f in self.after[key]:
                f(*args, **kwargs)

        return result

    def _wrap_around(self, around_fn, inner_fn):
        def wrapped(*args, **kwargs):
            return around_fn(inner_fn, *args, **kwargs)
        return wrapped

    def _resolve_method(self, dispatch_val):
        if dispatch_val in self._cache:
            return self._cache[dispatch_val]

        matches = self._sorted_matches(dispatch_val)
        if not matches:
            raise ValueError(f"No method for dispatch value {dispatch_val}")

        matches.sort(key=lambda k: -self._depth(dispatch_val, k))

        if len(matches) > 1 and self.hierarchy.is_preferred(matches[0], matches[1]):
            chosen = matches[0]
        else:
            chosen = matches[0]

        method = self.primary.get(chosen)
        if not method:
            raise ValueError(f"No primary method for dispatch value {chosen}")

        self._cache[dispatch_val] = method
        return method

    def _sorted_matches(self, dispatch_val):
        return [
            k for k in self.primary
            if tuple_isa(self.hierarchy, dispatch_val, k)
        ]

    def _depth(self, child, ancestor):
        if isinstance(child, tuple) and isinstance(ancestor, tuple):
            depths = [self._depth(c, a) for c, a in zip(child, ancestor)]
            return sum(d for d in depths if d >= 0) if all(d >= 0 for d in depths) else -1
        if child == ancestor:
            return 0
        for parent in self.hierarchy.parents.get(child, []):
            d = self._depth(parent, ancestor)
            if d != -1:
                return 1 + d
        return -1
