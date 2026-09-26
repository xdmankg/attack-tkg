"""Redraw numerical figures from archived files, preserving publication artwork."""
import argparse,shutil,subprocess,sys,json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from common import ROOT,csv

def figure6(work):
    frame=csv('results/initial/stage15/final_original_vs_adjusted_descriptor_comparison.csv')
    labels=['New-relation rate','Disappearance rate','Increase rate','Low-support relation share','Medium-support relation share','RMS low','RMS medium','RMS high','Persistent-relation RMS']
    fig,ax=plt.subplots(figsize=(7.6,3.5),layout='constrained');y=np.arange(9)
    ax.hlines(y,frame.original_slope,frame.adjusted_slope,color='#BDC8CD',lw=2)
    ax.scatter(frame.original_slope,y,c='#153F68',s=22,label='Observed',zorder=3)
    ax.scatter(frame.adjusted_slope,y,c='#D87916',marker='D',s=20,label='Positive Excess',zorder=3)
    ax.axvline(0,color='#777777',lw=.7,ls='--');ax.set_yticks(y,labels,fontsize=8);ax.invert_yaxis()
    ax.set_xlabel('Linear slope against normalized time τ ∈ [−1, 1]\nRobust-scaled descriptors; 21 transitions',fontsize=8)
    ax.spines[['top','right']].set_visible(False);ax.legend(frameon=False,fontsize=8);ax.tick_params(labelsize=8)
    ax.annotate('sign reversed',(-.38,8),xytext=(-1.15,7.5),fontsize=7,arrowprops={'arrowstyle':'-','lw':.6})
    for ext in ['png','svg','pdf']:fig.savefig(work/f'figure_06.{ext}',dpi=400)
    plt.close(fig)

def main():
    p=argparse.ArgumentParser();p.add_argument('--figures',nargs='+',type=int,default=[3,5,6,7,8,9,10],choices=[3,5,6,7,8,9,10]);a=p.parse_args()
    for i in a.figures:
        out=ROOT/'reproduced'/f'figure_{i:02d}';out.mkdir(parents=True,exist_ok=True)
        if i==6:figure6(out);continue
        src=ROOT/(f'data/examples/figure_{i:02d}' if i==3 else f'results/followup/figure_{i:02d}' if i==10 else f'results/initial/figure_{i:02d}')
        shutil.copytree(src,out/'source',dirs_exist_ok=True)
        subprocess.run([sys.executable,str(ROOT/f'scripts/plots/figure_{i:02d}.py'),str(out)],check=True)
        print(f'Figure {i}: {out.relative_to(ROOT)}')
if __name__=='__main__':main()
