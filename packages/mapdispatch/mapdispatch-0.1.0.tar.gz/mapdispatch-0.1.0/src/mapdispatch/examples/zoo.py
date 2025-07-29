from mapdispatch import Hierarchy, MultiMethod

# 1. Setup animal data
simba = {"name": "Simba", "type": "lion"}
shere = {"name": "Shere Khan", "type": "tiger"}
dumbo = {"name": "Dumbo", "type": "elephant"}

# 2. Create and populate hierarchy
h = Hierarchy()
h.derive("lion", "big-cat")
h.derive("tiger", "big-cat")
h.derive("big-cat", "animal")
h.derive("elephant", "animal")

# 3. Define single-dispatch multimethod
feed = MultiMethod(lambda a: a["type"], hierarchy=h)

# 4. Define primary methods
def lion_feed(a):
    print(f"{a['name']} eats meat")

def elephant_feed(a):
    print(f"{a['name']} eats bananas")

def bigcat_feed(a):
    print(f"{a['name']} eats like a cat")

feed.defmethod("lion", lion_feed)
feed.defmethod("elephant", elephant_feed)
feed.defmethod("big-cat", bigcat_feed)

# 5. Add method combinations
def open_cage(a):
    print(f"Opening cage for {a['name']}")

def cleanup(a):
    print(f"Cleaning up after {a['name']}")

def log_feed(inner_fn, a):
    print(f"[LOG] Start {a['name']}")
    result = inner_fn(a)
    print(f"[LOG] End {a['name']}")
    return result

feed.defmethod("lion", open_cage, kind=":before")
feed.defmethod("lion", cleanup, kind=":after")
feed.defmethod("lion", log_feed, kind=":around")

# 6. Define real multiple dispatch: interactions
interact = MultiMethod(lambda a, b: (a["type"], b["type"]), hierarchy=h)

def lion_vs_lion(a, b):
    print(f"{a['name']} roars at {b['name']}")

def lion_vs_elephant(a, b):  
    print(f"{a['name']} chases {b['name']}")
    
def elephant_vs_lion(a, b):
    print(f"{a['name']} flees from {b['name']}")
    
def bigcats_fight(a, b):
    print(f"{a['name']} fights {b['name']} like wild cats!")

def generic_encounter(a, b):
    print(f"{a['name']} and {b['name']} look at each other curiously.")
    
interact.defmethod(("lion", "lion"), lion_vs_lion)
interact.defmethod(("lion", "elephant"), lion_vs_elephant)
interact.defmethod(("elephant", "lion"), elephant_vs_lion)
interact.defmethod(("big-cat", "big-cat"), bigcats_fight)
interact.defmethod(("animal", "animal"), generic_encounter)    # general fallback


def main():
    # 7. Feed animals
    print("== Feeding Simba ==")
    feed(simba)

    print("\n== Feeding Dumbo ==")
    feed(dumbo)

    print("\n== Feeding Shere Khan ==")
    feed(shere)

    # 8. Run interactions
    print("\n== Interactions ==")
    interact(simba, shere)
    interact(simba, dumbo)
    interact(dumbo, simba)

if __name__ == "__main__":
    main()


