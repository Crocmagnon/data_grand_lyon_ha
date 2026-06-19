---
name: add-grand-lyon-dataset
description: Use when adding support for a new Grand Lyon open data dataset to this library — i.e. a new `get_*` method on `DataGrandLyonClient`, its data model, a pure lookup/filter helper, and the matching tests/docs. Triggers on requests like "add a method to fetch <dataset>", "support the <X> endpoint", "expose <dataset> from the Grand Lyon API".
---

# Add a Grand Lyon dataset

Each dataset on the Grand Lyon platform is exposed the same way. Follow these steps in order, mirroring the existing TCL stops / park-and-ride / Vélo'v implementations. Reuse the named references rather than inventing new shapes.

## What you need first

- The **layer name** (e.g. `tcl_sytral.tclparcrelaistr`) → full URL is `{BASE_URL}/<layer_name>/all.json`.
- Whether the endpoint **requires auth** (TCL real-time needs it; Vélo'v is public).
- A **sample JSON response** (`{"fields": [...], "values": [...]}`) to derive field names, types, and which fields can be null.

## Steps

1. **Model** — `src/data_grand_lyon_ha/models.py`
   - `@dataclass(frozen=True)` with a docstring and a type annotation on every field.
   - Date fields → `datetime | None` (parsed in the client, not here).
   - Reference: `TclStop`, `TclParkAndRide`.

2. **Client method** — `src/data_grand_lyon_ha/client.py`
   - `async def get_<dataset>(self) -> list[<Model>]:`, modeled on `get_tcl_stops` / `get_tcl_park_and_rides`.
   - `url = f"{self.BASE_URL}/<layer_name>/all.json"`.
   - `self._session.get(url, params={"maxfeatures": "-1"}, auth=self._auth)` — **omit `auth=`** for public endpoints (see `get_velov_stations`).
   - `resp.raise_for_status()`, then `data = await resp.json()`.
   - Parse dates with `datetime.fromisoformat(v["x"]) if v["x"] else None`.
   - Return a list-comprehension over `data["values"]`.
   - Import the new model in the existing `from .models import (...)` block.

3. **Filter helper** — by domain: `src/data_grand_lyon_ha/tcl.py` for TCL/Sytral data, `src/data_grand_lyon_ha/velov.py` for Vélo'v.
   - Pure function `find_<dataset>_by_id(items, item_id) -> <Model> | None` (loop, return first match or `None`).
   - Mind the id type (TCL stops use `int`, park-and-rides use `str`).
   - Reference: `find_tcl_stop_by_id`, `find_tcl_park_and_ride_by_id`.

4. **Exports** — `src/data_grand_lyon_ha/__init__.py`
   - Add the model and the helper to the relevant `from ...` import blocks **and** to `__all__`.
   - Keep both lists in **alphabetical order**.

5. **Tests** — pytest
   - `tests/test_client.py`: add a `SAMPLE_<DATASET>_RESPONSE` dict derived from real JSON (include at least one row with a null `last_update`). Add a test using the existing `_make_client_with_response` helper that asserts full equality of the first parsed object and checks date parsing + the null case.
   - `tests/test_<domain>.py`: add a list of model instances and tests for the filter (found / not found / empty list), like `test_velov.py` and the park-and-ride tests in `test_tcl.py`.

6. **Docs & playground** (the "Checklist for New Features" in `CLAUDE.md`)
   - `contrib/playground.py`: fetch the dataset, look one up by id, print it.
   - `README.md`: add a usage snippet (import + `get_*` + `find_*_by_id`).
   - `CLAUDE.md`: add the new model and helper to the "Key Modules" lists.

## Verify

```bash
uv run pytest
```
