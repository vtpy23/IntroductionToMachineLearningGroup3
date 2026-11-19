"""Statistical reporting must wait for three distinct seed results."""
import copy
import pytest
from scripts.core_multiseed_report import aggregate_rows, normalized_config

def test_three_distinct_seeds_and_sample_sd_required():
    rows=[{'method':'dsal-k5','seed':seed,'Abar':value,'AK':value-5}
          for seed,value in enumerate([60.,62.,64.])]
    assert aggregate_rows(rows[:2])==[]
    assert aggregate_rows([rows[0],rows[0],rows[1]])==[]
    result=aggregate_rows(rows)[0]
    assert result['Abar_mean']==62. and result['Abar_std_sample_ddof1']==2.
    assert result['AK_mean']==57. and result['AK_std_sample_ddof1']==2.

def test_protocol_comparison_allows_only_seed_paths_and_metadata():
    baseline={'seed':0,'class_order_seed':0,'training':{'checkpoint':'seed0.pt','epochs':160},
              'analytic':{'buffer_size':8192},'output':'seed0','tracking':{},'provenance':{}}
    other=copy.deepcopy(baseline)
    other.update(seed=1,class_order_seed=1,output='seed1')
    other['training']['checkpoint']='seed1.pt'
    assert normalized_config(other)==normalized_config(baseline)
    other['analytic']['buffer_size']=2048
    assert normalized_config(other)!=normalized_config(baseline)
