# Introduction

Engin is a lightweight application framework for modern Python.

Engin is inspired by [Uber's Fx framework for Go](https://github.com/uber-go/fx) and the
[Injector framework for Python](https://github.com/python-injector/injector).

## Why use Engin?

- **Dependency Injection** - Engin includes a fully-featured Dependency Injection system,
  powered by type hints.
- **Applicaton Management** - Engin can run your whole application from start to end with
  a simple call to `run()` including managing lifecycle startup and shutdown tasks. 
- **Code Reuse** - Engin's modular components, called Blocks, work great as distributed
  packages allowing zero boiler-plate code reuse across multiple applications. Perfect for
  maintaining many services across your organisation.
- **Ecosystem Compatability** - Engin ships with integrations for popular frameworks that
  provide their own Dependency Injection, such as FastAPI, allowing you to integrate
  Engin into existing code bases incrementally.
- **Async Native**: Engin is an async framework, meaning first class support for async
  dependencies and applications, but can easily run synchronous code as well.
