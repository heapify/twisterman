import yaml

class Procfile(object):
    def __init__(self, name_or_file):
        try:
            data = name_or_file.read()
        except AttributeError:
            with open(name_or_file, 'rb') as procfile:
                self.contents = yaml.safe_load(procfile)

    def __iter__(self):
        for key in self.contents:
            yield key

    def __getitem__(self, key):
        return self.contents[key]

    def __len__(self):
        return len(self.contents)

    def items(self):
        return self.contents.items()

    def iteritems(self):
        return self.contents.iteritems()
