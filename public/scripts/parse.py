import argparse
import configparser
import sys

def parse():
    """ Parse config file, update with command line arguments
    """
    # defaults arguments
    defaults = { "min":0, "max":0 , "verif_text":"VERIFICATION SUCCESSFUL", "total_dyncount_text":"TOTAL_DYNCOUNT", 
            "backtrace_json_file":"data.json"}
    # Parse any conf_file specification
    conf_parser = argparse.ArgumentParser(
        description=__doc__, # printed with -h/--help
        # Don't mess with format of description
        formatter_class=argparse.RawDescriptionHelpFormatter,
        # Turn off help, so we print all options in response to -h
        add_help=False
        )
    conf_parser.add_argument("-c", "--conf_file",
                        help="Specify config file", metavar="FILE")
    args, remaining_argv = conf_parser.parse_known_args()

    if args.conf_file:
        config = configparser.ConfigParser()
        config.read([args.conf_file])
        defaults.update(dict(config.items("Defaults")))

    # Parse rest of arguments
    parser = argparse.ArgumentParser(
        # Inherit options from config_parser
        parents=[conf_parser]
        )
    parser.set_defaults(**defaults)
    parser.add_argument("--binary", help="binary file absolute path")
    parser.add_argument("--onlyProfile", help="Choose to do only profile", action='store_true')
    parser.add_argument("--directory", help="directory absolute path for all files generated by tool analysis")
    parser.add_argument("--verif_text", help="Text searched in output to verify the code executed without accuracy error")
    args = parser.parse_args(remaining_argv)
    assert args.binary, "binary absolute path is required"
    return args
