from torngas.utils.iterutils import dictincr
import traceback


def tryall(context, prefix=None):
    """
    Tries a series of functions and prints their results. 
    `context` is a dictionary mapping names to values; 
    the value will only be tried if it's callable.
    
        >>> tryall(dict(j=lambda: True))
        j: True
        ----------------------------------------
        results:
           True: 1

    For example, you might have a file `test/stuff.py` 
    with a series of functions testing various things in it. 
    At the bottom, have a line:

        if __name__ == "__main__": tryall(globals())

    Then you can run `python test/stuff.py` and get the results of 
    all the tests.
    """
    context = context.copy() # vars() would update
    results = {}
    for (key, value) in context.iteritems():
        if not hasattr(value, '__call__'):
            continue
        if prefix and not key.startswith(prefix):
            continue
        print key + ':',
        try:
            r = value()
            dictincr(results, r)
            print r
        except:
            print 'ERROR'
            dictincr(results, 'ERROR')
            print '   ' + '\n   '.join(traceback.format_exc().split('\n'))

    print '-' * 40
    print 'results:'
    for (key, value) in results.iteritems():
        print ' ' * 2, str(key) + ':', value


def autoassign(self, locals):
    """
    Automatically assigns local variables to `self`.
    
        >>> self = storage()
        >>> autoassign(self, dict(a=1, b=2))
        >>> self
        <Storage {'a': 1, 'b': 2}>
    
    Generally used in `__init__` methods, as in:

        def __init__(self, foo, bar, baz=1): autoassign(self, locals())
    """
    for (key, value) in locals.iteritems():
        if key == 'self':
            continue
        setattr(self, key, value)


import json, re
import locale


def strip_html(data):
    if not data:
        return
    p = re.compile(r'<[^<]*?/?>')
    return p.sub('', data)


def add_commas(val, as_data_type='int', the_locale=locale.LC_ALL):
    locale.setlocale(the_locale, "")
    if as_data_type == 'int':
        return locale.format('%d', int(val), True)
    elif as_data_type == 'float':
        return locale.format('%f', float(val), True)
    else:
        return val


def get_time_string(str):
    if str == "N/A":
        return str

    parts = str.split("/")
    isPM = parts[0].find('am') == -1
    if not isPM:
        parts[0] = parts[0].replace("am", "")

    parts[1] = parts[1].replace("c", "")
    if (len(parts[0]) >= 3):
        if (len(parts[0]) == 4):
            parts[0] = parts[0][0:2] + ":" + parts[0][2:]
        else:
            parts[0] = parts[0][:1] + ":" + parts[0][1:]
    if (len(parts[1]) >= 3):
        if (len(parts[1]) == 4):
            parts[1] = parts[1][0:2] + ":" + parts[1][2:]
        else:
            parts[1] = parts[1][:1] + ":" + parts[1][1:]

    if isPM:
        time = parts[0] + "/" + parts[1] + "c"
    else:
        time = parts[0] + "am/" + parts[1] + "c"

    return time


class Pluralizer():
    #
    # (pattern, search, replace) regex english plural rules tuple
    #
    rule_tuple = (
        ('[ml]ouse$', '([ml])ouse$', '\\1ice'),
        ('child$', 'child$', 'children'),
        ('booth$', 'booth$', 'booths'),
        ('foot$', 'foot$', 'feet'),
        ('ooth$', 'ooth$', 'eeth'),
        ('l[eo]af$', 'l([eo])af$', 'l\\1aves'),
        ('sis$', 'sis$', 'ses'),
        ('man$', 'man$', 'men'),
        ('ife$', 'ife$', 'ives'),
        ('eau$', 'eau$', 'eaux'),
        ('lf$', 'lf$', 'lves'),
        ('[sxz]$', '$', 'es'),
        ('[^aeioudgkprt]h$', '$', 'es'),
        ('(qu|[^aeiou])y$', 'y$', 'ies'),
        ('$', '$', 's')
    )

    def regex_rules(self, rules=rule_tuple):
        for line in rules:
            pattern, search, replace = line
            yield lambda word: re.search(pattern, word) and re.sub(search, replace, word)

    def plural(self, noun):
        for rule in self.regex_rules():
            result = rule(noun)
            if result:
                return result


if __name__ == "__main__":
    import doctest

    doctest.testmod()

