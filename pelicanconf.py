AUTHOR = "Erwin Janssen"
SITENAME = "Erwin Janssen"
SITEURL = ""

PATH = "content"

TIMEZONE = "Europe/Amsterdam"

DEFAULT_LANG = "en"

ARTICLE_URL = "post/{slug}.html"
ARTICLE_SAVE_AS = ARTICLE_URL

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (
    ("Pelican", "https://getpelican.com/"),
    ("Python.org", "https://www.python.org/"),
    ("Jinja2", "https://palletsprojects.com/p/jinja/"),
    ("You can modify those links in your config file", "#"),
)

# Social widget
SOCIAL = (
    ("GitHub", "https://github.com/ErwinJanssen/"),
    ("Mastodon", "https://mastodon.social/@erwinjanssen"),
    ("LinkedIn", "https://www.linkedin.com/in/ejjanssen/"),
)

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True

PLUGINS = [
    "pelican.plugins.pandoc_reader",
]

PANDOC_ARGS = [
    # This allows the headings in the Markdown document to be level 1 headings,
    # which then convert to `<h2>` headings in the HTML output. This in turn
    # makes it easier to convert the document to a PDF using Pandoc. Check
    # https://github.com/jgm/pandoc/issues/5071 for more info.
    "--base-header-level=2",
]
