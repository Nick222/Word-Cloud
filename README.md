# Word Cloud

A [Zim](https://zim-wiki.org/) plugin that displays a word cloud based on the most frequently used words in the current notebook.

The plugin scans the notebook's `.txt` pages, removes Zim markup and technical headers, filters stop words, and generates a visual word cloud.

## Features

* Scans the entire active Zim notebook
* Counts words by frequency
* Supports Russian and English words
* Removes Zim technical headers
* Converts Zim links to their visible text
* Removes formatting markup
* Preserves heading text
* Removes the `@` from Zim tags
* Configurable stop-word list
* Configurable minimum word length
* Configurable minimum word frequency
* Configurable minimum and maximum font size
* Refreshes the cloud without restarting Zim

## Requirements

* Zim
* Python 3
* [`wordcloud`](https://github.com/amueller/word_cloud)

On Ubuntu, the required Python package can be installed with:

```bash
sudo apt install python3-wordcloud
```

## Installation

Copy the plugin directory to the Zim user plugin directory:

```text
~/.local/share/zim/plugins/word_cloud/
```

The directory should contain:

```text
word_cloud/
└── __init__.py
```

Then enable **Word Cloud** in:

**Edit → Preferences → Plugins**

The command **Word Cloud** is available from the notebook menu.

## Settings

The plugin provides the following settings.

### Stop words

The stop-word list is stored in **Zim's plugin preferences**. It is not stored in a separate file.

Words are entered as a **comma-separated list**.

The list can contain a large number of words, so it is convenient to prepare the list as plain text and paste it into the setting.

For example:

```text
это, как, так, что, для, при, или, его, ее, ещё, уже, только
```

Spaces after commas are ignored.

### Minimum word length

Words shorter than this value are ignored.

### Minimum word frequency

Words occurring fewer times than this value are ignored.

### Minimum word size

Minimum font size used in the generated cloud.

### Maximum word size

Maximum font size used in the generated cloud.

## Refresh

When the word cloud window is opened, the plugin reads the notebook and creates the cloud automatically.

Each time **Refresh** is pressed, the plugin:

1. Reads all `.txt` pages in the current notebook again
2. Processes the Zim markup
3. Counts the words
4. Applies the stop-word and frequency filters
5. Generates a new word cloud

The plugin does **not** use a separate word index or cache.

For large notebooks, refreshing the cloud may therefore take some time.

## How it works

The plugin reads Zim page files directly from the current notebook.

Before counting words, it removes or converts common Zim markup:

* technical headers such as `Content-Type`, `Wiki-Format`, and `Creation-Date`
* page links
* headings markup
* image markup
* inline formatting
* the `@` prefix from tags

The resulting text is then tokenized and counted.

The word cloud is generated with the Python `wordcloud` library.

## License

MIT License

Copyright 2026 Nick
