import argparse

import polib


def fill_msgstr_with_msgid(po_file_path: str):
    po = polib.pofile(po_file_path)
    for entry in po:
        if entry.msgstr:
            continue
        entry.msgstr = entry.msgid
    return po


def main():
    parser = argparse.ArgumentParser(description="Utility scripts")
    subparsers = parser.add_subparsers(dest="command", help="Subcommands")

    parser_fill = subparsers.add_parser("fillmsgstr", help="Fill msgstr with msgid")
    parser_fill.add_argument(
        "po_file", metavar="po_file", type=str, help="Path to the .po file"
    )

    args = parser.parse_args()

    if args.command == "fillmsgstr":
        fill_msgstr_with_msgid(args.po_file).save()


if __name__ == "__main__":
    main()
