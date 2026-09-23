"""Integration with synthetic evaluation fixtures, never formal baseline results."""
import numpy as np
import pytest
from exp001.artifacts import write_json,read_json,save_npz,inventory,check_integrity
from exp001.config import COLORS,SHAPES,SPLITS,configuration,seeds_for,NUMPY_VERSION
from exp001.data import split_indices
from exp001.runner import evaluate_saved,write_metadata,reanalyze,require_verification


def test_saved_evaluation_pipeline(metadata,tmp_path):
    run=tmp_path/"synthetic-verification-input"; run.mkdir()
    config={**configuration(),"formal":False,"seeds":seeds_for(77),"numpy_version":NUMPY_VERSION}
    write_json(run/"configuration.json",config)
    write_metadata(run/"metadata.csv",metadata)
    indices=split_indices(metadata)
    ids=np.array([r["sample_id"] for r in metadata])
    colors=np.array([COLORS.index(r["color"]) for r in metadata])
    shapes=np.array([SHAPES.index(r["shape"]) for r in metadata])
    # Synthetic saved latent, explicitly not extracted from a formally trained encoder.
    rng=np.random.Generator(np.random.PCG64(78))
    x=rng.normal(size=(9000,32)).astype(np.float32)
    x[:,:3]+=np.eye(3)[colors]*3
    x[:,3:6]+=np.eye(3)[shapes]*3
    (run/"latent").mkdir()
    for state in ("initial","final"):
        for split in SPLITS:
            save_npz(run/"latent"/f"{state}_{split}.npz",latent=x[indices[split]],sample_ids=ids[indices[split]])
    images=np.lib.format.open_memmap(run/"images.npy",mode="w+",dtype=np.float32,shape=(9000,64,64,3))
    images[:]=0
    for index in range(9000):
        images[index,0,:1+shapes[index],colors[index]]=230
    images.flush(); del images
    summary=evaluate_saved(run,run/"evaluation")
    assert summary["evaluation_flags"]==[]
    assert "classification" not in summary
    for state in ("initial","final"):
        for attribute in ("color","shape"):
            probe=read_json(run/"evaluation"/f"probe_{state}_{attribute}.json")
            assert len(probe["test_predictions"])==900
            assert len(probe["candidates"])==5
        for kind in ("standardized","raw"):
            with np.load(run/"evaluation"/f"bootstrap_{state}_{kind}.npz") as boot:
                assert boot["indices"].shape==(1000,900) and boot["means"].shape==(1000,8)
                np.testing.assert_array_equal(boot["sample_ids"],ids[indices["test"]])
        pairs=np.load(run/"evaluation"/f"pairs_{state}.npz")
        assert len(pairs["pair_i"])==404550
        distance=read_json(run/"evaluation"/f"distance_{state}.json")
        assert distance["metrics"]["standardized"]["statistics"]["same_color_same_shape"]["count"]==44550
    for kind in ("simple_image_statistics","raw_pixel_linear"):
        assert set(summary["pixel"][kind])=={"color","shape"}
        for attribute in ("color","shape"):
            pixel=read_json(run/"evaluation"/f"pixel_{kind}_{attribute}.json")
            assert pixel["scaler"]["fit_split"]=="train"
            assert len(pixel["scaler"]["mean"])==(7 if kind=="simple_image_statistics" else 12288)
    # Both states have identical saved input; this also tests complete distance/CI reproducibility.
    assert read_json(run/"evaluation"/"distance_initial.json")==read_json(run/"evaluation"/"distance_final.json")
    write_json(run/"integrity.json",inventory(run)); check_integrity(run)
    with pytest.raises(FileExistsError): evaluate_saved(run,run/"evaluation")


def test_verification_receipt_and_reanalysis_guards(tmp_path,monkeypatch):
    import exp001.runner as r
    monkeypatch.setattr(r,"environment",lambda:{"fixture":1})
    monkeypatch.setattr(r,"implementation_fingerprint",lambda root:{"a":"hash"})
    path=tmp_path/"receipt.json"
    write_json(path,{"exit_code":1,"implementation":{"a":"hash"},"environment":{"fixture":1}})
    with pytest.raises(ValueError,match="verification"): require_verification(tmp_path,path)
    write_json(path,{"exit_code":0,"implementation":{"a":"changed"},"environment":{"fixture":1}},replace=True)
    with pytest.raises(ValueError,match="verification"): require_verification(tmp_path,path)
    write_json(path,{"exit_code":0,"implementation":{"a":"hash"},"environment":{"fixture":2}},replace=True)
    with pytest.raises(ValueError,match="environment"): require_verification(tmp_path,path)
    write_json(path,{"exit_code":0,"implementation":{"a":"hash"},"environment":{"fixture":1}},replace=True)
    assert require_verification(tmp_path,path)["exit_code"]==0
    run=tmp_path/"wrong-version"; run.mkdir()
    write_json(run/"configuration.json",{"numpy_version":"different"})
    write_json(run/"integrity.json",inventory(run))
    with pytest.raises(ValueError,match="NumPy"): reanalyze(run,tmp_path/"reanalysis")


def test_verify_cli_never_dispatches_run(tmp_path,monkeypatch):
    import exp001.cli as cli
    import exp001.runner as runner
    calls=[]
    monkeypatch.setattr(cli,"verify",lambda output,root:calls.append(output) or 0)
    def forbidden(*args,**kw): raise AssertionError("Formal execution during verify")
    monkeypatch.setattr(runner,"run_one",forbidden)
    assert cli.main(["verify","--output",str(tmp_path/"verification")])==0
    assert len(calls)==1


def test_verify_cli_utf8_log_in_japanese_path(tmp_path,monkeypatch):
    import sys
    import exp001.cli as cli
    original_run=cli.subprocess.run
    monkeypatch.setattr(cli,"environment",lambda:{"fixture":"encoding-only"})
    def short_child(command,**kwargs):
        assert kwargs["env"]["PYTHONIOENCODING"]=="utf-8"
        assert kwargs["env"]["PYTHONUTF8"]=="1"
        return original_run([sys.executable,"-c","print('日本語パスの検証')"],**kwargs)
    monkeypatch.setattr(cli.subprocess,"run",short_child)
    output=tmp_path/"日本語の検証"
    assert cli.verify(output,tmp_path)==0
    assert (output/"pytest.txt").read_text(encoding="utf-8").strip()=="日本語パスの検証"
    assert read_json(output/"verification.json")["exit_code"]==0
