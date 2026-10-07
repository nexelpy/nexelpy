# QuickEvent

A minimal JavaScript library for event handling, DOM manipulation, and AJAX .

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Events](#events)
3. [Commands](#commands)
4. [AJAX](#ajax)
5. [Values](#values)
6. [Templates](#templates)
7. [Conditions](#conditions)
8. [Execution Order](#execution-order)
9. [Full Reference](#full-reference)

---

## Quick Start

QuickEvent works on HTML. Add an attribute with the event name to any element:

```python
x.button("Click me", click=[
    ["setText", "this", "Clicked!"]
])
```

Result:

```html
<button click='[["setText", "this", "Clicked!"]]'>
  Click me
</button>
```

Allowed events:

```
click, dblclick, keyup, keydown, change, input, submit, focus, blur, mouseenter, mouseleave
```

Also `loadDom` runs once when the page is loaded.

---

## Events

Each event takes an **array of commands** that run **in order**.

```python
x.button("Click", click=[
    ["setText", "this", "First"],
    ["addClass", "this", "active"]
])
```

| Event | Description |
|-------|-------------|
| `click` | Mouse click |
| `dblclick` | Double click |
| `keyup` | Key released |
| `keydown` | Key pressed |
| `change` | Value changed |
| `input` | Input event |
| `submit` | Form submit |
| `focus` | Element focused |
| `blur` | Element blurred |
| `mouseenter` | Mouse enters |
| `mouseleave` | Mouse leaves |
| `loadDom` | Runs once after page load |

---

## Commands

### Text

```python
["setText", selector, text, delay?]
["appendText", selector, text, delay?]
["prependText", selector, text, delay?]
```

### HTML

```python
["setHtml", selector, html, delay?]
["appendHtml", selector, html, delay?]
["prependHtml", selector, html, delay?]
```

### Value

```python
["setValue", selector, value, delay?]
```

### Class

```python
["addClass", selector, className, delay?]
["removeClass", selector, className, delay?]
["toggleClass", selector, className, delay?]
["setClass", selector, className, delay?]
```

### Attribute

```python
["setAttr", selector, name, value, delay?]
["setAttrs", selector, attrs, delay?]
["removeAttr", selector, name, delay?]
```

### Props (attribute without value)

```python
["setProps", selector, name, delay?]
["removeProps", selector, name, delay?]
["toggleProps", selector, name, delay?]
```

### Style

```python
["addStyle", selector, styles, delay?]
["removeStyle", selector, key, delay?]
["setStyle", selector, styles, delay?]
```

### Animation

```python
["animate", selector, css, delay?, duration?, ease?]
```

```python
["animate", "this", {"color": "red"}, 0, 500]
["animate", "this", {"opacity": 0.5, "transform": "scale(1.1)"}, 0, 300, "ease-out"]
```

### Utilities

```python
["wait", ms]
["log", value]
["redirect", url]
["reload"]
["scrollTo", target]
["focus", selector]
```

### Clipboard

```python
["copyClipboard", selector, value]
["pasteClipboard", selector]
```

### Custom Function

```python
["runFunc", path, name, arg1, arg2, ...]
```

Imports the module at `path` and calls `name` with args.

```python
["runFunc", "/utils.js", "formatDate", "@@now"]
["setText", "p", ["runFunc", "/utils.js", "capitalize", "hello"]]
```

---

## AJAX

```python
["ajax", url, method?, body?]
```

```python
["ajax", "/api/users"]
["ajax", "/api/save", "POST", {"name": "Ali"}]
["ajax", "/api/search", "GET", {"q": "test"}]
```

- **GET** — data becomes query string
- **POST** — data becomes JSON body

After the response, `@@response` is available:

```python
["ajax", "/api/data"]
["setHtml", "#result", "@@response.view"]
```

---

## Values

Values can be read from elements, the response, or the browser.

### `@@attr.key` — from attribute

```python
["@@attr.counter", "div"]
["@@attr.counter", "div", "{counter + 1}"]
["@@attr.counter", "div", "count is {counter}"]
```

### `@@input.key` — from property

```python
["@@input.value", "this"]
["@@input.checked", "this"]
```

Difference between `@@attr` and `@@input`:

- `@@attr.value` → attribute value (initial)
- `@@input.value` → property value (current)

### `@@text` — from textContent

```python
["@@text", "#my-div"]
["@@text", "#my-div", "text is {text}"]
```

### `@@html` — from innerHTML

```python
["@@html", "#my-div"]
```

### `@@form` — all form fields

```python
["@@form", "#myform"]
```

Collects all named fields into an object.

```python
with x.form(id="myform"):
    x.input(name="name", placeholder="name")
    x.input(name="age", placeholder="age")
    x.submit("Send", click=[
        ["ajax", "/api/save", "POST", ["@@form", "#myform"]],
        ["setHtml", "p", "@@response.view"]
    ])
```

### `@@response` — from AJAX response

```python
["@@response"]
["@@response.view"]
["@@response.data.student.name"]
```

### `@@cookie.key` — from cookies

```python
["@@cookie.sessionId"]
```

### `@@location.key` — from location

```python
["@@location.href"]
["@@location.pathname"]
["@@location.search"]
["@@location.hash"]
```

---

## Templates

Use `{}` to embed values inside text:

```python
["@@attr.counter", "div", "count is {counter}"]
# → "count is 6"

["@@attr.counter", "div", "count is {counter + 1}"]
# → "count is 7"

["@@attr.counter", "div", "count is {counter += 1}"]
# → "count is 7" (and counter is saved as 7)
```

### Multiple values

```python
["@@attr.counter,name", "div", "{counter} - {name}"]
```

### Functions

```python
["@@attr.counters", "span", "sum: {sum(counters)}"]
["@@attr.counters", "span", "min: {min(counters)}"]
["@@attr.counters", "span", "max: {max(counters)}"]
["@@attr.counters", "span", "avg: {avg(counters)}"]
["@@attr.counters", "span", "count: {count(counters)}"]
```

### Operators

```python
["@@attr.counter", "div", "{counter + 1}"]
["@@attr.counter", "div", "{counter - 1}"]
["@@attr.counter", "div", "{counter * 2}"]
["@@attr.counter", "div", "{counter / 2}"]
["@@attr.counter", "div", "{counter % 3}"]
["@@attr.counter", "div", "{counter ** 2}"]
["@@attr.counter", "div", "{(counter + 1) * 8}"]
```

### Assignment operators

```python
["@@attr.counter", "div", "{counter += 1}"]
["@@attr.counter", "div", "{counter -= 5}"]
["@@attr.counter", "div", "{counter *= 2}"]
["@@attr.counter", "div", "{counter /= 4}"]
["@@attr.counter", "div", "{counter %= 2}"]
```

### String methods

```python
["@@attr.name", "div", "{name.toUpperCase()}"]
["@@attr.name", "div", "{name.toLowerCase()}"]
["@@attr.name", "div", "{name.trim()}"]
["@@attr.name", "div", "{name.slice(0, 3)}"]
["@@attr.url", "a", "{url.replace('api', 'vapi')}"]
```

### Math functions

```python
["@@attr.counter", "div", "{abs(counter)}"]
["@@attr.counter", "div", "{floor(counter)}"]
["@@attr.counter", "div", "{ceil(counter)}"]
["@@attr.counter", "div", "{round(counter)}"]
["@@attr.counter", "div", "{sqrt(counter)}"]
["@@attr.counter", "div", "{pow(counter, 2)}"]
```

---

## Conditions

Conditions are block-based. Body runs until the next `if`, `elif`, `else`, or `endCondition`.

```python
["if", condition],
["setText", "p", "..."],
["elif", condition],
["setText", "p", "..."],
["else"],
["setText", "p", "..."],
["endCondition"]
```

### Condition syntax

A condition is `["@@type.key", "selector", "{expression}"]`:

```python
["if", ["@@attr.counter", "this", "{counter > 7}"]]
```

### `and` / `or`

```python
["if",
    ["@@attr.counter", "this", "{counter > 3}"],
    "and",
    ["@@attr.counter", "this", "{counter < 10}"]
]
```

Precedence: `and` > `or`.

```python
["if",
    ["@@attr.counter", "this", "{counter > 10}"],
    "or",
    ["@@attr.counter", "this", "{counter == 0}"]
]
```

### Example

```python
x.button("Check", counter=6, click=[
    ["if", ["@@attr.counter", "this", "{counter > 10}"]],
    ["setText", "this", "counter is > 10"],
    ["elif", ["@@attr.counter", "this", "{counter > 5}"]],
    ["setText", "this", "counter is > 5"],
    ["else"],
    ["setText", "this", "counter is {counter}"],
    ["endCondition"]
])
```

### Rules

- Nested `if` is not allowed
- Without `endCondition`, body runs to the end
- `endCondition` is optional
- `then` inside a body works normally

---

## Execution Order

Commands run **in order**. AJAX and animations **block** the chain.

```python
["setText", "#status", "Loading..."]
["ajax", "/api/data"]
["setHtml", "#result", "@@response.view"]
["setText", "#status", "Done"]
```

### Parallel with `then`

Use `then` to wait for all pending promises:

```python
["animate", "#box", {"opacity": 0}, 0, 3000]
["ajax", "/api/data"]
["then"]
["setHtml", "#result", "@@response.view"]
```

Order:

1. `animate` starts (non-blocking)
2. `ajax` starts
3. `then` waits for both
4. `setHtml` runs

### `wait`

Pause the chain:

```python
["setText", "#msg", "Hello"]
["wait", 2000]
["setText", "#msg", "World"]
```

---

## Full Reference

### Events

`click`, `dblclick`, `keyup`, `keydown`, `change`, `input`, `submit`, `focus`, `blur`, `mouseenter`, `mouseleave`, `loadDom`

### Commands

| Command | Structure |
|---------|-----------|
| `setText` | `["setText", selector, text, delay?]` |
| `appendText` | `["appendText", selector, text, delay?]` |
| `prependText` | `["prependText", selector, text, delay?]` |
| `setHtml` | `["setHtml", selector, html, delay?]` |
| `appendHtml` | `["appendHtml", selector, html, delay?]` |
| `prependHtml` | `["prependHtml", selector, html, delay?]` |
| `setValue` | `["setValue", selector, value, delay?]` |
| `addClass` | `["addClass", selector, className, delay?]` |
| `removeClass` | `["removeClass", selector, className, delay?]` |
| `toggleClass` | `["toggleClass", selector, className, delay?]` |
| `setClass` | `["setClass", selector, className, delay?]` |
| `setAttr` | `["setAttr", selector, name, value, delay?]` |
| `setAttrs` | `["setAttrs", selector, attrs, delay?]` |
| `removeAttr` | `["removeAttr", selector, name, delay?]` |
| `setProps` | `["setProps", selector, name, delay?]` |
| `removeProps` | `["removeProps", selector, name, delay?]` |
| `toggleProps` | `["toggleProps", selector, name, delay?]` |
| `addStyle` | `["addStyle", selector, styles, delay?]` |
| `removeStyle` | `["removeStyle", selector, key, delay?]` |
| `setStyle` | `["setStyle", selector, styles, delay?]` |
| `animate` | `["animate", selector, css, delay?, duration?, ease?]` |
| `wait` | `["wait", ms]` |
| `log` | `["log", value]` |
| `redirect` | `["redirect", url]` |
| `reload` | `["reload"]` |
| `scrollTo` | `["scrollTo", target]` |
| `focus` | `["focus", selector]` |
| `copyClipboard` | `["copyClipboard", selector, value]` |
| `pasteClipboard` | `["pasteClipboard", selector]` |
| `runFunc` | `["runFunc", path, name, ...args]` |
| `ajax` | `["ajax", url, method?, body?]` |
| `then` | `["then"]` |

### Values

| Syntax | Source |
|--------|--------|
| `@@attr.key` | element attribute |
| `@@input.key` | element property |
| `@@text` | element textContent |
| `@@html` | element innerHTML |
| `@@form` | form fields |
| `@@response` | AJAX response |
| `@@response.key` | response path |
| `@@cookie.key` | cookie |
| `@@location.key` | location |

### Template Functions

| Function | Description |
|----------|-------------|
| `sum(x)` | Sum |
| `sub(x)` | Subtract |
| `min(x)` | Minimum |
| `max(x)` | Maximum |
| `avg(x)` | Average |
| `count(x)` | Count |
| `abs(x)` | Absolute |
| `floor(x)` | Floor |
| `ceil(x)` | Ceiling |
| `round(x)` | Round |
| `sqrt(x)` | Square root |
| `pow(x, n)` | Power |

### String Methods

`replace`, `toUpperCase`, `toLowerCase`, `trim`, `slice`, `substring`, `substr`, `length`, `repeat`, `padStart`, `padEnd`, `concat`, `charAt`, `includes`, `startsWith`, `endsWith`, `indexOf`, `split`

### Operators

| Operator | Description |
|----------|-------------|
| `+` `-` `*` `/` `%` `**` | Arithmetic |
| `>` `<` `>=` `<=` `==` `!=` | Comparison |
| `&&` `\|\|` `!` | Logical |
| `+=` `-=` `*=` `/=` `%=` | Assignment |

### Selectors

- `"this"` — current element
- `"#id"` — by id
- `".class"` — by class
- `"div"` — by tag
- `"div.class"` — combined

---

## Example

```python
with x.form(id="myform"):
    x.input(type="text", name="name", placeholder="name")
    x.br()
    x.input(type="text", name="family", placeholder="family")
    x.br()
    x.input(type="text", name="age", placeholder="age")
    x.br()
    x.input(type="text", name="lang", placeholder="lang")
    x.br()
    x.submit("Send", click=[
        ["ajax", "/api/save", "POST", ["@@form", "#myform"]],
        ["setHtml", "p", "@@response.view"]
    ])

x.p("Result...")
```

---

## License

MIT