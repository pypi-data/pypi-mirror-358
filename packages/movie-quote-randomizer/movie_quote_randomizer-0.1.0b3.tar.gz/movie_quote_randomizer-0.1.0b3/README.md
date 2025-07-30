# Movie Quote Randomizer

## Description

Welcome to the Python package no one needed or asked for: Movie Quote Randomizer.

Movie Quote Randomizer provides an API to randomly select quotes from your favorite movie, TV show, video game, or whatever medium suits your fancy. You can then import this package into your project, provide your own JSON quotes database (or use the built-in one if you're lazy), and in just a few lines of Python randomly select a new quote every time.

Why would you want to do this? Honestly I don't really know.

Maybe you have a school project where you are required write a command line tool that prints randomly selected movie quotes to the console. Good news. Install this package and call into it from your `main()`, and you're done. A+ this semester. You're welcome.

Maybe you want to flatter your boss by having the project you're developing at work periodically print their pearls of "wisdom" in the log files. Happy to help.

Perhaps you work for the government and you need to provide a "business justification" for the most trivial things. Ron Swanson quotes fit the bill here nicely.

Personally, I like the idea of adding an easter egg that, when activated, prints randomly selected dialogue from the long lost E.T. videogame for NES.

Look, how you use this isn't really my problem. That sounds more like a *you* problem. I've already done the hard work for you.

## Installation

You can install this package from PyPI via `pip`:

```console
pip install movie-quote-randomizer
```

However, as it's a library that's intended for use from another project, you'll probably want to add `movie-quote-randomizer` to your project's `install_requires`.

## Usage

Simply import `MQRandomizer` from `mq_randomizer`, and instantiate it. If you have your own JSON quote database, use that. Otherwise you'll get quotes from the 1995 Film, Hackers.

The randomizer object returns `MQuote` objects.

You can work with `MQuote` objects in three ways:

**They are proper Python dictionaries that look like:**
```python
{
  'quote_type': 'single',
  'characters': ['Nikon'],
  'lines': [{'Nikon': "You're in the butter zone now, baby."}],
  'media_title': 'Hackers',
  'media_type': 'movie',
  'year': 1995
}
```

**They're Python objects with several useful properties defined**:
- `characters: list[str]`
- `lines: list[dict[str, str]]`
- `media_title: str`
- `media_type: str`
- `year: int`

**Also they're easily converted to a string for easy logging/console printing:**

```ipython
In [7]: str(generator.random_quote())
Out[7]: 'Dade Murphy: The pool on the roof must have a leak.'
```

## JSON Structure

Here's an abbreviated JSON dictionary:

```json
{
  "meta": {
    "version": 1,
    "media_title": "Hackers",
    "media_type": "movie",
    "year": 1995,
    "description": "Quotes from the movie Hackers"
  },
  "quotes": [
    {
      "quote_type": "single",
      "characters": [
        "The Plague"
      ],
      "lines": [
        {
          "The Plauge": "The Plague: There is no right and wrong. There's only fun and boring."
        }
      ]
    },
    {
      "quote_type": "dialogue",
      "characters": [
        "Dade Murphy",
        "Mrs. Murphy"
      ],
      "lines": [
        {
          "Dade Murphy": "I'm taking over a TV network."
        },
        {
          "Mrs. Murphy": "Finish up, honey, and get to sleep."
        }
      ]
    }
  ]
}
```

Note there are two quote types: "single" where there's a single line by a single character, and "dialogue" where there are mutliple lines between two or more characters.

## Example

Here's an end-to-end example:

```python
from mq_randomizer import MQRandomizer

def main():
  randomizer = MQRandomizer("path/to/quotes.json")
  quote = randomizer.random_quote()

  print("Media title: "+quote.media_title)
  print("Media type: "+quote.media_type)
  print("Year: "+quote.year)
  for character in quote.characters:
    print(character)

  print(str(quote))
```

## Unattributed Quotes

In some cases the quotes aren't associated with a particular character or even the narrator. Take this from the opening sequence of the video game Zero Wing (1989):

> In A.D. 2101
>
> War was beginning.

In this case the "character" should be the special value `"__none__"` which will tell the `MQuote` object to not render the character's name.

Here's some JSON:

```json
{
  "meta": {
    "version": 1,
    "media_title": "Zero Wing",
    "media_type": "Video Game",
    "year": 1989,
    "description": "Quotes from the video game Zero Wing, noted for poorly translated subtitles that spawned an internet meme."
  },
  "quotes": [
    {
      "quote_type": "dialogue",
      "characters": [
        "__none__"
      ],
      "lines": [
        { "__none__": "In A.D. 2101" },
        { "__none__": "War was beginning."}
      ]
    },
  ]
}

```

```ipython
In [19]: str(q)
Out[19]: 'In A.D. 2101\nWar was beginning.'

In [20]: print(str(q))
In A.D. 2101
War was beginning.
```

