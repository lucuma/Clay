from collections import defaultdict


__all__ = ("MultiDict", )


class MultiDict(defaultdict):
    """A :class:`MultiDict` is a defaultdict subclass customized to deal with
    multiple values for the same key.
    """

    def __init__(self, *mapping):
        super().__init__(list)
        for key, value in mapping or []:
            self[key].append(value)

    def __repr__(self):
        return f"<Multidict {self.keys()} >"

    def get(self, key, default=None, *, index=-1):
        """Return the first value of the key of `default` one if the key
        doesn't exist.

        Arguments are:

            key (str):
                The key to be looked up.

            default (any):
                The default value to be returned if the key can't
                be looked up.  If not further specified `None` is returned.

            index (integer):
                Which of the values to take. By default is -1, so the last one
                is chosen.

        """
        values = self[key]
        value = values[index] if values else None
        if value is None:
            return default
        return value

    def getall(self, key):
        """Return the list of items for a given key. If that key is not in the
        :class:`MultiDict`, the return value will be an empty list.

        Arguments are:

            key (str):
                The key to be looked up.

        """
        return defaultdict.__getitem__(self, key)

    # shallow compatibility with other Request objects
    # Aliases to mimic other multi-dict APIs (Django, Flask, etc.)
    getfirst = get
    getone = get
    getlist = getall
