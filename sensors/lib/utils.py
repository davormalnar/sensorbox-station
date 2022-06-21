#!/usr/bin/python
import yaml

def loadConfig(path):
    with open(path, "r") as ymlfile:
        return yaml.safe_load(ymlfile)

