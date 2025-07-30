import argparse


def main() -> None:
    from logfire_lsp import __version__, server  # noqa: PLC0415

    parser = argparse.ArgumentParser(prog='logfire-lsp')
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}',
    )
    parser.parse_args()

    server.start()


if __name__ == '__main__':
    main()
