import argparse
import os
import configparser
import sys

class EnvInterpolation(configparser.BasicInterpolation):
    """Interpolation which expands environment variables in values."""
    def before_get(self, parser, section, option, value, defaults):
        return os.path.expandvars(value)

def get_config(confPath):
    config = configparser.ConfigParser(interpolation=EnvInterpolation())
    config.optionxform=str
    try:
        config.read(confPath)
        return config
    except Exception as e:
         log.error(e)

def parse(defaults):
    """ Parse config file, update with command line arguments
    """
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
        assert os.path.exists(args.conf_file)
        config = get_config([args.conf_file])
        defaults.update(dict(config.items("Defaults")))

    # Parse rest of arguments
    parser = argparse.ArgumentParser(
        # Inherit options from config_parser
        parents=[conf_parser]
        )
    parser.set_defaults(**defaults)
    return parser,remaining_argv

def parseProfiling():
    # defaults arguments
    defaults = { "profilefile":"profile.json" , "verif_text":"VERIFICATION SUCCESSFUL",
            "params":"","outputfile":"stdoutAndstderr", "movePLTdir":False, "onlyProfile":False,
            "onlyGenStrat":False, "onlyApplyingStrat":False, "execAllStrat":False,
            "ptunerdir":"./"}
    parser,remaining_argv = parse(defaults)
    parser.add_argument("--binary", help="""binary file absolute or relative path:
                        DONT FORGET ./ if in same directory!""")

    parser.add_argument("--params", help="""This is for precising one application
                        parameter absolute or relative path.
                        (ex: ./inputs-2d-regt). Several arguments
                        should be written in between quotes: \"arg1 arg2 ...\" """)

    parser.add_argument("--ptunerdir",
            help="directory absolute path for all files generated and read by tool analysis")

    parser.add_argument("--stratfiles", nargs="+",
            help="List of json files containing either generated strategies and/or strategies to apply.")

    parser.add_argument("--outputfile",
    help="""Stdout and stderr are dumped into:
    /path/to/outputdirectory/outputfile_profile.txt or ./ptuner_stratCOUNT_DATE_outputfile.txt""")

    parser.add_argument("--profilefile",
    help="""Profile phase dumps the JSON into profilefile into outputdir,
    Applying strat phase read into to create strat files.""")

    parser.add_argument("--onlyProfile",
    help="""Choose to do only profiling no strategy generation,
    no applying strategy. One execution.""",
    action='store_true')

    parser.add_argument("--onlyGenStrat",
    help="""Choose to do only strategies generation based on existing profiling.
    No application execution here.""",
    action='store_true')

    parser.add_argument("--onlyApplyingStrat",
            help="Choose to do only applying strategy. These MUST already have been generated.",
    action='store_true')

    parser.add_argument("--movePLTdir",
            help="Choose to move plt directories according to strategy number.",
    action='store_true')

    parser.add_argument("--execAllStrat",
    help="Exec all strategies even when a valid one is found",
    action='store_true')

    parser.add_argument("--verif_text",
            help="Text searched in output to verify the code executed without accuracy error")

    args = parser.parse_args(remaining_argv)
    assert args.binary, "binary absolute path is required"
    return args

def parseMergeCSVintoTrace():
    defaults = {"directory":"./profile/", "dumpdir":"./", "check":False}
    parser,remaining_argv = parse(defaults)

    parser.add_argument("--directory",
            help="directory absolute path containing all csv files to merge.")

    parser.add_argument("--dumpdir",
            help="directory absolute path to dump the merged trace.")

    parser.add_argument("--check",
    help="Check if missing any indexes",
    action='store_true')

    args = parser.parse_args(remaining_argv)
    return args

def parseAnalyzing(verbose=1):
    defaults = { "profilefile":"profile.json" ,
                "verif_text":"AMReX (20.01-36-gfee20d598e0a-dirty) finalized",
                "params":"", "dumpdir":"./", "mergedtracefile":"mergeCSVintoTrace.trace",
                "strategy":"SLOC","filtering":False,"maxdepth":int(1),"windowSize":int(2),
                "threshold":int(100000)
                }
    parser,remaining_argv = parse(defaults)
    parser.add_argument("--binary", help="""binary file absolute or relative path:
                        DONT FORGET ./ if in same directory!""")

    parser.add_argument("--profilefile",
    help="""Profile phase dumps the JSON into profilefile into outputdir,
    Applying strat phase read into to create strat files.""")

    parser.add_argument("--readdir",
            help="directory absolute path for all files read by tool analysis")

    parser.add_argument("--params", help="""This is for precising one application
                        parameter absolute or relative path.
                        (ex: ./inputs-2d-regt). Several arguments
                        should be written in between quotes: \"arg1 arg2 ...\" """)

    parser.add_argument("--mergedtracefile",
            help="Use merge CSV into trace file to build clusters.")

    parser.add_argument("--strategy",
            help="""Strategy MultiStep to test: SLOC BT -C -Cf -> """)

    parser.add_argument("--dumpdir",
            help="directory absolute path for all files generated by tool analysis")

    parser.add_argument("--filtering",
    help="""If True, do clustering on SLOC (filter) before clustering on BACKTRACE when doing
            BT cluster step.""", action='store_true')

    parser.add_argument("--maxdepth",
            help="Clustering algorithm are hierarchical: pick a max depth.")

    parser.add_argument("--threshold",
            help="""Clustering algorithm result depend on graph edges,
            which depends on threshold (delta) for max timstamp difference.""")

    parser.add_argument("--windowSize",
            help="""Clustering algorithm result depend on graph edges,
            which depends on window size: how many nodes are allowed to have edges together?""")

    args = parser.parse_args(remaining_argv)
    if verbose>1:
        print(args)
    assert args.binary, "binary absolute path is required"
    return args
