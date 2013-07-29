import argparse 
from .config import Config
from .validator import Validator
from .builder import Builder
from .loader import Loader, ConfigLoader, ValidatorLoader

__version__ = (0, 3, 0)

__all__ = ["Config", "Validator", "Builder", "Loader", "ConfigLoader",
           "ValidatorLoader"]

def main():
    parser = argparse.ArgumentParser(
            description="Execconf config generator",
            usage="%(prog)s")
    parser.parse_args()


