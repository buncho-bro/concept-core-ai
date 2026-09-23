import warnings
import numpy as np
import pytest
from sklearn.exceptions import ConvergenceWarning
from exp001 import evaluation as e
from exp001.config import C_GRID


def test_scaler_population_statistics_and_boundary():
    train = np.array([[-1,1,0,0], [1,1,2e-8,1e-8]],dtype=float)
    scaler = e.TrainScaler.fit(train)
    np.testing.assert_array_equal(scaler.keep,[True,False,True,False])
    np.testing.assert_allclose(scaler.mean,[0,1,1e-8,0.5e-8])
    np.testing.assert_allclose(scaler.std,[1,0,1e-8,0.5e-8])
    changed_test = np.full((3,4),10**8)
    before = scaler.mean.copy()
    scaler.transform(changed_test)
    np.testing.assert_array_equal(before,scaler.mean)
    np.testing.assert_allclose(scaler.transform(train),[[-1,-1],[1,1]])
    final_scaler = e.TrainScaler.fit(train*2)
    assert not np.array_equal(scaler.std,final_scaler.std)


def test_classifier_parameters():
    c = e.classifier(10,72)
    assert c.C == 10 and c.penalty == "l2" and c.solver == "lbfgs"
    assert c.max_iter == 1000 and c.tol == 1e-6
    assert c.fit_intercept and c.class_weight is None and c.random_state == 72
    assert C_GRID == (.01,.1,1.,10.,100.)


@pytest.mark.parametrize("failed", [(),(.01,),(.01,.1,1,10,100)])
def test_convergence_ties_and_no_test_selection(monkeypatch, failed):
    events = []
    class Fake:
        def __init__(self,C):
            self.C=C; self.coef_=np.zeros((3,1)); self.intercept_=np.zeros(3)
            self.n_iter_=np.array([1000 if C in failed else 3]); self.classes_=np.array(["red","green","blue"])
        def fit(self,x,y):
            events.append(("fit",self.C,len(x)))
            assert len(x)==6
            if self.C in failed:
                warnings.warn("fixture non-convergence",ConvergenceWarning)
            return self
        def predict(self,x):
            events.append(("predict",self.C,len(x)))
            return np.resize(self.classes_,len(x))
    monkeypatch.setattr(e,"classifier",lambda C,seed:Fake(C))
    features={"train":np.arange(6)[:,None],"validation":np.arange(3)[:,None],"test":np.arange(9)[:,None]}
    labels={s:np.resize(["red","green","blue"],len(x)) for s,x in features.items()}
    result=e.evaluate_classifier(features,labels,("red","green","blue"),12)
    assert len(result["candidates"])==5
    assert [r["converged"] for r in result["candidates"]] == [c not in failed for c in C_GRID]
    if len(failed)==5:
        assert result["flag"]=="PROBE_FAILED"
        assert not any(n==9 for _,_,n in events)
        pixel=e.evaluate_classifier(features,labels,("red","green","blue"),12,"PIXEL_BASELINE_FAILED")
        assert pixel["flag"]=="PIXEL_BASELINE_FAILED"
    else:
        assert result["selected_C"] == (.1 if failed else .01)
        assert [x for x in events if x[2]==9] == [("predict", result["selected_C"],9)]
        assert max(i for i,event in enumerate(events) if event[0]=="fit") < next(i for i,event in enumerate(events) if event[2]==9)
        assert result["test_confusion_matrix"].tolist()==[[3,0,0],[0,3,0],[0,0,3]]


def test_larger_validation_accuracy_beats_small_C(monkeypatch):
    class Fake:
        def __init__(self,C):
            self.C=C; self.coef_=np.ones((3,1)); self.intercept_=np.zeros(3); self.n_iter_=np.array([1])
        def fit(self,x,y): return self
        def predict(self,x): return np.array([0,1,2] if self.C>=1 else [0,0,0])
    monkeypatch.setattr(e,"classifier",lambda C,seed:Fake(C))
    selected,candidates=e.select_classifier(np.eye(3),np.arange(3),np.eye(3),np.arange(3),0)
    assert selected.C==1


def test_real_multinomial_metrics_and_test_isolation():
    classes=np.array(["red","green","blue"])
    train=np.tile(np.eye(3), (12,1))
    features={"train":train,"validation":np.eye(3),"test":np.eye(3)}
    labels={s:np.resize(classes,len(v)) for s,v in features.items()}
    first=e.evaluate_classifier(features,labels,classes,2)
    second=e.evaluate_classifier({**features,"test":np.full((3,3),500.)},labels,classes,2)
    for key in ("selected_C","train_accuracy","train_balanced_accuracy","validation_accuracy","validation_balanced_accuracy","test_accuracy","test_balanced_accuracy"):
        assert key in first
    assert first["test_accuracy"]==1
    assert first["selected_C"]==second["selected_C"]
    np.testing.assert_array_equal(first["coefficients"],second["coefficients"])
    np.testing.assert_array_equal(first["scaler"]["mean"],second["scaler"]["mean"])
    assert first["class_order"]==["red","green","blue"] and first["chance_level"]==1/3
    assert first["coefficients"].shape==(3,3)


def test_zero_features_failure():
    features={s:np.ones((3,2)) for s in ("train","validation","test")}
    labels={s:np.array(["red","green","blue"]) for s in features}
    assert e.evaluate_classifier(features,labels,labels["train"],1)["flag"]=="PROBE_FAILED"


def test_pixel_features():
    images=np.zeros((1,64,64,3),np.float32)
    images[0,0,0]=[16,32,48]
    images[0,0,1]=[.0625,0,0]
    simple=e.pixel_features(images,"simple_image_statistics")
    assert simple.shape==(1,7)
    np.testing.assert_allclose(simple[0,:3],images.astype(float).mean(axis=(1,2))[0])
    np.testing.assert_allclose(simple[0,3:6],images.astype(float).std(axis=(1,2),ddof=0)[0])
    assert simple[0,6]==2/4096
    raw=e.pixel_features(images,"raw_pixel_linear")
    assert raw.shape==(1,12288)
    assert raw[0,0]==16/255 and raw[0,4096]==32/255 and raw[0,8192]==48/255
