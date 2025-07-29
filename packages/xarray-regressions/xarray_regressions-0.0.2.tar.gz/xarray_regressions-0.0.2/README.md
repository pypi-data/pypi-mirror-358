[![PyPI version](https://badge.fury.io/py/xarray-regressions.svg)](https://badge.fury.io/py/xarray-regressions)
[![Build status](https://github.com/aazuspan/xarray-regressions/actions/workflows/ci.yaml/badge.svg)](https://github.com/aazuspan/xarray-regressions/actions/workflows/ci.yaml)

A [pytest-regressions](https://pytest-regressions.readthedocs.io/en/latest/overview.html) plugin for identifying regressions in [Xarray](https://docs.xarray.dev/en/stable/) objects.


> [!WARNING]
> `xarray-regressions` is in early development and might have breaking changes.


## Install

```
pip install xarray-regressions
```

## Usage

> [!TIP]
> If you're unfamiliar with `pytest-regressions`, check out [their documentation](https://pytest-regressions.readthedocs.io/en/latest/overview.html) first. 

Once installed, this package registers a test fixture `xarray_regression` for detecting regressions in the data or metadata of `xr.DataArray` and `xr.Dataset` objects.

Say you have a function `make_dataarray` that should always return the same output:

```python
import xarray as xr

def make_dataarray(name: str) -> xr.DataArray:
    """A dummy method that needs to be tested."""
    return xr.DataArray(
        np.full((2, 4, 3), 1),
        dims=["variable", "y", "x"],
        coords={
            "variable": ["var1", "var2"],
            "y": [1, 2, 3, 4],
            "x": [1, 2, 3],
        },
        name=name,
        attrs={"foo": "bar"},
    )
```

Add the `xarray_regression` fixture to a new test and call the `check` method on the returned data array:

```python
from xarray_regressions import XarrayRegressionFixture # Only used for type annotation

def test_make_dataarray(xarray_regression: XarrayRegressionFixture):
    """Test that the function always returns an identical xr.DataArray."""
    da = make_dataarray(name="test_array")
    xarray_regression.check(
        da,
        check_names=True,
        check_attrs=True,
    )
```

Running the test once will write `da` to a local NetCDF[^netcdf], and future test runs will compare `da` with the stored result. Values, dimensions, and coordinates are checked using [xr.testing.assert_equal](https://docs.xarray.dev/en/stable/generated/xarray.testing.assert_equal.html) or [xr.testing.assert_allclose](https://docs.xarray.dev/en/latest/generated/xarray.testing.assert_allclose.html) (if `atol` or `rtol` are given). Names and attributes are checked seperately. Encodings are *not* currently checked.

If `make_dataarray(name="test_array")` returns a different result in the future, the test will fail:

```text
AssertionError: DataArray names are different. L: foo, R: test_array
```

[^netcdf]: Because results are stored in NetCDF, all tested objects *must* be serializable.
