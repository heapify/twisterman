import yaml
import errno
from os import environ

class Container(object):
    def __init__(self):
        self.contents = {}

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
        if hasattr(name_or_file, "read"):
            self.contents = yaml.safe_load(name_or_file)
        else:
            with open(name_or_file, 'rb') as procfile:
                self.contents = yaml.safe_load(procfile)

class EnvFile(Container):
    def __init__(self, name_or_file):
        self.contents = {}
        self.contents.update(environ)
        try:
            data = name_or_file.readlines()
        except AttributeError:
            try:
                with open(name_or_file, 'rb') as envfile:
                    data = envfile.readlines()
            except IOError as e:
                if e.errno == errno.ENOENT:
                    return
                raise
        self.contents.update(dict(e.rstrip().split("=") for e in data))

