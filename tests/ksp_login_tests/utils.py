from collections import defaultdict

from django.utils.six.moves import html_parser


class IDAttributeCounter(html_parser.HTMLParser):
    """Collects the values of all "id" attributes in a counter.
    """
    def __init__(self, *args, **kwargs):
        html_parser.HTMLParser.__init__(self, *args, **kwargs)
        self.id_counter = defaultdict(int)

    def handle_starttag(self, tag, attrs):
        ids = [value for name, value in attrs if name == "id"]
        assert len(ids) <= 1, "Invalid HTML: multiple 'id' attributes in a single element"
        try:
            self.id_counter[ids[0]] += 1
        except IndexError:
            pass
