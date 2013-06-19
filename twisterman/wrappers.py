import yaml

class Container(object):
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

class Procfile(Container):
    def __init__(self, name_or_file):
        try:
            self.contents = yaml.safe_load(name_or_file.read())
        except AttributeError:
            with open(name_or_file, 'rb') as procfile:
                self.contents = yaml.safe_load(procfile)

class EnvFile(Container):
    def __init__(self, name_or_file):
        try:
            data = name_or_file.readlines()
        except AttributeError:
            with open(name_or_file, 'rbU') as envfile:
                data = envfile.readlines()
        self.contents = dict(e.rstrip().split("=") for e in data.split("\n"))

