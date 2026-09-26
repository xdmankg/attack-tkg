"""Replay one annual CP-null ensemble using the retained V07 seed and sampling rules."""
import argparse,json
import numpy as np
import numerical_kernels as k
from common import ROOT,annual_inputs

def main():
    p=argparse.ArgumentParser();p.add_argument('--year',type=int,default=2002,choices=range(2002,2024));p.add_argument('--scenario',choices=['S0_FULL','S1_DROP_TOP1','S2_DROP_TOP5'],default='S0_FULL');p.add_argument('--replicate',type=int,choices=range(5),default=0);p.add_argument('--level',choices=['L0_STAGE15_MATCHED','L1_EXTENDED','L2_HIGH'],default='L0_STAGE15_MATCHED');a=p.parse_args()
    conf=json.loads((ROOT/'configs/followup.json').read_text());level=conf['levels'][a.level]
    mem,joined,index,matrix=annual_inputs(a.scenario);data=k.build_year(mem,joined,index,a.year)
    eligible=[ids for ids in data['strata'].values() if len(ids)>=2 and len({tuple(sorted(data['rows'][i])) for i in ids})>1]
    entries=json.loads((ROOT/'configs/followup_seeds.json').read_text())['entries'];means=[];constraints=[]
    original_degrees=np.array([len(s) for s in data['rows']]);original_cols=np.zeros(len(matrix),int)
    for row in data['rows']:original_cols[list(row)]+=1
    for slot in level['seed_slots']:
        for chain in level['chains']:
            e=next(e for e in entries if e['scenario']==a.scenario and e['replicate_id']==a.replicate and e['year']==a.year and e['seed_slot']==slot and e['chain_id']==chain)
            rows=[set(s) for s in data['rows']];rng=np.random.default_rng(int(e['seed_uint64']));k.apply_trades(rows,eligible,rng,True);total=np.zeros(28195)
            for _ in range(level['draws_per_chain_for_mu']):
                k.apply_trades(rows,eligible,rng,False);w,_=k.project(rows,data['weights'],matrix);total+=w/data['effective_mass']
            means.append(total/level['draws_per_chain_for_mu'])
            np.testing.assert_array_equal([len(s) for s in rows],original_degrees)
            cols=np.zeros(len(matrix),int)
            for row in rows:cols[list(row)]+=1
            np.testing.assert_array_equal(cols,original_cols);constraints.append({'slot':slot,'chain':chain,'seed_uint64':e['seed_uint64'],'row_and_column_degrees':'pass'})
    mu=np.mean(means,axis=0);weighted,_=k.project(data['rows'],data['weights'],matrix);obs=weighted/data['effective_mass']
    with np.load(ROOT/f'results/followup/foundation/{a.scenario}_replicate_{a.replicate}.npz',allow_pickle=False) as f:ref=f['mu_'+a.level][a.year-2002]
    np.testing.assert_allclose(mu,ref,atol=1e-12,rtol=1e-10)
    out=ROOT/'reproduced'/'cp_null'/f'{a.scenario}_R{a.replicate}_{a.level}_{a.year}';out.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(out/'annual_replay.npz',observed=obs,mu=mu,positive_excess=np.maximum(obs-mu,0))
    report={'year':a.year,'scenario':a.scenario,'replicate':a.replicate,'level':a.level,'samples':level['N_mu'],'maximum_mu_difference':float(np.max(abs(mu-ref))),'constraints':constraints,'status':'pass'}
    (out/'verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':main()
