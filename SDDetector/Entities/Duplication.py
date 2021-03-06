#!/usr/bin/env python

import sys
import logging

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
        self.DuplicationType = self.setDuplicationType()


    def setDuplicationType(self):
        """set if duplication type: mirror, bridge, intra,inter """

        if (self.seq1, self.start1, self.end1) == (self.seq2, self.start2, self.end2):
            return 'mirror'
        if self.seq1 == self.seq2:
            if self.isOverlapping():
                return 'bridge'
            if not self.isOverlapping():
                return 'intra'
        if self.seq1 != self.seq2:
            return 'inter'
        else:
            logging.error('Could not detect duplication type for duplication: {}'.format(self.seq1,self.start1, self.end1, self.seq2, self.start2, self.end2))
            return None


    def isOverlapping(self):
        """test if seq1 overlaps seq2"""

        start = min(self.start1, self.start2)
        if start == self.start1:
            if self.end1 < self.start2:
                return False
            else:
                return True
        else:
            if self.end2 < self.start1:
                return False
            else:
                return True


    def getdSeqToSeq(self):
        """get dict with link seq to seq"""

        dSeqToSeq = {}
        dSeqToSeq[self.seq1] = {}
        dSeqToSeq[self.seq2] = {}

        for i,(reg1,reg2) in enumerate(self.lRegions):

            lreg1 = []
            lreg2 = []
            index2 = reg2.start-1
            nbIndel2 = 0
            for base in self.lSeqAlgmts[i][1]:
                if base != '-':
                    index2 +=1
                    lreg2.append(index2)
                else:
                    lreg2.append(None)
                    nbIndel2 +=1
            if index2 != reg2.end:
                logging.error('#1: problem with nb of base/algnmt')
                sys.exit(1)

            if reg1.strand == 1:
                index1 = reg1.start-1
                nbIndel1 = 0
                for base in self.lSeqAlgmts[i][0]:
                    if base != '-':
                        index1 +=1
                        lreg1.append(index1)
                    else:
                        lreg1.append(None)
                        nbIndel1 += 1
                if index1 != reg1.end:
                    logging.error('#2: problem with nb of base/algnmt')
                    sys.exit(1)
            elif reg1.strand == -1:
                index1 = reg1.end+1
                nbIndel1 = 0
                for base in self.lSeqAlgmts[i][0]:
                    if base != '-':
                        index1 -=1
                        lreg1.append(index1)
                    else:
                        lreg1.append(None)
                        nbIndel1 += 1
                if index1 != reg1.start:
                    logging.error('#3: problem with nb of base/algnmt')
                    sys.exit(1)
            if len(lreg1) != len(lreg2):
                logging.error('length algmt 1 not equals to length algmt 2')
                sys.exit(1)
            for i,pos in enumerate(lreg1):
                if pos != None:
                    dSeqToSeq[reg1.seq][pos] = (reg2.seq,lreg2[i])
            for i,pos in enumerate(lreg2):
                if pos != None:
                    dSeqToSeq[reg2.seq][pos] = (reg1.seq,lreg1[i])

        return dSeqToSeq

    def getSeqAlignmentWithIndels(self, seqid, start, end, deltaStart, deltaEnd):
        """get alignment with Indels managment"""

        seqIndex = None
        myRegionIndex = None
        myRegionStrand = None

        if self.seq1 != self.seq2:
            if seqid == self.seq1:
                seqIndex = 0
            elif seqid == self.seq2:
                seqIndex = 1
            else:
                logging.error("Error this sequence is not in this duplication")
                sys.exit(1)

            for i, reg in enumerate (self.lRegions):
                logging.debug('getSeqAlignment - request:{}-{}-{}, region:{}-{}'.format(seqid,start,end,reg[seqIndex].start,reg[seqIndex].end))
                if start >= reg[seqIndex].start and end <= reg[seqIndex].end:
                    myRegionIndex = i
                    myRegion = reg[seqIndex]
            if myRegionIndex == None and start > 0 and end > 0:
                logging.info("No region span these positions : {}-{}, possibly splitted regions".format(start,end))
                return (None,None)
        else:
            for index in range(0,2):
                for i, reg in enumerate(self.lRegions):
                    if start >= reg[index].start and end <= reg[index].end:
                        myRegionIndex = i
                        myRegion = reg[index]
                        seqIndex = index
            if myRegionIndex == None and start > 0 and end > 0:
                logging.info("No region span these positions : {}-{}, possibly splitted regions".format(start,end))
                return (None,None)

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

        return(algmt, myRegion.strand)

    def getSeqAlignment(self,seqid,start,end):
        """return the alignment"""

        seqIndex = None
        myRegionIndex = None
        myRegionStrand = None

        if self.seq1 != self.seq2:
            if seqid == self.seq1:
                seqIndex = 0
            elif seqid == self.seq2:
                seqIndex = 1
            else:
                loggin.error("Error this sequence is not in this duplication")
                sys.exit(1)

            for i, reg in enumerate (self.lRegions):
                logging.debug('getSeqAlignment - request:{}-{}-{}, region:{}-{}'.format(seqid,start,end,reg[seqIndex].start,reg[seqIndex].end))
                if start >= reg[seqIndex].start and end <= reg[seqIndex].end:
                    myRegionIndex = i
                    myRegion = reg[seqIndex]
            if myRegionIndex == None and start > 0 and end > 0:
                logging.info("No region span these positions : {}-{}, possibly splitted regions".format(start,end))
                return (None,None)
        else:
            for index in range(0,2):
                for i, reg in enumerate(self.lRegions):
                    if start >= reg[index].start and end <= reg[index].end:
                        myRegionIndex = i
                        myRegion = reg[index]
                        seqIndex = index
            if myRegionIndex == None and start > 0 and end > 0:
                logging.info("No region span these positions : {}-{}, possibly splitted regions".format(start,end))
                return (None,None)

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

        return(algmt, myRegion.strand)

    def getSeqAlignmentWithBothAlgmts(self,seqid,start,end):
        """return the alignment"""

        seqIndex = None
        seqIndex2 = None
        myRegionIndex = None
        myRegionStrand = None
        myRegion = None
        mySecondRegion = None

        if self.seq1 != self.seq2:
            if seqid == self.seq1:
                seqIndex = 0
                seqIndex2 = 1
            elif seqid == self.seq2:
                seqIndex = 1
                seqIndex2 = 0
            else:
                logging.error("Error this sequence is not in this duplication")
                sys.exit(1)

            for i, reg in enumerate (self.lRegions):
                logging.debug('getSeqAlignment - request:{}-{}-{}, region:{}-{}'.format(seqid,start,end,reg[seqIndex].start,reg[seqIndex].end))
                if start >= reg[seqIndex].start and end <= reg[seqIndex].end:
                    myRegionIndex = i
                    myRegion = reg[seqIndex]
                    mySecondRegion = reg[seqIndex2]
            if myRegionIndex == None and start > 0 and end > 0:
                logging.info("Error no region span these positions : {}-{}, possibly splitted regions".format(start,end))
                return (None,None,None,None)
        else:
            for index in range(0,2):
                otherIndex = 2
                if index == 0:
                    otherIndex = 1
                elif index == 1:
                    otherIndex = 1
                for i, reg in enumerate(self.lRegions):
                    if start >= reg[index].start and end <= reg[index].end:
                        myRegionIndex = i
                        myRegion = reg[index]
                        seqIndex = index
                        mySecondRegion = reg[otherIndex]
                        seqIndex2 = otherIndex
            if myRegionIndex == None and start > 0 and end > 0:
                return (None,None,None,None)

        algmt = ''
        algmt2 = ''
        if myRegion.strand == 1:
            loopEnd = myRegion.start
            i = 0
            while loopEnd != end+1:
                if loopEnd < start:
                    next
                else:
                    algmt += self.lSeqAlgmts[myRegionIndex][seqIndex][i]
                    algmt2 += self.lSeqAlgmts[myRegionIndex][seqIndex2][i]
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
                    algmt2 += self.lSeqAlgmts[myRegionIndex][seqIndex2][i]
                if self.lSeqAlgmts[myRegionIndex][seqIndex][i] != '-':
                    loopEnd -= 1
                i += 1
        else:
            sys.exit("missing strand")

        return(algmt, algmt2, myRegion.strand, mySecondRegion.strand)


    def __eq__(self, other):
        """Equality on all args"""

        if self.dSeqToSeq:
            return (self.seq1,self.start1,self.end1,self.seq2,self.start2,self.end2,self.lRegions,self.lSeqAlgmts,self.dSeqToSeq) == (other.seq1,other.start1,other.end1,other.seq2,other.start2,other.end2,other.lRegions,other.lSeqAlgmts,other.dSeqToSeq)
        else:
            return (self.seq1,self.start1,self.end1,self.seq2,self.start2,self.end2,self.lRegions,self.lSeqAlgmts) == (other.seq1,other.start1,other.end1,other.seq2,other.start2,other.end2,other.lRegions,other.lSeqAlgmts)


    def __repr__(self):
        """representation"""

        return('{}-{}-{}-{}-{}-{}-{}'.format(self.seq1,self.start1,self.end1,self.seq2,self.start2,self.end2,self.lRegions))
