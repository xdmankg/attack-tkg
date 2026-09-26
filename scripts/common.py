from pathlib import Path
import numpy as np
import pandas as pd
from numerical_kernels import DESCRIPTORS
ROOT=Path(__file__).resolve().parents[1]

def csv(path,**kwargs):
    return pd.read_csv(ROOT/path,float_precision='round_trip',**kwargs)

def datasets():
    base=np.load(ROOT/'results/initial/baseline/baseline_datasets.npz',allow_pickle=False)
    yield 'BASELINE_STAGE15_S0',base['STAGE15_S0_raw'],base['STAGE15_S0_coverage']
    for scenario in ['S0_FULL','S1_DROP_TOP1','S2_DROP_TOP5']:
        yield f'BASELINE_V06_{scenario}',base[f'V06_{scenario}_B0_REFERENCE_100_raw'],base[f'V06_{scenario}_coverage']
    frame=csv('results/followup/mc/mc_descriptor_raw.csv')
    frame=frame[(frame.scope=='B0_REFERENCE')&(frame.density_multiplier==1)]
    for (scenario,replicate,level),part in frame.groupby(['scenario','replicate_id','level'],sort=True):
        with np.load(ROOT/f'results/followup/foundation/{scenario}_replicate_{replicate}.npz',allow_pickle=False) as a:
            coverage=np.minimum(a['analytical_coverage'][:-1],a['analytical_coverage'][1:])
        yield f'MC_{scenario}_R{replicate}_{level}',part.sort_values('transition_index')[DESCRIPTORS].to_numpy(),coverage

def annual_inputs(scenario='S0_FULL'):
    membership=csv('data/document_year_weights.csv').rename(columns={'weight':'primary_membership_mass'})
    if scenario!='S0_FULL':
        name='top1_excluded_documents.csv' if scenario=='S1_DROP_TOP1' else 'top5_excluded_documents.csv'
        excluded=set(csv('results/initial/v05/'+name).canonical_document_id)
        membership=membership[~membership.canonical_document_id.isin(excluded)]
    techniques=csv('data/document_techniques.csv')[['canonical_document_id','canonical_attack_id']].drop_duplicates()
    joined=membership.merge(techniques,on='canonical_document_id',how='left').dropna(subset=['canonical_attack_id'])
    # The historical index is defined from all S0 analytical mappings, also for exclusions.
    all_ids=csv('data/document_year_weights.csv').canonical_document_id.unique()
    names=sorted(techniques[techniques.canonical_document_id.isin(all_ids)].canonical_attack_id.unique())
    index={name:i for i,name in enumerate(names)};universe=csv('data/relation_universe.csv')
    matrix=np.full((len(names),len(names)),-1,np.int32)
    for row in universe.itertuples():
        a,b=index[row.technique_i_id],index[row.technique_j_id]
        matrix[a,b]=matrix[b,a]=row.feature_index
    return membership,joined,index,matrix
