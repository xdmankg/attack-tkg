"""Check corpus links, numerical identities, reported results and package hashes."""
import json
import numpy as np
import pandas as pd
from common import ROOT,csv,annual_inputs
import numerical_kernels as k
from check_table16 import compare as compare_table16
from update_checksums import check as check_integrity

def main():
    checks=[]
    def passed(name,detail):checks.append({'check':name,'status':'pass','detail':detail})
    docs=csv('data/canonical_documents.csv');raw=csv('data/source_manifest.csv');weights=csv('data/document_year_weights.csv');pairs=csv('data/document_techniques.csv')
    assert docs.canonical_document_id.is_unique and raw.raw_document_id.is_unique
    assert set(raw.canonical_document_id)<=set(docs.canonical_document_id)
    assert weights.canonical_document_id.nunique()==1474 and len(weights)==4060
    assert len(docs)==1856 and len(raw)==2192 and len(pairs)==5258
    assert weights.weight.gt(0).all() and weights.groupby('canonical_document_id').weight.sum().le(1+1e-12).all()
    passed('document links','1,856 canonical documents; 2,192 raw-to-canonical mappings; 1,474 core documents; 4,060 core document-years.')
    allm=pd.read_parquet(ROOT/'data/all_year_assignments.parquet')
    ref=allm[allm.window_label.astype(int).between(2002,2023)&(allm.primary_membership_mass>0)].copy()
    ref['year']=ref.window_label.astype(int)
    joint=weights.merge(ref[['canonical_document_id','year','primary_membership_mass']],on=['canonical_document_id','year'],validate='one_to_one')
    assert len(joint)==4060;np.testing.assert_allclose(joint.weight,joint.primary_membership_mass,rtol=0,atol=1e-15)
    passed('document-year weights','Values retain the frozen normalization; no reweighting after clipping to 2002-2023.')
    rank=csv('results/initial/figure_05/rich_document_ranking.csv');assert len(rank)==1474
    assert (rank.pair_potential==rank.n_techniques*(rank.n_techniques-1)//2).all()
    assert rank.pair_potential.sum()==66325 and (rank.pair_potential>0).sum()==588
    for values,expected in [(rank.pair_potential,[67.68,92.72,97.47]),(rank.loc[rank.pair_potential>0,'pair_potential'],[46.87,80.24,89.85])]:
        vals=np.sort(values.to_numpy())[::-1]
        for frac,e in zip([.01,.05,.1],expected):assert round(100*vals[:int(np.ceil(len(vals)*frac))].sum()/vals.sum(),2)==e
    passed('pair potential','Full ranks reproduce all six Table 14 percentages.')
    # Check all observed graph cells against the saved follow-up S0 arrays.
    mem,joined,index,matrix=annual_inputs()
    with np.load(ROOT/'results/followup/foundation/S0_FULL_replicate_0.npz',allow_pickle=False) as arr:
        for i,year in enumerate(range(2002,2024)):
            data=k.build_year(mem,joined,index,year);weighted,support=k.project(data['rows'],data['weights'],matrix)
            np.testing.assert_allclose(weighted/data['effective_mass'],arr['observed'][i],rtol=1e-12,atol=1e-14)
            np.testing.assert_array_equal(support,arr['supports'][i])
    passed('annual observed graphs','22 years × 28,195 relations reconstructed from public mappings and weights.')
    mc=csv('results/followup/mc/mc_model_comparison.csv');mc=mc[(mc.scope=='B0_REFERENCE')&(mc.density_multiplier==1)]
    desc=csv('results/followup/mc/mc_descriptor_raw.csv');sets={};counts={}
    for r in mc.itertuples():
        ic=np.array([r.R0_IC,r.R1_IC,r.R2_IC]);s={f'R{i}' for i in range(3) if ic[i]-min(ic)<=2+1e-12}
        assert '{'+','.join(sorted(s))+'}'==r.preferred_model_set;sets[r.scenario,r.level,r.replicate_id]=s
        part=desc[(desc.scenario==r.scenario)&(desc.level==r.level)&(desc.replicate_id==r.replicate_id)&(desc.scope=='B0_REFERENCE')].sort_values('transition_index')
        with np.load(ROOT/f'results/followup/foundation/{r.scenario}_replicate_{r.replicate_id}.npz',allow_pickle=False) as arr:
            residual=arr['residual_'+r.level]
            np.testing.assert_array_equal(residual,np.maximum(arr['observed']-arr['mu_'+r.level],0))
            computed=[k.descriptor(residual[i],residual[i+1],np.maximum(arr['supports'][i],arr['supports'][i+1])) for i in range(21)]
            np.testing.assert_allclose(pd.DataFrame(computed)[k.DESCRIPTORS],part[k.DESCRIPTORS],rtol=1e-10,atol=1e-12)
    levels=['L0_STAGE15_MATCHED','L1_EXTENDED','L2_HIGH'];overlap=[]
    for level in levels:overlap.append(sum(bool(sets['S0_FULL',level,r]&sets['S2_DROP_TOP5',level,r]) for r in range(5)))
    assert overlap==[0,0,5]
    assert sum(sets['S0_FULL',levels[0],r]=={'R1'} for r in range(5))==3
    assert sum(sets['S0_FULL',levels[0],r]=={'R2'} for r in range(5))==2
    passed('follow-up graphs and descriptors','45 B0 datasets; candidate sets recalculated from IC; overlap counts 0/5, 0/5, 5/5.')
    a=np.load(ROOT/'results/initial/figure_07/initial_bootstrap_replay.npz',allow_pickle=False);vals=a['delta_rss_star'];obs=float(a['observed'])
    assert len(vals)==10000 and int((vals>=obs).sum())==1398
    np.testing.assert_allclose(np.quantile(vals,.95,method='linear'),17.984492446201724,rtol=0,atol=1e-12)
    passed('initial wild bootstrap','10,000 saved replay statistics; raw plus-one p = 1399/10001.')
    for file,col,n in [('E02_T12_null.csv','T12_null',1),('E03_T12_null.csv','T12_null_E03',0)]:
        d=csv('results/initial/figure_08/'+file);assert len(d)==200 and (d[col]<=-1.8094631700427186).sum()==n
    passed('pseudo-temporal tests','Separate E02 and E03 arrays; lower-tail counts 1/200 and 0/200.')
    universe=csv('data/relation_universe.csv');assert len(universe)==28195 and universe.feature_index.tolist()==list(range(28195))
    passed('fixed relation universe','28,195 indexed undirected Technique pairs.')
    table_check, annual_check, table_summary = compare_table16()
    saved_check = pd.read_csv(ROOT/'results/paper_tables/table_16_numeric_check.csv',
                              dtype={'small_positive_values': str})
    saved_annual = csv('results/paper_tables/table_16_annual_check.csv')
    pd.testing.assert_frame_equal(table_check.fillna(''), saved_check.fillna(''), check_dtype=False,
                                  rtol=1e-14, atol=1e-30)
    pd.testing.assert_frame_equal(annual_check.reset_index(drop=True), saved_annual,
                                  check_dtype=False, rtol=1e-14, atol=1e-30)
    assert table_summary['strict_count_mismatches'] == 4
    passed('Table 16 reporting rule','All six counts match Positive Excess > 1e-12; 132 pair-year values checked. Four strict-zero counts differ; historical generator remains unlocated.')
    snapshots = csv('data/collection_snapshots.csv').set_index('collection')
    expected_urls = raw.source_dataset.map(snapshots.repository_url)
    assert expected_urls.notna().all() and expected_urls.equals(raw.collection_repository_url)
    assert raw.retrieval_url.eq('unavailable').all()
    assert snapshots.retrieval_date.eq('unavailable').all()
    passed('collection references','2,192 records link to two upstream collection URLs; historical retrieval metadata remains unavailable.')
    count=check_integrity()
    passed('file integrity',str(count)+' SHA-256 entries, complete file coverage and both provenance indexes matched.')
    out=ROOT/'reproduced';out.mkdir(exist_ok=True);(out/'verification.json').write_text(json.dumps(checks,indent=2)+'\n')
    print(json.dumps({'status':'pass','checks':len(checks)}))
if __name__=='__main__':main()
