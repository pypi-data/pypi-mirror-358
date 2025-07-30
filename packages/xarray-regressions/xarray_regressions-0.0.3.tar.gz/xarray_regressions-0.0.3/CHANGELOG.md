# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [0.0.3] - 2025-06-29

### Changed

- Equality checks now use a small tolerance by default to match [`ndarrays_regression`](https://pytest-regressions.readthedocs.io/en/latest/api.html#ndarrays-regression). Exact equality can be enforced by setting `rtol=0.0` and `atol=0.0`.
- Renamed `check_names` parameter to `check_name` for clarity.

### Added

- The `check` method now accepts an `obj_id` argument to differentiate between multiple objects in the same test. The ID will be appended to the basename of the test, allowing each object to be tested against itself.

## [0.0.2] - 2025-06-26

### Added

- Backwards support for Python 3.9

## [0.0.1] - 2025-05-23

### Added

- Initial release

---

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

[unreleased]: https://github.com/aazuspan/xarray-regressions/compare/v0.0.3...HEAD
[0.0.3]: https://github.com/aazuspan/xarray-regressions/compare/v0.0.2...v0.0.3
[0.0.2]: https://github.com/aazuspan/xarray-regressions/compare/v0.0.1...v0.0.2
[0.0.1]: https://github.com/aazuspan/xarray-regressions/releases/tag/v0.0.1
