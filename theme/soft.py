from main import console_clear, latency, task, last_bought, last_detected, error_count, succes_count
import asyncio
from colorama import Fore, Style
import os
import time

start_time = time.time()

async def theme() -> None:
    while True:
        console_clear()
        elapsed_time = time.time() - start_time
        hours, remainder = divmod(int(elapsed_time), 3600)
        minutes, seconds = divmod(remainder, 60)

        tag = """
███╗   ██╗███████╗██████╗ ██╗██╗   ██╗███╗   ███╗
████╗  ██║██╔════╝██╔══██╗██║██║   ██║████╗ ████║
██╔██╗ ██║█████╗  ██████╔╝██║██║   ██║██╔████╔██║
██║╚██╗██║██╔══╝  ██╔══██╗██║██║   ██║██║╚██╔╝██║
██║ ╚████║███████╗██║  ██║██║╚██████╔╝██║ ╚═╝ ██║
╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝     ╚═╝
                                                 
"""

        design = f"""
{Style.BRIGHT}╭──────────────────────────╮{Style.RESET_ALL}
{Fore.MAGENTA}      INFORMATION     {Style.RESET_ALL}
{Style.BRIGHT}├──────────────────────────┤{Style.RESET_ALL}

{Fore.CYAN}Latency: {Fore.YELLOW}{latency()} ms{Style.RESET_ALL}
{Fore.CYAN}    Task: {Fore.YELLOW}{task()}{Style.RESET_ALL}
{Fore.CYAN} Run Time: {Fore.YELLOW}{hours}h {minutes}m {seconds}s{Style.RESET_ALL}

{Style.BRIGHT}├──────────────────────────┤{Style.RESET_ALL}

{Fore.GREEN} Last Bought:  {Fore.WHITE}{last_bought}{Style.RESET_ALL}
{Fore.GREEN} Last Detected:{Fore.WHITE}{last_detected}{Style.RESET_ALL}

{Style.BRIGHT}├──────────────────────────┤{Style.RESET_ALL}

{Fore.RED} Errors:      {Fore.WHITE}{error_count}{Style.RESET_ALL}
{Fore.GREEN} Successes:   {Fore.WHITE}{succes_count}{Style.RESET_ALL}

{Style.BRIGHT}╰──────────────────────────╯{Style.RESET_ALL}
"""

        terminal_width = os.get_terminal_size().columns
        tag_lines = tag.splitlines()
        design_lines = design.splitlines()

        for line in tag_lines:
            print(line.center(terminal_width))

        for line in design_lines:
            print(line.center(terminal_width))

        await asyncio.sleep(1)
