#!/usr/bin/env python

import sys

class Duplication(object):

    def __init__(self, seq1, start1, end1, seq2, start2, end2,lRegions=[],lSeqAlgmts=[]):
        """Constructor"""

        self.seq1 = seq1
        self.start1 = start1
        self.end1 = end1
        self.seq2 = seq2
        self.start2 = start2
        self.end2 = end2
        self.lRegions =  lRegions # list of tulpe of 2 Region objects
        self.lSeqAlgmts = lSeqAlgmts # list of tuple of 2 strings  = aligned sequence
        self.dSeqToSeq = {} 
        if self.lRegions and self.lSeqAlgmts:
            self.dSeqToSeq = self.getdSeqToSeq()


    def getdSeqToSeq(self):
        """get """

        dSeqToSeq = {}
        dSeqToSeq[self.seq1] = {}
        dSeqToSeq[self.seq2] = {}

        for i,(reg1,reg2) in enumerate(self.lRegions):
           
            lreg1 = []
            lreg2 = []
            # reg2 = query in +1 strand
            index2 = reg2.start-1
            nbIndel2 = 0
            for base in self.lSeqAlgmts[i][1]:
                #print base
                index2 +=1
                if base != '-':
                    lreg2.append(index2)
                else:
                    lreg2.append(None)
                    nbIndel2 +=1
                #print index2
            if index2 != (reg2.end + nbIndel2):
                # todo log
                sys.exit('exit problem with nb of base/algnmt')

            if reg1.strand == 1:
                index1 = reg1.start-1
                nbIndel1 = 0
                for base in self.lSeqAlgmts[i][0]:
                    index1 +=1
                    if base != '-':
                        lreg1.append(index1)
                    else:
                        lreg1.append(None)
                        nbIndel1 += 1
                if index1 != (reg1.end + nbIndel1):
                    # todo log
                    #print index1
                    #print reg1.end
                    #print reg1.seq
                    sys.exit('exit 2 problem with nb of base/algnmt')
            
            elif reg1.strand == -1:
                index1 = reg1.end+1
                nbIndel1 = 0
                for base in self.lSeqAlgmts[i][0]:
                    index1 -=1
                    if base != '-':
                        lreg1.append(index1)
                    else:
                        lreg1.append(None)
                        nbIndel1 += 1
                if index1 != (reg1.start - nbIndel1):
                    # todo log
                    sys.exit('exit 3 problem with nb of base/algnmt')
 
            if len(lreg1) != len(lreg2):
                sys.exit('error algmt list')

            for i,pos in enumerate(lreg1):
                dSeqToSeq[reg1.seq][pos] = (reg2.seq,lreg2[i])
            for i,pos in enumerate(lreg2):
                dSeqToSeq[reg2.seq][pos] = (reg1.seq,lreg1[i])
         
        return dSeqToSeq


    def getSeqAlignment(self,seqid,start,end):
        """return the alignment"""

        seqIndex = None
        if seqid == self.seq1:
            seqIndex = 0
        elif seqid == self.seq2:
            seqIndex = 1
        else:
            #TODO: log
            sys.exit("Error this sequence is not in this duplication")

        myRegionIndex = None
        myRegionStrand = None
        for i, reg in enumerate (self.lRegions):
            if start >= reg[seqIndex].start and end <= reg[seqIndex].end:
                myRegionIndex = i
                myRegion = reg[seqIndex]
        if myRegionIndex == None:
            sys.exit("Error region of this sequence not in this duplication")

        algmt = ''
        if myRegion.strand == 1:
            loopEnd = myRegion.start
            i = 0
            while loopEnd != end+1:
                if loopEnd < start:
                    next
                else:
                    algmt += self.lSeqAlgmts[myRegionIndex][seqIndex][i]
                     
                if self.lSeqAlgmts[myRegionIndex][seqIndex][i] != '-':
                    loopEnd += 1
                i += 1

        elif myRegion.strand == -1:
            loopEnd = myRegion.end
            i = 0
            while loopEnd != start-1:
                if loopEnd > end:
                    next
                else:
                    algmt += self.lSeqAlgmts[myRegionIndex][seqIndex][i]

                if self.lSeqAlgmts[myRegionIndex][seqIndex][i] != '-':
                    loopEnd -= 1
                i += 1

        else:
            sys.exit("missing strand")

        return(algmt) 


    def __eq__(self, other):
        """Equality on all args"""
        
        if self.dSeqToSeq: 
            return (self.seq1,self.start1,self.end1,self.seq2,self.start2,self.end2,self.lRegions,self.lSeqAlgmts,self.dSeqToSeq) == (other.seq1,other.start1,other.end1,other.seq2,other.start2,other.end2,other.lRegions,other.lSeqAlgmts,other.dSeqToSeq)
        else:
            return (self.seq1,self.start1,self.end1,self.seq2,self.start2,self.end2,self.lRegions,self.lSeqAlgmts) == (other.seq1,other.start1,other.end1,other.seq2,other.start2,other.end2,other.lRegions,other.lSeqAlgmts)

    def __repr__(self):
        """representation"""
         
        return('{}-{}-{}-{}-{}-{}-{}-{}'.format(self.seq1,self.start1,self.end1,self.seq2,self.start2,self.end2,self.lRegions,self.lSeqAlgmts))
