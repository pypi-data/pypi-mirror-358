import argparse
from phisher.monitor import *
from rich.console import Console
from rich.text import Text
from rich_gradient import Gradient
from rich_argparse import RichHelpFormatter

console = Console()


def parse_args():
    p = argparse.ArgumentParser(
        prog="Phisher",
        description="A tool for monitoring the certificate transparacy logs.",
        formatter_class=RichHelpFormatter
    )
    p.add_argument(
        "--notify", "-n",
        nargs=2,                         
        metavar=("CHAT_ID", "BOT_TOKEN"), 
        help="Enable notifications: provide CHAT_ID and BOT_TOKEN"
    )
    p.add_argument(
        "--log", "-l",
        action="store_true",
        help="Enable logging results to a file. By default will log to a domains.txt file."
    )
    p.add_argument(
        "--keywords", "-k",
        nargs="+",
        metavar="KEYWORDS",
        help="Space separated list of keywords"
    )
    p.add_argument(
        "--keywords-file", "-kf",
        default="keywords.txt",
        help="Path to newline-separated keywords file"
    )

    p.add_argument(
        "--format", "-f",
        choices=["csv", "txt"],
        default="txt",
        help="Choose the output format: 'csv' or 'txt'."
    )
    p.add_argument(
        "--output-file", "-o",
        default="domains.txt",
        help="File to append matching domain reports to"
    )
    return p.parse_args()

def main():
    args = parse_args()
    raw_banner = """
██████╗ ██╗  ██╗██╗███████╗██╗  ██╗███████╗██████╗
██╔══██╗██║  ██║██║██╔════╝██║  ██║██╔════╝██╔══██╗
██████╔╝███████║██║███████╗███████║█████╗  ██████╔╝
██╔═══╝ ██╔══██║██║╚════██║██╔══██║██╔══╝  ██╔══██╗
██║     ██║  ██║██║███████║██║  ██║███████╗██║  ██║
╚═╝     ╚═╝  ╚═╝╚═╝╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
    """

    colors = ["#01ff87", "#01ffd6","#01f7ff", "#008eff", "#628bff","#5e5299", "purple4","dark_magenta","dark_magenta" ,"dark_magenta" , "purple3" , "purple3" , "purple3" ,"purple3" , "deep_pink3" ,"deep_pink3" ]
    console.print(Gradient(raw_banner, colors=colors))
    log = args.log or args.output_file
    monitor = CTMonitor(args.keywords_file, args.output_file, args.format,args.keywords ,args.notify, log )
    monitor.start()

if __name__ == '__main__':
    main()