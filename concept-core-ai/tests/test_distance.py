import itertools
import numpy as np
import pytest
from scipy.spatial.distance import pdist
from exp001.distance import (CATEGORIES,GROUPS,pair_layout,pair_statistics,bootstrap_indices,
                             instance_means,bootstrap,linear_quantile,confidence_interval,analyze_distance)
from exp001.data import split_indices


@pytest.fixture
def layout(metadata):
    rows=[metadata[i] for i in split_indices(metadata)["test"]]
    return pair_layout([r["color"] for r in rows],[r["shape"] for r in rows],[r["sample_id"] for r in rows])


def test_pair_counts_and_union_statistics(layout):
    i,j,category=layout
    assert len(i)==404550 and np.all(i<j)
    assert len(set(zip(i,j)))==404550
    assert np.bincount(category).tolist()==[44550,90000,90000,180000]
    values=np.arange(len(i),dtype=float)/100
    result=pair_statistics(values,category)
    for name,codes in GROUPS.items():
        selected=values[np.isin(category,codes)]
        assert result[name]["count"]==len(selected)
        assert result[name]["mean_distance"]==selected.mean()
        assert result[name]["median_distance"]==np.median(selected)
        assert result[name]["standard_deviation"]==selected.std(ddof=0)
    assert result["same_color"]["mean_distance"] != np.mean([result[CATEGORIES[0]]["mean_distance"],result[CATEGORIES[1]]["mean_distance"]])


def test_bootstrap_all_indices_reference():
    got=np.array(list(bootstrap_indices(123)))
    ref_rng=np.random.Generator(np.random.PCG64(123))
    reference=np.array([ref_rng.integers(low=0,high=900,size=900,endpoint=False,dtype=np.int64) for _ in range(1000)])
    assert got.shape==(1000,900) and got.dtype==np.int64
    np.testing.assert_array_equal(got,reference)
    assert got[0,:20].tolist()==[13,614,533,48,818,198,229,165,300,158,313,730,406,831,404,248,709,737,775,800]
    assert not np.array_equal(got[0],got[1])
    np.testing.assert_array_equal(got,np.array(list(bootstrap_indices(123))))


def test_instance_multiplicity_against_explicit_enumeration():
    colors=np.array([0,0,1,1]); shapes=np.array([0,1,0,1])
    i,j,category=pair_layout(colors,shapes,[10,11,12,13])
    distances=pdist(np.array([[0.],[2.],[5.],[9.]]))
    indices=np.array([0,0,0,1,1,2,3,3])
    got=instance_means(indices,i,j,category,distances,4)
    pairs=[]
    for left,right in itertools.combinations(range(len(indices)),2):
        a,b=indices[left],indices[right]
        if a==b: continue
        cat=2*int(colors[a]!=colors[b])+int(shapes[a]!=shapes[b])
        pairs.append((cat,abs([0,2,5,9][a]-[0,2,5,9][b])))
    expected=[np.mean([v for c,v in pairs if c in codes]) if any(c in codes for c,v in pairs) else np.nan for codes in GROUPS.values()]
    np.testing.assert_allclose(got,expected,equal_nan=True)
    assert sum(1 for c,v in pairs if c==1)==3*2+1*2
    assert np.isnan(instance_means(np.zeros(10,dtype=int),i,j,category,distances,4)).all()


@pytest.mark.parametrize("n,failed",[(949,True),(950,False),(1000,False)])
def test_quantile_and_valid_boundary(n,failed):
    means=np.r_[np.arange(n,dtype=float),np.full(1000-n,np.nan)]
    result=confidence_interval(means)
    assert result["valid_iterations"]==n
    assert (result.get("flag")=="BOOTSTRAP_CI_FAILED")==failed
    if not failed:
        np.testing.assert_allclose(result["CI"],[(n-1)*.025,(n-1)*.975])
    assert linear_quantile([0,10],.25)==2.5
    assert linear_quantile([7],.975)==7
    assert linear_quantile([0,10],1)==10


def test_full_bootstrap_means_and_ci_reproducible(layout):
    i,j,c=layout
    distances=pdist(np.column_stack((np.arange(900)%17,np.arange(900)/100)))
    a=bootstrap(distances,i,j,c,987)
    b=bootstrap(distances,i,j,c,987)
    np.testing.assert_array_equal(a["indices"],b["indices"])
    np.testing.assert_array_equal(a["means"],b["means"])
    assert a["summaries"]==b["summaries"]
    assert all(v["valid_iterations"]==1000 for v in a["summaries"].values())


def test_distance_scaler_and_raw_saved(metadata,monkeypatch):
    import exp001.distance as d
    # Full statistical bootstrap is tested above; isolate scaling here.
    def fake_boot(*args):
        return {"summaries":{name:{"CI":[0,1],"valid_iterations":1000} for name in GROUPS}}
    monkeypatch.setattr(d,"bootstrap",fake_boot)
    rows=[metadata[i] for i in split_indices(metadata)["test"]]
    train=np.array([[-1,0,2],[1,0,6]],float)
    test=np.column_stack((np.arange(900)/100,np.zeros(900),np.arange(900)/20))
    result=analyze_distance(train,test,[r["color"] for r in rows],[r["shape"] for r in rows],list(range(900)),4)
    np.testing.assert_array_equal(result["scaler"]["keep"],[True,False,True])
    np.testing.assert_allclose(result["metrics"]["raw"]["distances"],pdist(test))
    np.testing.assert_allclose(result["metrics"]["standardized"]["distances"],pdist((test[:,[0,2]]-[0,4])/[1,2]))
    with pytest.raises(ValueError):
        pair_layout([0,0],[0,1],[1,1])
