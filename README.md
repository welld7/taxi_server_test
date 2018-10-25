Introduction
============
Tests for taxi service

How To Run Tests
================
To run dumping logs
```
./LAUNCHER &>LOG
```

To run sanity suite execute:

```
  py.test -v -m 'sanity'
```

To run negative test suite:

```
  py.test -v -m 'negative'
```

To run long tests:

```
  py.test -v -m 'long'
```

To run all the tests
```
  py.test -v -m 'taxi'
```

