"""Recalculate model fits or bootstrap analyses from the retained numerical inputs."""
import argparse, hashlib, json
import numpy as np
import pandas as pd
import numerical_kernels as k
from initial_bootstrap_reference import generic_wild_bootstrap
from common import ROOT,csv,datasets

def models(out):
    rows=[]
    for name,raw,coverage in datasets():
        med,scale,_=k.robust_params(raw);fits,_=k.all_models((raw-med)/scale)
        for f in fits:rows.append({'dataset_id':name,'model':f['method_id'],'rss':f['rss'],'ic':f['ic'],'candidate_set':k.preferred_set(fits)})
    pd.DataFrame(rows).to_csv(out/'model_fits.csv',index=False)
    source=csv('results/followup/mc/mc_model_comparison.csv')
    for r in source[(source.scope=='B0_REFERENCE')&(source.density_multiplier==1)].itertuples():
        key=f'MC_{r.scenario}_R{r.replicate_id}_{r.level}'
        for row in rows:
            if row['dataset_id']==key:
                np.testing.assert_allclose(row['ic'],getattr(r,row['model']+'_IC'),rtol=1e-8,atol=1e-8)
                assert row['candidate_set']==r.preferred_model_set
    return {'datasets':49,'followup_IC_comparisons':135,'status':'pass'}

def initial(out):
    a=np.load(ROOT/'results/initial/figure_07/stage15_inputs.npz',allow_pickle=False)
    raw,cov=a['raw'],a['coverage'];med,scale,_=k.robust_params(raw);y=(raw-med)/scale
    xr=np.column_stack([np.ones(21),cov]);xf=np.column_stack([np.ones(21),np.linspace(-1,1,21),cov])
    r=generic_wild_bootstrap(y,xr,xf,2026081505,10000)
    saved=np.load(ROOT/'results/initial/figure_07/initial_bootstrap_replay.npz',allow_pickle=False)['delta_rss_star']
    np.testing.assert_allclose(r['statistics'],saved,rtol=1e-12,atol=1e-12)
    assert r['exceedance_count']==1398
    np.savez_compressed(out/'initial_bootstrap.npz',delta_rss_star=r['statistics'])
    return {'B':10000,'seed':2026081505,'array_equal_in_this_environment':bool(np.array_equal(r['statistics'],saved)),'max_absolute_difference':float(np.max(abs(r['statistics']-saved))),'observed':r['observed'],'upper_tail_count':1398,'plus_one_p':r['p'],'q95_linear':float(np.quantile(r['statistics'],.95,method='linear')),'status':'pass'}

def followup(out,dataset):
    name,raw,cov=next(x for x in datasets() if x[0]==dataset)
    med,scale,_=k.robust_params(raw);values=(raw-med)/scale
    table=csv('results/followup/bootstrap/conditional_delta_rss_bootstrap.csv');table=table[table.dataset_id==dataset]
    rows=[];saved=np.load(ROOT/'results/followup/bootstrap/conditional_delta_rss_null_arrays.npz',allow_pickle=False)
    for r in table.itertuples():
        result=k.conditional_bootstrap(values,cov,r.direction,r.scheme,int(r.seed_uint64),int(r.B))
        obs,_,stats,count,p,*_=result
        np.testing.assert_allclose(obs,r.delta_RSS_observed,atol=1e-8,rtol=1e-8);assert count==r.extreme_count_upper
        np.testing.assert_allclose(stats.astype(np.float32),saved[r.null_array_key],rtol=1e-6,atol=1e-5)
        rows.append({'dataset_id':name,'direction':r.direction,'scheme':r.scheme,'seed_uint64':str(r.seed_uint64),'upper_tail_count':count,'p':p})
    pd.DataFrame(rows).to_csv(out/'followup_bootstrap.csv',index=False)
    return {'dataset':name,'comparisons':len(rows),'status':'pass'}

def loto(out,dataset):
    name,raw,cov=next(x for x in datasets() if x[0]==dataset)
    saved=csv('results/followup/loto/loto_loss_by_transition.csv');saved=saved[saved.dataset_id==name]
    med,scale,_=k.robust_params(raw);values=(raw-med)/scale;rows=[]
    for h in range(21):
        p0,h0,_,_=k.fit_fold_prediction(k,raw,h,0);p1,h1,_,_=k.fit_fold_prediction(k,raw,h,1)
        mask=np.ones(21,bool);mask[h]=False
        legacy={f['method_id']:f['trajectory'][h]*scale+med for f in [k.fit_r0_exact(values,mask),k.fit_r1_exact(values,mask),k.fit_r2_exact(values,mask)]}
        for cond,pred in [('LEGACY_GLOBAL_LOTO',legacy),('FOLD_LOCAL_LOTO',p0),('FOLD_LOCAL_GAP1',p1)]:
            for score,s in [('H0_COMMON',h0['scale']),('GAP1_COMMON',h1['scale']),('LEGACY_GLOBAL_SCALE',scale)]:
                for model in k.MODELS:
                    mse=float(np.mean(((raw[h]-pred[model])/s)**2))
                    ref=saved[(saved.holdout==h)&(saved.condition==cond)&(saved.score_scale_id==score)&(saved.model==model)].iloc[0]
                    np.testing.assert_allclose(mse,ref.mean_squared_loss,rtol=1e-8,atol=1e-8)
                    rows.append({'dataset_id':name,'holdout':h,'condition':cond,'score_scale_id':score,'model':model,'mean_squared_loss':mse})
    pd.DataFrame(rows).to_csv(out/'loto_losses.csv',index=False)
    # Stored CI summaries were computed in float64; the large float32 arrays are not needed here.
    boot=csv('results/followup/bootstrap/loto_dependence_bootstrap.csv');boot=boot[boot.dataset_id==name];checks=[]
    for r in boot.itertuples():
        part=saved[(saved.condition==r.loto_condition)&(saved.score_scale_id==r.scoring_scale_id)]
        models=r.model_comparison.split('_MINUS_');left=part[part.model==models[0]].sort_values('holdout').mean_squared_loss.to_numpy();right=part[part.model==models[1]].sort_values('holdout').mean_squared_loss.to_numpy()
        diff=left-right;rng=np.random.default_rng(int(r.seed_uint64));idx=rng.integers(0,21,size=(int(r.B),21)) if r.block_length==1 else k.moving_block_indices(rng,int(r.B),21,int(r.block_length))
        stats=diff[idx].mean(axis=1);lo,hi=np.quantile(stats,[.025,.975],method='linear')
        np.testing.assert_allclose([lo,hi],[r.ci95_low,r.ci95_high],atol=1e-9,rtol=1e-9)
        checks.append({'role':r.analysis_role,'comparison':r.model_comparison,'scheme':r.scheme,'ci95_low':lo,'ci95_high':hi})
    pd.DataFrame(checks).to_csv(out/'loto_bootstrap.csv',index=False)
    return {'dataset':name,'loss_comparisons':len(rows),'bootstrap_intervals':len(checks),'status':'pass'}

def main():
    p=argparse.ArgumentParser();p.add_argument('analysis',choices=['models','initial-bootstrap','followup-bootstrap','loto']);p.add_argument('--dataset',default='BASELINE_STAGE15_S0');a=p.parse_args()
    out=ROOT/'reproduced'/a.analysis/a.dataset;out.mkdir(parents=True,exist_ok=True)
    result=models(out) if a.analysis=='models' else initial(out) if a.analysis=='initial-bootstrap' else followup(out,a.dataset) if a.analysis=='followup-bootstrap' else loto(out,a.dataset)
    (out/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
