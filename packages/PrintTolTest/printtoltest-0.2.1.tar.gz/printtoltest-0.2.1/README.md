# PrintTolTest

A simple CLI tool to calculate 3D print dimensional tolerance.

It is worthy to note this is more for testing your print consistency (and lets be honest, even more-so bragging).

Testing in this way is not an end-all be-all solution,
It does have issues and is not a perfect representation of printer performance.

## Installation

Get the Latest

```sh
python3 -m pip install --upgrade 'PrintTolTest @ git+https://github.com/NanashiTheNameless/PrintTolTest@main'
```

Or get from [PyPi](<https://pypi.org/project/PrintTolTest/>) (not recommended, may be out of date)

```sh
python3 -m pip install --upgrade PrintTolTest
```

## Get started

### Interactively

```sh
PrintTolTest
```

### Partially-interactively

```sh
PrintTolTest --expected X Y Z
```

### Non-Interactively

```sh
PrintTolTest --expected X Y Z --measured X Y Z
```

## Credits

[All Major Contributors](<CONTRIBUTORS.md>)

[All Other Contributors](<https://github.com/NanashiTheNameless/PrintTolTest/graphs/contributors>)
