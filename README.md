# wikiaudify
> Generate audio summaries of Wikipedia articles using OpenAI and ElevenLabs

## Introduction
This was a hackathon project made during the [Wikimedia NL Mini Hackathon 2024](https://nl.wikimedia.org/wiki/Mini_Hackathon_November_2024) to generate audio summaries like the ones from [NotebookLM](https://blog.google/technology/ai/notebooklm-audio-overviews/). Obviously it's not as good as that one, but it makes quite enjoyable fun short audio conversations.

## Install
What you'll need:
* An [OpenAI API key](https://openai.com/api/)
* An [ElevenLabs API key](https://elevenlabs.io/api)
* Python 3.13+ (it probably works with older versions too, but no guarantees)

There is an option to use a local LLM ([like Ollama](https://ollama.com/)) but i didn't get very good results, but you could try to make it work!

To use this script:
1. Clone this repo
```bash
git clone https://github.com/hay/wikiaudify.git
```

2. Make a virtual environment and install the `requirements.txt`
```bash
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```

3. Copy the `example-config.toml` to a new file (e.g. `test.toml`) and fill in your API keys and other details

4. Try running it from the command line like this:
```bash
python generate.py -a "Grilled_Cheese" -q "At what temperature will my cheese melt?" -c test.toml
```

Note that the Wikipedia article you give with the `-a` option should have underscores, e.g. the path in the URL of the article.

By default this will generate two files in the root of this project: a `summary.mp3` containing the summary and a `summary.txt` with a transcription.

## Troubleshooting
If you add the `-v` (verbose) flag `audio2text` will give much more debug information.

## All options
You'll get this when doing `python generate.py -h`

```bash
usage: generate.py [-h] [-a ARTICLE] [-c CONFIG] [-na] [-nt] [-o OUT]
                   [-ot OUT_TRANSCRIPT] [-q QUESTION] [-v]

Generate an audio summary of a Wikipedia article

options:
  -h, --help            show this help message and exit
  -a, --article ARTICLE
                        Article you want the audio summary to be about
  -c, --config CONFIG   Path to a TOML file with configuration
  -na, --no-audio       Don't generate audio output
  -nt, --no-transcript  Don't generate an audio transcript
  -o, --out OUT         Path of output MP3 file
  -ot, --out-transcript OUT_TRANSCRIPT
                        Path of output transcript
  -q, --question QUESTION
                        User question that will be included in the summary
  -v, --verbose         Show debug information
```

## License
MIT &copy; [Hay Kranen](http://www.haykranen.nl)