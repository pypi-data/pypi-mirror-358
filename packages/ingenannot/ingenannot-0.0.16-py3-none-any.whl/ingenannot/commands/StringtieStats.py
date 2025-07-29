#/usr/bin/env python3

import logging
import re
import numpy as np
import seaborn as sns
import matplotlib
import pandas as pd

matplotlib.use('Agg')
import matplotlib.pyplot as plt

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib import gridspec



from  Ingenannot.Utils import Utils


class StringtieStats(object):

    def __init__(self, args):

        self.gff_transcripts = args.Gff_transcripts
        self.source = args.source
        self.gff_supp = args.addgff
        self.source_supp = args.addsource

    def stats(self, genes, source):

        l = []
        cov = []
        tpm = []
        lmax = 0
        trmax = None
        nb_tr = 0
        for g in genes:
            for tr in g.lTranscripts:
                nb_tr += 1
                l.append(tr.getExonTotalLength())
                cov.append(float(tr.dAttributes['cov'][0]))
                tpm.append(float(tr.dAttributes['TPM'][0]))
                if tr.getExonTotalLength() > lmax:
                    lmax = tr.getExonTotalLength()
                    trmax = tr
        nb_genes = len(genes)
        print("Source\t#Transcripts\t#Genes\tMeanLength\tStdv\tMedian\tMin\tMax\tMeanCov\tStdv\tMedian\tMin\tMax\tMeanTPM\tStdv\tMedian\tMin\tMax")
        print("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}".format(source,nb_tr, nb_genes,np.mean(l),np.std(l),np.median(l),min(l),max(l),np.mean(cov),np.std(cov),np.median(cov),min(cov),max(cov),np.mean(tpm),np.std(tpm),np.median(tpm),min(tpm),max(tpm)))
        return l,cov,tpm


    def boxplot(self,lXs, lYs, out="", title="", xax="", yax="", color=['blue','green'],legend="", grid=[]):
            """Draw box plots"""
    
            fig = plt.Figure(figsize=(20,20))
            fig.suptitle(title, fontsize=32)
            ax = fig.add_subplot(111)
    #        for i,val in enumerate(llYs):
            ax.boxplot(lXs, labels=lYs, showfliers=False)
            axis_font = {'size':'28'}
            ax.set_xlabel(xax, **axis_font)
            ax.set_ylabel(yax, **axis_font)
            ax.tick_params(labelsize=20)
            ax.xaxis.set_tick_params(rotation=45)
            if legend:
                ax.legend(legend, fontsize=22)
            for line in grid:
                ax.axvline(x=line, linestyle='dashed', linewidth=1, color='black')
            canvas = FigureCanvasAgg(fig)
            canvas.print_figure(out, dpi=80)


    def plotDensity(self, ltpm, out="", legend="", title="", xax="", yax="",hist=False):

        fig = plt.Figure(figsize=(20,20))
        ax = fig.add_subplot(111)
        axis_font = {'size':'28'}
        fig.suptitle(title, fontsize=32)
        for i,l in enumerate(ltpm):
            sn = sns.distplot(l, hist=hist, kde=True,
               #      bins=int(180/5), color = 'darkblue',
                   #  hist_kws={'edgecolor':'black'},
                     kde_kws={'linewidth': 2},
                     label=legend[i], ax=ax)
            data_x, data_y = sn.lines[0].get_data()
            maxy = 0
            maxx = 0
            for j,h in enumerate(data_y):
                if h > maxy and j < len(data_y)-25: #bidouille for 2 small runs
                    maxy = h
                    maxx = data_x[j]
            if len(ltpm) == 1:
                print("limit maxx {}: {}".format(legend[i], maxx))
        ax.set_xlabel(xax, **axis_font)
        ax.set_ylabel(yax, **axis_font)
        ax.tick_params(axis='x', labelsize=26)
        ax.tick_params(axis='y', labelsize=26)
        ax.legend(fontsize=32) 
        canvas = FigureCanvasAgg(fig)
        canvas.print_figure(out, dpi=80)

    def plotHist(self, llYs, nb_bins, out="",legend="", title="", xax="", yax=""):
            fig = plt.Figure(figsize=(20,20))
            fig.suptitle(title, fontsize=32)
            ax = fig.add_subplot(111)
            axis_font = {'size':'28'}
            #ax.hist(llYs, nb_bins, histtype='bar')
            ax.hist(llYs, [0,1,2,3,4,5,6,7,8,9,10,15,20,40,100000], histtype='bar')
    #        for i,val in enumerate(llYs):
    #            ax.plot(lXs,val,color=color[i])
            axis_font = {'size':'28'}
            ax.set_xlabel(xax, **axis_font)
            ax.set_ylabel(yax, **axis_font)
            ax.set_xlim((0,nb_bins))
            ax.tick_params(labelsize=20)
            if legend:
                ax.legend(legend, fontsize=22)
    #        for line in grid:
    #            ax.axvline(x=line, linestyle='dashed', linewidth=1, color='black')
            canvas = FigureCanvasAgg(fig)
            canvas.print_figure(out, dpi=80)
    
    


    def run(self):
        """"launch command"""


        gffs = [self.gff_transcripts]
        sources = [self.source]
        if self.gff_supp:
            gffs.extend(self.gff_supp)
            sources.extend(self.source_supp)


        lbxplot = []
        covbxplot = []
        tpmbxplot = []
        nb_bins = 50
        lfiles = []
        ltpm = []
        labels = []

        for i,g in enumerate(gffs):
            genes = Utils.extract_genes(g)
            l, cov, tpm = self.stats(genes,sources[i])
            lbxplot.append(l)
            covbxplot.append(cov)
            tpmbxplot.append(tpm)
            dtpm = {}
            dtpm[nb_bins-1] = 0
            for val in tpm:
                if val < nb_bins:
                    if val in dtpm:
                        dtpm[val] += 1
                    else:
                        dtpm[val] = 1
                else:
                    dtpm[nb_bins-1] += 1
            l = []
            for key in dtpm:
                l.extend([key]*dtpm[key])
            ltpm.append(l)
            labels.append(sources[i])

        self.boxplot(lbxplot, labels, "box_length.png", "boxplot of transcript length", "runs","length in bp")
        self.boxplot(covbxplot, labels, "box_cov.png", "boxplot of transcript coverage", "runs", "coverage, nb reads")
        self.boxplot(tpmbxplot, labels, "box_tpm.png", "boxplot of TPM", "runs", "TPM")

        self.plotHist(ltpm, nb_bins, "hist-tpm.png",legend=labels, title="histogram of TPM", xax="runs", yax="TPM")
        self.plotDensity(ltpm, "density.png",legend=labels, title="Distribution of TPM", xax="TPM (bins, last bin = cumulative values of higher TPM)")
        for i,lab in enumerate(labels):
            self.plotDensity([ltpm[i]], "{}.density.png".format(lab),legend=[lab], title="{} - Distribution of TPM".format(lab), xax="TPM (bins, last bin = cumulative values of higher TPM)",hist=True)
#

        return 0
