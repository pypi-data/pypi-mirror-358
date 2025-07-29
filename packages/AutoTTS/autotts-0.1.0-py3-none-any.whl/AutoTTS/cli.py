import argparse
from .core import speak
from easytts.config_gui import main as config_gui

def cli():
    parser = argparse.ArgumentParser(description="EasyTTS CLI")
    subparsers = parser.add_subparsers(dest="command")

    say_cmd = subparsers.add_parser("say")
    say_cmd.add_argument("text", help="Text to speak")

    subparsers.add_parser("config")
    subparsers.add_parser("voices")

    args = parser.parse_args()

    if args.command == "say":
        speak(args.text)
    elif args.command == "config":
        config_gui()
    elif args.command == "voices":
        import voices
        voices.main()
    else:
        parser.print_help()

if __name__ == "__main__":
    cli()