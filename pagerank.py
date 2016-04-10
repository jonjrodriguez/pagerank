#!/usr/bin/env python

import argparse, os, sys
from math import log

from bs4 import BeautifulSoup

class PageRank(object):
    def __init__(self, F):
        self.F = F
        self.indexes = {}
        self.n = 0
        self.epsilon = 0

    def rank(self, docsPath):
        files = self.getFiles(docsPath)

        self.initializeScore(files)

        weight = self.calculateWeight(files)

        self.calculatePageRank(files, weight)

        self.printSorted(files)

    def calculatePageRank(self, files, weight):
        changed = True
        while changed:
            changed = False
            for key, file in enumerate(files):
                total = sum(files[i]['score'] * weight[key][i] for i in range(self.n))

                file['newScore'] = ((1-self.F) * file['base']) + (self.F * total)

                if abs(file['newScore'] - file['score']) > self.epsilon:
                    changed = True

            for file in files:
                file['score'] = file['newScore']

    def calculateWeight(self, files):
        weight = [[0.]*self.n for _ in range(self.n)]
        for key, file in enumerate(files):
            outlinks = self.getOutLinks(file['path'], file['name'])
            if (not len(outlinks)):
                for i in range(self.n):
                    weight[i][key] = 1./self.n
            else:
                for link in outlinks:
                    weight[self.getIndex(link)][key] += self.calculateLinkWeight(link)

                total = sum(zip(*weight)[key])

                for i in range(self.n):
                    weight[i][key] = weight[i][key]/total

        return weight

    def getIndex(self, link):
        return self.indexes.get(link.get('href').lower())

    def calculateLinkWeight(self, link):
        weighted = ['h1', 'h2', 'h3', 'h4', 'em', 'b']
        
        if link.find_parent(weighted):
            return 2

        return 1

    def initializeScore(self, files):
        for file in files:
            file['base'] = log(self.getWordCount(file['path'], file['name']), 2)

        total = sum(f['base'] for f in files)

        for file in files:
            file['score'] = file['base'] = file['base']/total

    def getFiles(self, path):
        files = []
        for path, _, filenames in os.walk(path):
            files += [{
                'path': path, 
                'name': name,
                'score': 0,
                'base': 0,
                'newScore': 0
            } for name in filenames if not name[0] == '.']

        self.indexes = dict((f['name'].lower(), i) for i, f in enumerate(files))
        self.n = len(files)

        if (not self.n):
            sys.exit("Please select a document path with valid files");

        self.epsilon = 0.01/self.n

        return files

    def printSorted(self, files):
        for file in sorted(files, key=lambda k: k['score'], reverse=True):
            print file['name'], file['score']

    def getOutLinks(self, path, name):
        soup = self.getSoup(path, name)

        outlinks = []
        for link in soup.find_all('a'):
            if link.has_attr('href'):
                if self.getIndex(link) is not None:
                    outlinks.append(link)

        return outlinks

    def getWordCount(self, path, name):
        soup = self.getSoup(path, name)

        return len(soup.get_text().split())

    def getSoup(self, path, name):
        path = os.path.join(path, name)

        return BeautifulSoup(open(path), 'html.parser')


def main():
    parser = argparse.ArgumentParser(description='Calculate the weighted PageRank for html documents')

    parser.add_argument('-docs', metavar="DOCS_PATH", default="docs", help='The path where the documents are stored (default: docs)')
    parser.add_argument('-f', metavar="F_VALUE", default=0.7, type=float, help='The value of the parameter F to calculate PageRank (default: 0.7)')

    args = parser.parse_args()

    print "Calculating PageRank:"

    pageRank = PageRank(args.f)

    pageRank.rank(args.docs)

if __name__ == '__main__':
    main()