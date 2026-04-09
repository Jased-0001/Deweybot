#! /usr/bin/env python3

raise Exception("NOT WRITTEN YET!!!!!!!!!!!! come back later :)")

from yaml import load,Loader

with open("dewey.yaml", "r") as f:
    DeweyConfig = load(stream=f, Loader=Loader)