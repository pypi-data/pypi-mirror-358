# attrobj

A dictionary manipulator that enables attribute-style access to dictionary items.  
Also, supports nested dictionaries and value filtering via predicates.

## Example

```python
from attrobj import Object

foo = Object({"quake": {"mw": "3.7"}})
bar = Object({"quake": {"ml": "3.9"}})

print("first quake:", foo.quake.any(["mw", "ml", "md"], key=True))  # {'mw': 3.7}
print("second quake:", bar.quake.any(["mw", "ml", "md"], key=True))  # {'ml': 3.9}

foo.haskey("quake")  # True
foo.only()  # Filters out None values
foo.only(lambda k, v: k[:2] == "is")  # Filters keys starting with 'is'

info = Object({"quake": {"magnitude": 3.9}})
print(info.quake.magnitude)  # 3.9
```