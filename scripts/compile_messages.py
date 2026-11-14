#!/usr/bin/env python3
"""
Pure-Python fallback for ``manage.py compilemessages``.

Django's compilemessages needs GNU gettext's ``msgfmt`` binary, which is often
missing in sandboxes and minimal VMs (and may not be installable without root).
This script compiles every ``locale/*/LC_MESSAGES/*.po`` into the matching
``.mo`` file using only the standard library.

Usage: compile_messages.py <locale dir> [<locale dir> ...]
"""

import ast
import struct
import sys
from pathlib import Path


def parse_po(path):
    """Return {msgid: msgstr} in the key/value format expected in .mo files."""
    messages = {}
    entry = {}
    fuzzy = False
    section = None

    def flush():
        nonlocal entry, fuzzy
        if "msgid" in entry:
            msgid = entry["msgid"]
            is_header = msgid == ""
            if "msgid_plural" in entry:
                msgid = msgid + "\0" + entry["msgid_plural"]
                forms = [entry[k] for k in sorted(k for k in entry if k.startswith("msgstr["))]
                msgstr = "\0".join(forms)
                translated = any(forms)
            else:
                msgstr = entry.get("msgstr", "")
                translated = bool(msgstr)
            if "msgctxt" in entry:
                msgid = entry["msgctxt"] + "\x04" + msgid
            # Like msgfmt: skip untranslated and fuzzy entries, but always keep
            # the header (it carries the charset and plural rules).
            if is_header or (translated and not fuzzy):
                messages[msgid] = msgstr
        entry = {}
        fuzzy = False

    def entry_complete():
        return any(k == "msgstr" or k.startswith("msgstr[") for k in entry)

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("#"):
            # Comments (incl. flags and obsolete "#~" entries) precede the entry
            # they belong to, so a comment after a msgstr starts a new entry.
            if entry_complete():
                flush()
            if line.startswith("#,") and "fuzzy" in line:
                fuzzy = True
            continue
        if line.startswith('"'):
            if section is None:
                raise ValueError(f"{path}: unexpected string continuation: {raw_line!r}")
            entry[section] += ast.literal_eval(line)
            continue
        keyword, _, value = line.partition(" ")
        if keyword in ("msgctxt", "msgid") and entry_complete():
            flush()
        if not (
            keyword in ("msgctxt", "msgid", "msgid_plural", "msgstr")
            or keyword.startswith("msgstr[")
        ):
            raise ValueError(f"{path}: unsupported line: {raw_line!r}")
        section = keyword
        entry[section] = ast.literal_eval(value)
    flush()
    return messages


def write_mo(messages, path):
    """Write a GNU .mo file (same layout as CPython's Tools/i18n/msgfmt.py)."""
    keys = sorted(messages)
    ids = b""
    strs = b""
    offsets = []
    for key in keys:
        key_bytes = key.encode("utf-8")
        value_bytes = messages[key].encode("utf-8")
        offsets.append((len(ids), len(key_bytes), len(strs), len(value_bytes)))
        ids += key_bytes + b"\0"
        strs += value_bytes + b"\0"

    count = len(keys)
    keystart = 7 * 4 + 16 * count
    valuestart = keystart + len(ids)
    koffsets = []
    voffsets = []
    for id_off, id_len, str_off, str_len in offsets:
        koffsets += [id_len, id_off + keystart]
        voffsets += [str_len, str_off + valuestart]

    output = struct.pack(
        "Iiiiiii",
        0x950412DE,  # magic
        0,  # version
        count,
        7 * 4,  # start of key index
        7 * 4 + count * 8,  # start of value index
        0,  # size of hash table
        0,  # offset of hash table
    )
    output += struct.pack(f"{len(koffsets)}i", *koffsets)
    output += struct.pack(f"{len(voffsets)}i", *voffsets)
    output += ids + strs
    path.write_bytes(output)


def main(argv):
    if len(argv) < 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    for locale_dir in map(Path, argv[1:]):
        for po_path in sorted(locale_dir.glob("*/LC_MESSAGES/*.po")):
            mo_path = po_path.with_suffix(".mo")
            write_mo(parse_po(po_path), mo_path)
            print(f"processing file {po_path.name} in {po_path.parent}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
