# pyhurl

A set of useful functions that I use in projects.

## Release Notes:

1.0.0
- First Release

1.0.1
- support oss related functions

1.0.2
- Allow custom llm client params.

1.0.3
- Update SqliteClient:
  - fix database lock error
  - rename methods for better readability
- Important: SqliteClient class is not compatible with previous versions, please adjust your code accordingly.

1.0.4
- Fix SqliteClient:
  - fix discard exception when update error

1.0.5
- Use LLMClient instance instead of LLMClient class to make it more flexible.

1.0.6
- fix sqlite function error: no such function SQRT

1.0.7
- fix sqlite function error: no such function SQRT

1.0.8
- Update MysqlClient:
  - add two convenient functions: `update` and `insert`

1.1.0
- Update SqliteClient:
  - add two convenient functions: `update` and `insert`