# LibSalesforce

LibSalesforce deals with ...

\# TODO: a brief overview.

## Set up

You will need `flit` for managing the python dependencies.
a `Makefile` is used to make sure your dependencies are up to date:

`make install` will do everything you need.

## Linting

4 Linters have been set up to adhere to our style guidelines and code checks:
- isort
- black
- autoflake
- mypy

You can check your changes by running `make lint` to get a report.

To fix any linting issues, run:
```sh
make fixlint
```
