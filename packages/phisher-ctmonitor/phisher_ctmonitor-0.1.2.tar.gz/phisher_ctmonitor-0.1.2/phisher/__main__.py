import argparse
from phisher.monitor import *
from rich.console import Console
from rich.text import Text
import os
from rich_gradient import Gradient
from rich_argparse import RichHelpFormatter

console = Console()


def parse_args():
    p = argparse.ArgumentParser(
        prog="Phisher",
        description="""
        Phisher is a real-time tool designed to monitor Certificate Transparency logs. 
        By default, it displays all newly discovered domains directly in your console. 
        You can also filter the results using specific keywords, set up instant Telegram 
        notifications whenever there's a match, and save certificate details to a file 
        in plain text or CSV format. If you don’t specify keywords or provide a keyword 
        file, Phisher will simply show every domain it finds.
        """,
        formatter_class=RichHelpFormatter
    )
    p.add_argument(
        "--keywords", "-k",
        nargs="+",
        metavar="KEYWORDS",
        help="Provide inline keywords (space-separated) to filter matching domains. Supports wildcards using '*', e.g., 'dhl*com'."
    )
    p.add_argument(
        "--keywords-file", "-kf",
        default="keywords.txt",
        help="Path to a newline-separated file of keywords. Wildcards supported."
    )
    p.add_argument(
        "--notify", "-n",
        nargs=2,                         
        metavar=("CHAT_ID", "BOT_TOKEN"), 
        help="Enable Telegram notifications. Requires your Telegram chat ID and bot token."
    )
    p.add_argument(
        "--log", "-l",
        action="store_true",
        help="Enable logging of certificate data. Defaults to 'domains.txt'."
    )
    p.add_argument(
        "--format", "-f",
        choices=["csv", "txt"],
        default="txt",
        help="Choose output format: plain text or CSV. Default is 'txt'."
    )
    p.add_argument(
        "--output-file", "-o",
        default="domains.txt",
        help="Custom path to the log file. If omitted, defaults to 'domains.txt'."
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