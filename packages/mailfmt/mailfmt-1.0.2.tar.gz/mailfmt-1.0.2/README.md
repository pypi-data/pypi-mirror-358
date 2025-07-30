<h1>Mail Format</h1>

`mailfmt` is a simple plain text email formatter. It's designed to ensure
consistent paragraph spacing while preserving markdown syntax, email headers,
sign-offs, and signature blocks.

By default, the command accepts its input on `stdin` and prints to `stdout`.
This makes it well suited for use as a formatter with a text editor like Kakoune
or Helix.

<!--toc:start-->

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Output Example](#output-example)
- [Markdown Safety](#markdown-safety)
- [Aerc Integration](#aerc-integration)
- [Contributing](#contributing)

<!--toc:end-->

## Features

- Wraps emails at specified columns.
- Automatically reflows paragraphs.
- Squashes consecutive paragraph breaks.
- Preserves:
  - Any long word not broken by spaces (e.g. URLs, email addresses).
  - Quoted lines.
  - Indented lines.
  - Lists.
  - Markdown-style code blocks.
  - Usenet-style signature block at EOF.
  - Sign-offs.
- If specified, output can be made safe for passing to a Markdown renderer.
  - Use case: piping the output to `pandoc` to write a `text/html` message. See
    [Markdown Safety](#markdown-safety).

## Installation

`mailfmt` is intended for use as a standaole tool. The package is available on
PyPI as `mailfmt`. I recommend using [uv](https://github.com/astral-sh/uv) or
`pipx` to install it so the `mailfmt` command is available on your path:

```sh
uv tool install mailfmt
```

Verify that the installation was successful:

```sh
mailfmt --help
```

The tool doesn't currently have any dependencies. Therefore, you can just
download and execute the
[mailfmt](https://git.sr.ht/~ficd/mailfmt/tree/main/item/mailfmt.py) script
directly. However, dependencies may be introduced later, so I recommend
installing with a Python package manager.

## Usage

```
usage: mailfmt [-h] [-w WIDTH] [-b] [--no-replace-whitespace] [--no-reflow]
               [--no-signoff] [--no-signature] [--no-squash] [-m] [-i INPUT]
               [-o OUTPUT]

Formatter for plain text email.
"--no-*" options are NOT passed by default.

options:
  -h, --help            show this help message and exit
  -w, --width WIDTH     Text width for wrapping. (default: 74)
  -b, --break-long-words
                        Break long words while wrapping. (default: False)
  --no-replace-whitespace
                        Don't normalize whitespace when wrapping.
  --no-reflow           Don't reflow lines.
  --no-signoff          Don't preserve signoff line breaks.
  --no-signature        Don't preserve signature block.
  --no-squash           Don't squash consecutive paragraph breaks.
  -m, --markdown-safe   Output format safe for Markdown rendering.
  -i, --input INPUT     Input file. (default: STDIN)
  -o, --output OUTPUT   Output file. (default: STDOUT)

Author : Daniel Fichtinger
License: ISC
Contact: daniel@ficd.ca
```

## Output Example

Before:

```
Hey,

This is a really long paragraph with lots of words in it. However, my text editor uses soft-wrapping, so it ends up looking horrible when viewed without wrapping! Additionally,
if I manually add some line breaks, things start to look _super_ janky!

I can't just pipe this to `fmt` because it may break my beautiful
markdown
syntax. Markdown formatters are also problematic because they mess up
my signoff and signature blocks! What should I do?

Best wishes,
Daniel

-- 
Daniel
sr.ht/~ficd
daniel@ficd.ca
```

After:

```
Hey,

This is a really long paragraph with lots of words in it. However, my text
editor uses soft-wrapping, so it ends up looking horrible when viewed
without wrapping! Additionally, if I manually add some line breaks, things
start to look _super_ janky!

I can't just pipe this to `fmt` because it may break my beautiful markdown
syntax. Markdown formatters are also problematic because they mess up my
signoff and signature blocks! What should I do?

Best wishes,
Daniel

-- 
Daniel
sr.ht/~ficd
daniel@ficd.ca
```

## Markdown Safety

In some cases, you may want to generate an HTML email. Ideally, you'd want the
HTML to be generated directly from the plain text message, and for _both_
versions to be legible and have the same semantics.

Although `mailfmt` was written with Markdown markup in mind, its intended output
is still the `text/plain` format. If you pass its output directly to a Markdown
renderer, line breaks in sign-offs and the signature block won't be preserved.

If you invoke `mailfmt --markdown-safe`, then `\` characters will be appended to
mark line breaks that would otherwise be squashed, making the output suitable
for conversion into HTML. Here's an example of one such pipeline:

```bash
cat message.txt | mailfmt --markdown-safe | pandoc -f markdown -t html
--standalone > message.html
```

Here's the earlier example message with markdown safe output:

```
Hey,

This is a really long paragraph with lots of words in it. However, my text
editor uses soft-wrapping, so it ends up looking horrible when viewed
without wrapping! Additionally, if I manually add some line breaks, things
start to look _super_ janky!

I can't just pipe this to `fmt` because it may break my beautiful markdown
syntax. Markdown formatters are also problematic because they mess up my
signoff and signature blocks! What should I do?

Best wishes, \
Daniel \

--  \
Daniel \
sr.ht/~ficd \
daniel@ficd.ca \
```

## Aerc Integration

For integration with `aerc`, consider adding the following to your `aerc.conf`:

```ini
[multipart-converters]
text/html=mailfmt --markdown-safe | pandoc -f markdown -t html --standalone
```

When you're done writing your email, you can call the `:multipart text/html`
command to generate a `multipart/alternative` message which includes _both_ your
original `text/plain` _and_ the newly generated `text/html` content.

## Contributing

Please send patches, requests, and concerns to my
[public inbox](https://lists.sr.ht/~ficd/public-inbox).
