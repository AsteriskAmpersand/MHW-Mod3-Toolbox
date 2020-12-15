# -*- coding: utf-8 -*-
"""
Created on Thu Jun 18 07:42:32 2020

@author: AsteriskAmpersand
"""


class ClusterSet():
    def __init__(self):
        self.clusters = []
        self.internalIndexTable = {}
        self.internalReferenceTable = {}
    def new(self,index,location):
        self.clusters.append(Cluster(index,location))
    def reduce(self,tol):
        i = 0
        while i < len(self):
            c = self.clusters[i]
            j = i+1
            while j < len(self):
                c2 = self.clusters[j]
                if c.distance(c2) < tol:
                    c.mergeInto(c2)
                    self.clusters.pop(j)
                else:
                    j+=1
            i+=1
        #self.clean()
        self.buildReferences()
        
    def __clean__(self):
        i = 0
        while i<len(self):
            if len(self.clusters[i]) < 2:
                self.clusters.pop(i)
            else:
                i+=1

    def clean(self):
        self.__clean__()
        self.buildReferences()
                
    def buildReferences(self):
        refTable = {}
        indexTable = {}
        for ix, cluster in enumerate(self):
            for element in cluster.members:
                refTable[element] = cluster
                indexTable[element] = ix
        self.internalReferenceTable = refTable
        self.internalIndexTable = indexTable
            
    def intersect(self,clusterset):
        r = []
        for c in self:
            r.append(c.intersect(clusterset[c.id]))
        self.clusters = r
        self.buildReferences()
        return self
                
    def __contains__(self,key):
        return key in self.internalReferenceTable
    def __getitem__(self,key):
        return self.internalReferenceTable[key]
    def __iter__(self):
        return iter(self.clusters)
    def __len__(self):
        return len(self.clusters)
    def __repr__(self):
        result = "Cluster:\n"
        result+= "Internal Ref Table: %d Entries\n"%(len(self.internalReferenceTable))
        for c in self.clusters:
            result += "\t%d: "%(c.id)
            result += str(c)+"\n"
        return result
    
class Cluster():
    def __init__(self,ix,rootCo):
        self.id = ix
        self.root = rootCo
        self.members = set([ix])
    def mergeInto(self,cluster2):
        self.members = self.members.union(cluster2.members)
    def distance(self,cluster2):
        return (self.root - cluster2.root).length
    def intersect(self,cluster2):
        c = Cluster(self.id,self.root)
        c.members = self.members.intersection(cluster2.members)
        return c
    def __len__(self):
        return len(self.members)
    def __repr__(self):
        return "|"+','.join(map(str,self.members))+"|"