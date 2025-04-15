import argparse
import configparser
import sys
def get_config(confPath):
    config = configparser.ConfigParser()
    config.optionxform=str
    try:
        config.read(confPath)
        return config
    except Exception as e:
         log.error(e)

def parse():
    """ Parse config file, update with command line arguments
    """
    # defaults arguments
    defaults = { "jsondata" : "data.json", 
            "appName" : "MyGreatApplication", 
            "outputfile" : "OneMoreFile"}
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
        config = get_config([args.conf_file])
        defaults.update(dict(config.items("Defaults")))

    # Parse rest of arguments
    parser = argparse.ArgumentParser(
        # Inherit options from config_parser
        parents=[conf_parser]
        )
    parser.set_defaults(**defaults)

    parser.add_argument("--jsondata", nargs="+",
            help="List of json files containing PrecisionTuning profiling.")

    parser.add_argument("--appName", nargs="+",
    help="Application profiled name.")

    parser.add_argument("--outputfile", nargs="+",
    help="List of ouput names for plot files.")

    args = parser.parse_args(remaining_argv)
    return args
