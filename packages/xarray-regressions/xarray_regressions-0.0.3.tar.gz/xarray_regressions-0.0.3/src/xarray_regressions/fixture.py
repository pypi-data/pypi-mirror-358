from __future__ import annotations

from typing import Any, Callable, TypeVar, Union

from pathlib import Path
import os
import re
import pytest
from pytest_regressions.common import perform_regression_check
import xarray as xr
from xarray.core.utils import dict_equiv
from xarray.core.formatting import diff_attrs_repr

XarrayType = TypeVar("XarrayType", bound=Union[xr.DataArray, xr.Dataset])


def assert_attrs_equal(a: XarrayType, b: XarrayType) -> None:
    assert dict_equiv(a.attrs, b.attrs), diff_attrs_repr(a.attrs, b.attrs, "identical")


def assert_names_equal(a: xr.DataArray, b: xr.DataArray) -> None:
    assert a.name == b.name, f"DataArray names are different. L: {a.name}, R: {b.name}"


class XarrayRegressionFixture:
    def __init__(
        self,
        datadir: Path,
        original_datadir: Path,
        request: pytest.FixtureRequest,
    ) -> None:
        self.request = request
        self.datadir = datadir
        self.original_datadir = original_datadir
        self.force_regen = False
        self.with_test_class_names = False

    def _get_load_fn(self, obj):
        if isinstance(obj, xr.DataArray):
            return xr.open_dataarray
        elif isinstance(obj, xr.Dataset):
            return xr.open_dataset
        else:
            msg = (
                f"Object of type `{obj.__class__.__name__}` has no default loading "
                "function. The object may be unsupported or require explicitly passing "
                "your own `load_fn`."
            )
            raise ValueError(msg)

    def check(
        self,
        obj: XarrayType,
        *,
        obj_id: str | None = None,
        basename: str | None = None,
        fullpath: os.PathLike[str] | None = None,
        rtol: float = 1e-05,
        atol: float = 1e-08,
        check_attrs: bool = True,
        check_name: bool = True,
        load_fn: Callable[[Path], XarrayType] | None = None,
        load_kwargs: dict[str, Any] | None = None,
        dump_kwargs: dict[str, Any] | None = None,
    ) -> None:
        """
        Compare an Xarray object to the previously stored result.

        This minimally checks the values, dimensions, and coordinates of the object.
        Attributes and DataArray names are checked by default. Encodings are *not*
        currently checked.

        Notes
        -----
        When run for the first time, this method will store the object as a NetCDF file.
        Subsequent runs will read that file as the expected result.

        Parameters
        ----------
        obj : xr.DataArray or xr.Dataset
            The Xarray object to check.

        obj_id : str, optional
            A identifier appended to the basename to differentiate multiple checked
            objects in the same test.

        basename : str, optional
            The base name for the regression file. If not provided, it defaults to a
            sanitized version of the test name.

        fullpath : os.PathLike[str], optional
            The full path to the regression file. If provided, it overrides `basename`.

        rtol : float, default 1e-05
            Relative tolerance for comparing numerical values. Set to `0.0` for exact
            equality. Passed to `xr.testing.assert_allclose`.

        atol : float, default 1e-08
            Absolute tolerance for comparing numerical values. Set to `0.0` for exact
            equality. Passed to `xr.testing.assert_allclose`.

        check_attrs : bool, default True
            Whether to check the attributes of the Xarray object against the previous
            result.

        check_name : bool, default True
            Whether to check the name of the DataArray against the previous result.
            Ignored for Dataset objects, which always compare variable names.
        """
        ___tracebackhide__ = True  # noqa: F841

        if load_fn is None:
            load_fn = self._get_load_fn(obj)
        load_kwargs = load_kwargs or {}
        dump_kwargs = dump_kwargs or {}

        if basename is None:
            # Matches the default basename format used by pytest-regressions
            basename = re.sub(r"[\W]", "_", self.request.node.name)
        if obj_id is not None:
            basename = f"{basename}_{obj_id}"

        def check_fn(obtained_filename: Path, expected_filename: Path) -> None:
            obtained = load_fn(obtained_filename, **load_kwargs)
            expected = load_fn(expected_filename, **load_kwargs)
            if check_name and isinstance(obj, xr.DataArray):
                assert_names_equal(obtained, expected)
            if check_attrs:
                assert_attrs_equal(obtained, expected)
            xr.testing.assert_allclose(obtained, expected, rtol=rtol, atol=atol)

        def dump_fn(filename: Path) -> None:
            obj.to_netcdf(filename, **dump_kwargs)

        perform_regression_check(
            datadir=self.datadir,
            original_datadir=self.original_datadir,
            request=self.request,
            check_fn=check_fn,
            dump_fn=dump_fn,
            extension=".nc",
            basename=basename,
            fullpath=fullpath,
            force_regen=self.force_regen,
            with_test_class_names=self.with_test_class_names,
        )
