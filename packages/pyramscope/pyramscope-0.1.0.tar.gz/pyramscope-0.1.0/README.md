# 🧠 Pyramscope

**Pyramscope** is a lightweight, high‑performance C++/pybind11 toolkit for
*inspecting live Python objects*:

* Deep, cycle‑safe memory sizing  
* Shared‑reference (alias) detection  
* Automatic ranking of the heaviest objects  
* Nesting‑depth metrics  
* JSON document (beta)

All with **zero heavy dependencies**—ideal for production and embedded
environments.

---

## 🚀 Key features

| Category | What you get |
| -------- | ------------ |
| **Memory** | `deep_size` for true RAM cost (lists, dicts, attrs, cycles, alias‑safe). |
| **Introspection** | `get_refs`, `get_referents`, `get_aliases`, `get_attrs`. |
| **Analytics** | `get_top_heavy_objects`, `get_nesting_depth`. |
| **Interop** | `export_to_json_optionally` — pretty print or write to file. |
| **Speed** | Core loops in modern C++ 17 via pybind11. |

---

## 📦 Installation (beta)

```bash
pip install pyramscope   # when published on PyPI

# or from source
git clone https://github.com/jara505/pyramscope.git
cd pyramscope
python -m venv .venv && source .venv/bin/activate
pip install .            # builds the native module
```
---
# 🧪 Quick start (classic)

```
import pyramscope as ps

data = {"nums": list(range(10_000)), "nested": {"a": [1, 2, 3]}}
print("Shallow  :", ps.get_size(data), "bytes")
print("Deep     :", ps.deep_size(data), "bytes")        # ← includes sub‑objects
print("Depth    :", ps.get_nesting_depth(data))
```
---
# 🆕 What’s new – v0.1.0 (beta)
- Deep memory scan with alias + cycle protection.
- Automatic “Top N heaviest” object ranking in one call.
- Export results to pretty‑printed JSON or straight‑to‑file.
- CLI skeleton ready for future releases.

# 💡 Extra (innovative) examples

## 1  Detect hidden shared references
```
import pyramscope as ps

a = [1, 2, 3]
b = [a, a]          # two references to same list
print(ps.get_aliases(b))          # → [[1, 2, 3], [1, 2, 3]]

```
## 2  Rank the biggest culprits in a complex graph
```
heavy = [bytearray(1_000_000) for _ in range(5)]
light = ["hi"] * 3
report = ps.get_top_heavy_objects(heavy + light, top_n=3)
for slot in report:
    print(slot["size"], "bytes →", slot["object"][:10], "...")

```
## 3  Export a full heap snapshot to JSON (file or console)
```
import pyramscope as ps, gc, json

snapshot = [o for o in gc.get_objects()][:500]    # small sample
json_str = ps.export_to_json_optionally(snapshot) # prints formatted JSON

# or save directly:
ps.export_to_json_optionally(snapshot, to_file=True, filename="heap.json")
print("heap.json written")
```
---
📄 API overview

| Function                                                                | Purpose                                             |
| ----------------------------------------------------------------------- | --------------------------------------------------- |
| `get_size(obj)`                                                         | Shallow `sys.getsizeof`.                            |
| `deep_size(obj)`                                                        | True recursive size (alias + cycle‑safe).           |
| `get_refs(obj)`                                                         | Objects **pointing to** `obj`.                      |
| `get_referents(obj)`                                                    | Objects **referenced by** `obj`.                    |
| `get_aliases(obj)`                                                      | All aliases (same `id`) inside current heap sample. |
| `get_nesting_depth(obj)`                                                | Maximum container nesting level.                    |
| `get_top_heavy_objects(list, n)`                                        | Top *n* largest objects (deep size).                |
| `get_attrs(obj)`                                                        | Attribute names (like `dir`, but filtered).         |
| `export_to_json_optionally(obj, *, to_file=False, filename="out.json")` | Pretty JSON to console or file.                     |

---

# 👤 Author
Juan Jara 🇳🇮  juanignaciojara505@gmai.com

# 🙌 Contribute
Bugs, benchmarks, and pull requests welcome!
Please open an issue or reach out by email.

