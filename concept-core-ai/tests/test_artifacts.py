from pathlib import Path
import json
import numpy as np
import pytest
import torch
from exp001.artifacts import new_directory,write_json,read_json,save_npz,inventory,check_integrity
from exp001.config import seeds_for,NUMPY_VERSION,configuration
from exp001.aggregation import record_from_run,aggregate_paths
from exp001.runner import save_distance


def test_no_silent_overwrite_and_integrity(tmp_path):
    directory=new_directory(tmp_path/"run")
    with pytest.raises(FileExistsError): new_directory(directory)
    write_json(directory/"data.json",{"values":np.array([1,2])})
    with pytest.raises(FileExistsError): write_json(directory/"data.json",{})
    save_npz(directory/"data.npz",data=np.ones((2,3)))
    with pytest.raises(FileExistsError): save_npz(directory/"data.npz",data=np.zeros(1))
    write_json(directory/"integrity.json",inventory(directory))
    check_integrity(directory)
    write_json(directory/"data.json",{"changed":True},replace=True)
    with pytest.raises(ValueError,match="integrity"): check_integrity(directory)


def test_distance_artifacts_keep_arrays_and_order(tmp_path):
    from exp001.distance import GROUPS
    boot={"indices":np.tile(np.arange(900),(1000,1)),"means":np.ones((1000,8)),
          "group_order":list(GROUPS),"summaries":{k:{"CI":[1,1],"valid_iterations":1000} for k in GROUPS}}
    result={"scaler":{"mean":[0],"std":[1],"keep":[True]},"sample_ids":np.arange(900)+100,
            "pair_i":np.array([0]),"pair_j":np.array([1]),"category":np.array([0]),"flags":[],
            "metrics":{"standardized":{"distances":np.ones(1),"statistics":{},"contrast":{"color":0,"shape":0},"bootstrap":boot}}}
    assert save_distance(result,tmp_path,"initial")==[]
    saved=np.load(tmp_path/"bootstrap_initial_standardized.npz",allow_pickle=False)
    assert saved["indices"].shape==(1000,900) and saved["means"].shape==(1000,8)
    assert saved["sample_ids"][0]==100
    assert read_json(tmp_path/"distance_initial.json")["scaler"]["keep"]==[True]


def make_run(path,seed):
    path.mkdir()
    write_json(path/"configuration.json",{"master_seed":seed,"seeds":seeds_for(seed),"git_commit":"fixture",
        "numpy_version":NUMPY_VERSION,"formal":True,"run_id":path.name})
    write_json(path/"status.json",{"execution_status":"VALID","evaluation_flags":[],"complete":True})
    evaluation=path/"evaluation"; evaluation.mkdir()
    write_json(evaluation/"summary.json",{"pixel":{"fixture":{}}})
    for state,accuracy,contrast in (("initial",.6,1),("final",.7,2)):
        for attribute in ("color","shape"):
            write_json(evaluation/f"probe_{state}_{attribute}.json",{"test_accuracy":accuracy})
        write_json(evaluation/f"distance_{state}.json",{"metrics":{"standardized":{"statistics":{
            "same_color":{"mean_distance":1},"different_color":{"mean_distance":1+contrast},
            "same_shape":{"mean_distance":1},"different_shape":{"mean_distance":1+contrast}}}}})
    write_json(path/"integrity.json",inventory(path))
    return path


def test_aggregate_recomputes_from_artifacts_and_detects_damage(tmp_path):
    paths=[make_run(tmp_path/f"fixture-{seed}",seed) for seed in range(1001,1006)]
    result=aggregate_paths(paths,tmp_path/"aggregate-fixture")
    assert result["classification"]=="SUCCESS"
    manifest=read_json(tmp_path/"aggregate-fixture"/"baseline_manifest.json")
    assert manifest["numpy_version"]==NUMPY_VERSION and len(manifest["runs"])==5
    assert manifest["runs"][0]["seeds"]==seeds_for(1001)
    (paths[0]/"evaluation"/"probe_final_color.json").write_text('{}',encoding="utf-8")
    assert record_from_run(paths[0])["execution_status"]=="INVALID"
    assert aggregate_paths(paths,tmp_path/"damaged-fixture")["classification"]=="NOT_EVALUATED"


@pytest.mark.parametrize("error,expected",[(ValueError("technical fixture"),"INVALID"),(KeyboardInterrupt("interrupt fixture"),"INVALID")])
def test_runner_preserves_technical_failures(tmp_path,monkeypatch,error,expected):
    from exp001 import runner as r
    monkeypatch.setattr(r,"clean_commit",lambda root:"fixture")
    monkeypatch.setattr(r,"require_verification",lambda *a:{"fixture":True})
    def fail(*args): raise error
    monkeypatch.setattr(r,"generate_metadata",fail)
    output=tmp_path/"verification-only-no-training"
    with pytest.raises(type(error)):
        r.run_one(1001,output,tmp_path,"mock-verification")
    status=read_json(output/"status.json")
    assert status["execution_status"]==expected and not status["complete"]
    assert (output/"failure.json").exists()
    check_integrity(output)
    assert "classification" not in read_json(output/"report.json")


def test_runner_preserves_experimental_failure(tmp_path,monkeypatch):
    from exp001 import runner as r
    monkeypatch.setattr(r,"clean_commit",lambda root:"fixture")
    monkeypatch.setattr(r,"require_verification",lambda *a:{"fixture":True})
    def fail(*args): raise r.ExperimentalFailure("numerical fixture")
    monkeypatch.setattr(r,"generate_metadata",fail)
    output=tmp_path/"verification-only-failure"
    status=r.run_one(1002,output,tmp_path,"mock-verification")
    assert status["execution_status"]=="EXPERIMENTAL_FAILURE"
    check_integrity(output)


def test_formal_run_guards_before_creation(tmp_path,monkeypatch):
    from exp001 import runner as r
    with pytest.raises(ValueError,match="five"):
        r.run_one(33,tmp_path/"disallowed",tmp_path,"absent")
    monkeypatch.setattr(r,"NUMPY_VERSION","different")
    with pytest.raises(ValueError,match="NumPy"):
        r.run_one(1001,tmp_path/"disallowed",tmp_path,"absent")
    assert not (tmp_path/"disallowed").exists()


def test_pca_and_reconstruction_artifacts(tmp_path):
    from exp001.visualization import pca_artifacts,reconstruction_artifact
    from exp001.data import ImageDataset
    x=np.random.Generator(np.random.PCG64(10)).normal(size=(30,32))
    ids=np.arange(30)+50
    labels={"color":np.resize(["red","green","blue"],30),"shape":np.resize(["circle","triangle","square"],30)}
    pca_artifacts(x,ids,labels,tmp_path/"pca")
    for dim in (2,3):
        with np.load(tmp_path/"pca"/f"pca_{dim}d.npz") as artifact:
            np.testing.assert_allclose(artifact["coordinates"],(x-artifact["mean"])@artifact["components"].T,atol=1e-12)
            np.testing.assert_array_equal(artifact["sample_ids"],ids)
        for attr in labels: assert (tmp_path/"pca"/f"pca_{dim}d_{attr}.png").stat().st_size>1000
    images=np.zeros((10,64,64,3),np.float32)
    reconstruction_artifact(torch.nn.Identity(),ImageDataset(images,np.arange(10)),np.arange(10)+100,tmp_path)
    artifact=np.load(tmp_path/"reconstruction.npz")
    assert artifact["sample_ids"].tolist()==list(range(100,109))
    np.testing.assert_array_equal(artifact["inputs"],artifact["reconstructions"])
