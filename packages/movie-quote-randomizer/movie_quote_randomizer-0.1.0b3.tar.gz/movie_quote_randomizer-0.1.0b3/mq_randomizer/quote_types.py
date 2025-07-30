class MQuote(dict):
    UNATTRIBUTED = "__none__"

    def __init__(self, quote_dict: dict, media_title: str, media_type: str, year: int):
        super().__init__()
        self.update(quote_dict)
        self["media_title"] = media_title
        self["media_type"] = media_type
        self["year"] = year

    @property
    def characters(self) -> list[str]:
        """
        Get the list of characters in the quote.

        Returns
        -------
        list[str]
            A list of character names associated with the quote.
        """
        return self["characters"]

    @property
    def lines(self) -> list[dict[str, str]]:
        """
        Get the list of lines in the quote.

        Returns
        -------
        list[dict[str, str]]
            A list of dictionaries representing each line of the quote.
        """
        lines = self["lines"]
        return lines

    @property
    def media_title(self) -> str:
        """
        Get the title of the media source.

        Returns
        -------
        str
            The title of the movie, TV show, or other media source.
        """
        return self["media_title"]

    @property
    def media_type(self) -> str:
        """
        Get the type of media source.

        Returns
        -------
        str
            The type of media (e.g., "movie", "TV show", "video game").
        """
        return self["media_type"]

    @property
    def year(self) -> int:
        """
        Get the release year of the media.

        Returns
        -------
        int
            The year the media was released.
        """
        return self["year"]

    def __str__(self):
        """
        Generate a string representation of the quote.

        Returns
        -------
        str
            A formatted string containing the quote's lines and characters.
        """
        lines = []
        for quote_dict in self.lines:
            for k, v in quote_dict.items():
                if k != self.UNATTRIBUTED:
                    line = f"{k}: {v}"
                else:
                    line = f"{v}"
                lines.append(line)
        _str = "\n".join(lines)
        return _str
