#!/bin/env python

# Simple text-wrapping script for email.
# Preserves code blocks, quotes, and signature.
# Automatically joins and re-wraps paragraphs to
# ensure even spacing & avoid ugly wrapping.
# Preserves signoffs.
# Signoff heuristic:
# 1-5 words ending with a comma, followed by
# 1-5 words that each start with capital letters.
# Author: Daniel Fichtinger
# License: ISC

import textwrap
import sys
import re
import argparse


def main() -> None:
    paragraph: list[str] = []
    skipping = False
    squash = True
    prev_is_parbreak = False
    out_stream = sys.stdout
    reflow = True
    width = 74
    break_long_words = False
    replace_whitespace = True
    markdown_safe = False

    in_signoff = False
    in_signature = False

    def pprint(string: str):
        if markdown_safe and (in_signoff or in_signature) and string:
            string += " \\"
        if not squash:
            print(string, file=out_stream)
        else:
            parbreak = not string
            nonlocal prev_is_parbreak
            if skipping or not (parbreak and prev_is_parbreak):
                print(string, file=out_stream)
            prev_is_parbreak = parbreak

    def wrap(text: str):
        return textwrap.wrap(
            text,
            width=width,
            break_long_words=break_long_words,
            replace_whitespace=replace_whitespace,
        )

    def flush_paragraph():
        if paragraph:
            if reflow:
                joined = " ".join(paragraph)
                wrapped = wrap(joined)
                pprint("\n".join(wrapped))
            else:
                for line in paragraph:
                    for wrapped_line in wrap(line):
                        pprint(wrapped_line)
            paragraph.clear()

    signoff_cache: str = ""

    def check_signoff(line: str) -> bool:
        if not line:
            return False
        words = line.split()
        n = len(words)
        # first potential signoff line
        if not signoff_cache and 1 <= n <= 5 and line[-1] == ",":
            return True
        # second potential line
        elif signoff_cache and 1 <= n <= 5:
            for w in words:
                if not w[0].isupper():
                    return False
            return True
        else:
            return False

    parser = argparse.ArgumentParser(
        description="Heuristic formatter for plain text email. Preserves markup, signoffs, and signature blocks.",
        epilog="""
Author    : Daniel Fichtinger
Repository: https://git.sr.ht/~ficd/mailfmt
License   : ISC
Contact   : daniel@ficd.ca
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-w",
        "--width",
        required=False,
        help="Text width for wrapping. (default: %(default)s)",
        default=width,
        type=int,
    )
    parser.add_argument(
        "-b",
        "--break-long-words",
        required=False,
        help="Break long words while wrapping. (default: %(default)s)",
        action="store_true",
    )
    parser.add_argument(
        "--no-replace-whitespace",
        required=False,
        help="Don't normalize whitespace when wrapping.",
        action="store_false",
    )
    parser.add_argument(
        "--no-reflow",
        required=False,
        help="Don't reflow lines.",
        action="store_false",
    )
    parser.add_argument(
        "--no-signoff",
        required=False,
        help="Don't preserve signoff line breaks.",
        action="store_false",
    )
    parser.add_argument(
        "--no-signature",
        required=False,
        help="Don't preserve signature block.",
        action="store_false",
    )
    parser.add_argument(
        "--no-squash",
        required=False,
        help="Don't squash consecutive paragraph breaks.",
        action="store_false",
    )
    parser.add_argument(
        "-m",
        "--markdown-safe",
        required=False,
        help="Output format safe for Markdown rendering.",
        action="store_true",
    )
    parser.add_argument(
        "-i",
        "--input",
        required=False,
        type=str,
        default="STDIN",
        help="Input file. (default: %(default)s)",
    )
    parser.add_argument(
        "-o",
        "--output",
        required=False,
        type=str,
        default="STDOUT",
        help="Output file. (default: %(default)s)",
    )
    args = parser.parse_args()
    width = args.width
    should_check_signoff = args.no_signoff
    should_check_signature = args.no_signature
    reflow = args.no_reflow
    squash = args.no_squash
    replace_whitespace = args.no_replace_whitespace
    break_long_words = args.break_long_words
    markdown_safe = args.markdown_safe

    if args.input == "STDIN":
        reader = sys.stdin
    else:
        with open(args.input, "r") as in_stream:
            reader = in_stream
    if args.output != "STDOUT":
        out_stream = open(args.output, "w")

    for line in reader:
        line = line.rstrip()
        if should_check_signoff:
            is_signoff = check_signoff(line)
            if is_signoff:
                in_signoff = True
                if not signoff_cache:
                    signoff_cache = line
                else:
                    pprint(signoff_cache)
                    pprint(line)
                    in_signoff = False
                    signoff_cache = ""
                continue
            elif not is_signoff and signoff_cache:
                paragraph.append(signoff_cache)
                signoff_cache = ""
                in_signoff = False
        if line.startswith("```"):
            flush_paragraph()
            skipping = not skipping
            pprint(line)
        elif should_check_signature and line == "--":
            flush_paragraph()
            skipping = True
            in_signature = True
            pprint("-- ")
        elif not line or re.match(
            r"^(\s+|-\s+|\+\s+|\*\s+|>\s*|#\s+|From:|To:|Cc:|Bcc:|Subject:|Reply-To:|In-Reply-To:|References:|Date:|Message-Id:|User-Agent:)",
            line,
        ):
            flush_paragraph()
            pprint(line)
        elif skipping:
            pprint(line)
        else:
            paragraph.append(line)
    else:
        if signoff_cache:
            paragraph.append(signoff_cache)
            signoff_cache = ""
        flush_paragraph()
    if out_stream is not None:
        out_stream.close()


if __name__ == "__main__":
    main()

# pyright: basic
