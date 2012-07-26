import yaml

class SpecFile(object):
    def __init__(self, name):
        with open(name, 'rb') as procfile:
            self.contents = yaml.load(procfile)

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
