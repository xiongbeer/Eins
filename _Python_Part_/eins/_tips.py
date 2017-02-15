# coding:utf-8
from colorama import Fore, Back, Style, init

colormap = {
    'RED':Fore.RED,
    'BLUE':Fore.BLUE,
    'GREEN':Fore.GREEN,
}

def INFO(context, color):
    return colormap[color]+context+Fore.RESET
