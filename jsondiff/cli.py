import argparse
import jsondiff
import sys


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("first")
    parser.add_argument("second")
    parser.add_argument("-p", "--patch", action="store_true", default=False)
    parser.add_argument("-s", "--syntax", choices=(jsondiff.builtin_syntaxes.keys()), default="compact",
                        help="Diff syntax controls how differences are rendered")
    parser.add_argument("-i", "--indent", action="store", type=int, default=None,
                        help="Number of spaces to indent. None is compact, no indentation.")
    parser.add_argument("-f", "--format", choices=("json", "yaml"), default="json",
                        help="Specify file format for input and dump")

    args = parser.parse_args()

    # pyyaml _can_ load json but is ~20 times slower and has known issues so use
    # the json from stdlib when json is specified.
    serializers = {
        "json": (jsondiff.JsonLoader(), jsondiff.JsonDumper(indent=args.indent)),
        "yaml": (jsondiff.YamlLoader(), jsondiff.YamlDumper(indent=args.indent)),
    }
    loader, dumper = serializers[args.format]

    with open(args.first, "r") as f:
        with open(args.second, "r") as g:
            jf = loader(f)
            jg = loader(g)
            if args.patch:
                x = jsondiff.patch(
                    jf,
                    jg,
                    marshal=True,
                    syntax=args.syntax
                )
            else:
                x = jsondiff.diff(
                    jf,
                    jg,
                    marshal=True,
                    syntax=args.syntax
                )

            dumper(x, sys.stdout)


if __name__ == '__main__':
    main()
