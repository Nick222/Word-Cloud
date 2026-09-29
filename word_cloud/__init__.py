# Copyright 2026 Nick
#
# Word Cloud plugin for Zim

import os
import re
from collections import Counter

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GdkPixbuf', '2.0')

from gi.repository import Gtk, GdkPixbuf

from wordcloud import WordCloud

from zim.plugins import PluginClass
from zim.actions import action
from zim.gui.mainwindow import MainWindowExtension


class WordCloudPlugin(PluginClass):

    plugin_info = {
        'name': _('Word Cloud'),
        'description': _('Show a cloud of frequently used words from the current notebook.'),
        'author': 'Nick',
        'version': '0.1',
    }

    plugin_preferences = (
        (
            'stop_words',
            'string',
            _('Stop words'),
            'это, как, так, что, для, при, или, его, ее, её, они, она, оно, мы, вы, меня, тебя, себя, был, была, были, быть, есть, вот, уже, еще, ещё, очень, только, также, после, перед, через, между, над, под, без, можно, нужно',
        ),
        (
            'min_word_length',
            'int',
            _('Minimum word length'),
            3,
            (1, 50),
        ),
        (
            'min_frequency',
            'int',
            _('Minimum word frequency'),
            2,
            (1, 1000),
        ),
        (
            'min_font_size',
            'int',
            _('Minimum word size'),
            10,
            (1, 200),
        ),
        (
            'max_font_size',
            'int',
            _('Maximum word size'),
            80,
            (1, 300),
        ),
    )

    def show_word_cloud(self, parent):

        window = Gtk.Window(
            title=_('Word Cloud'),
            transient_for=parent
        )

        window.set_default_size(1000, 700)
        window.set_position(Gtk.WindowPosition.CENTER)

        vbox = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=6
        )
        vbox.set_border_width(6)

        button = Gtk.Button(label=_('Refresh'))
        vbox.pack_start(button, False, False, 0)

        image = Gtk.Image()
        image.set_hexpand(True)
        image.set_vexpand(True)

        vbox.pack_start(image, True, True, 0)

        window.add(vbox)

        def refresh(button=None):
            frequencies = self._collect_words(parent)

            if not frequencies:
                image.clear()
                return

            font_path = self._find_font()

            if font_path is None:
                raise RuntimeError(
                    'No suitable Cyrillic font was found.'
                )

            cloud = WordCloud(
                width=1400,
                height=900,
                background_color='white',
                font_path=font_path,
                max_words=150,
                min_font_size=self.preferences['min_font_size'],
                max_font_size=self.preferences['max_font_size'],
                collocations=False,
            )

            cloud.generate_from_frequencies(frequencies)

            filename = '/tmp/zim-word-cloud.png'
            cloud.to_file(filename)

            pixbuf = GdkPixbuf.Pixbuf.new_from_file(filename)

            image.set_from_pixbuf(pixbuf)

        button.connect('clicked', refresh)

        window.show_all()

        refresh()

    def _collect_words(self, parent):

        notebook = parent.notebook

        if notebook is None:
            return Counter()

        root = notebook.folder.path

        words = Counter()

        for dirpath, dirnames, filenames in os.walk(root):

            dirnames[:] = [
                name for name in dirnames
                if not name.startswith('.')
            ]

            for filename in filenames:

                if not filename.endswith('.txt'):
                    continue

                path = os.path.join(dirpath, filename)

                try:
                    with open(
                        path,
                        'r',
                        encoding='utf-8'
                    ) as file:
                        text = file.read()

                except (OSError, UnicodeDecodeError):
                    continue

                # Remove technical Zim header.
                text = re.sub(
                    r"""
                    \A
                    (?:
                        (?:Content-Type|Wiki-Format|Creation-Date):[^\n]*\n
                    )+
                    [ \t\r]*\n?
                    """,
                    "",
                    text,
                    flags=re.VERBOSE,
                    count=1,
                )

                # Headings: keep the heading text.
                text = re.sub(
                    r"^\s*=+\s*(.*?)\s*=+\s*$",
                    r"\1",
                    text,
                    flags=re.MULTILINE,
                )

                # Links: keep labels, or target when there is no label.
                text = re.sub(
                    r"\[\[[^\]\n|]*\|([^\]\n]*)\]\]",
                    r"\1",
                    text,
                )

                text = re.sub(
                    r"\[\[([^\]\n]*)\]\]",
                    r"\1",
                    text,
                )

                # Images.
                text = re.sub(
                    r"\{\{\s*(?:[^{}]*[/\\])?([^{}|]+?)\."
                    r"(?:png|jpg|jpeg|gif|webp|svg)"
                    r"(?:\?[^{}]*)?\s*\}\}",
                    r"\1",
                    text,
                    flags=re.IGNORECASE,
                )

                # Inline formatting.
                text = re.sub(
                    r"(\*\*|__|//|''|~~)",
                    "",
                    text,
                )

                # Tags: @tag -> tag.
                text = re.sub(
                    r"(?<![\w@])@([^\s@]+)",
                    r"\1",
                    text,
                )

                min_length = self.preferences['min_word_length']

                found = re.findall(
                    rf'[A-Za-zА-Яа-яЁё]{{{min_length},}}',
                    text
                )

                words.update(
                    word.lower()
                    for word in found
                )

        # Stop words are entered as a comma-separated list.
        stop_words = {
            word.strip().lower()
            for word in self.preferences['stop_words'].split(',')
            if word.strip()
        }

        for word in list(words):
            if word in stop_words:
                del words[word]

        min_frequency = self.preferences['min_frequency']

        for word in list(words):
            if words[word] < min_frequency:
                del words[word]

        return words

    def _find_font(self):

        candidates = [
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf',
            '/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf',
        ]

        for path in candidates:
            if os.path.exists(path):
                return path

        return None


class WordCloudMainWindowExtension(MainWindowExtension):

    @action(_('Word Cloud'), menuhints='notebook')
    def show_word_cloud(self):
        self.plugin.show_word_cloud(self.window)
