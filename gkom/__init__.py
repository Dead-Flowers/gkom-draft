import argparse

import moderngl_window

from .window import GkomWindowConfig

# def parse_args() -> Namespace:
#     parser = argparse.ArgumentParser(description="TODO")
#     parser.add_argument("model_name", action="store" ,required=False)
#     return parser.parse_args()


def main():
    moderngl_window.run_window_config(GkomWindowConfig)
