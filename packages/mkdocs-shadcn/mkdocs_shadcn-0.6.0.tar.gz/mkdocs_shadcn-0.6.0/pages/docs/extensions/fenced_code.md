---
title: Fenced code
---

The Fenced Code Blocks extension adds a secondary way to define code blocks, which overcomes a few limitations of indented code blocks.

## Configuration

```yaml
# mkdocs.yml

markdown_extensions:
  - fenced_code
```

## Syntax

~~~ md
``` { .python linenos=true hl_lines="4 5" }
def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

for num in fibonacci(10):
    print(num)
```
~~~


``` { .python linenos=true hl_lines="4 5" }
def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

for num in fibonacci(10):
    print(num)
```