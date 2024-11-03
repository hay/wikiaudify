from argparse import ArgumentParser
from loguru import logger
from wikiaudify.config import Config
from wikiaudify.generator import Generator
import sys

logger.remove()

parser = ArgumentParser(description = "Generate an audio summary of a Wikipedia article")
parser.add_argument("-a", "--article", help = "Article you want the audio summary to be about")
parser.add_argument("-c", "--config", help = "Path to a TOML file with configuration")
parser.add_argument("-na", "--no-audio", help = "Don't generate audio output", action = "store_true")
parser.add_argument("-nt", "--no-transcript", help = "Don't generate an audio transcript", action = "store_true")
parser.add_argument("-o", "--out", help = "Path of output MP3 file", default = "summary.mp3")
parser.add_argument("-ot", "--out-transcript", help = "Path of output transcript", default = "summary.txt")
parser.add_argument("-q", "--question", help = "User question that will be included in the summary")
parser.add_argument("-v", "--verbose", help = "Show debug information", action = "store_true")

args = parser.parse_args()

if args.verbose:
    logger.add(sys.stderr, level = "DEBUG")
    logger.debug("Verbose logging enabled")
    logger.debug(f"Arguments: {args}")

if (not args.config) or (not args.article):
    parser.print_help()
    sys.exit()

config = Config(args.config)
generator = Generator(config)
generator.create_conversation(args.article, args.question)

if not args.no_audio:
    generator.render_audio()
    generator.export_audio(args.out)

if not args.no_transcript:
    generator.export_transcript(args.out_transcript)