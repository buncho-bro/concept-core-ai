from copy import deepcopy
import numpy as np
import pytest
from exp001.config import FORMAL_SEEDS,seeds_for
from exp001.aggregation import aggregate_records


def records():
    return [{"master_seed":s,"seeds":seeds_for(s),"run_id":f"fixture-{s}","git_commit":"fixture-commit",
             "numpy_version":"2.3.5","formal":True,"execution_status":"VALID","evaluation_flags":[],
             "primary":{a:{"initial_accuracy":.6,"final_accuracy":.7,"initial_contrast":1.,"final_contrast":2.}
                        for a in ("color","shape")}} for s in FORMAL_SEEDS]


@pytest.mark.parametrize("status,flags,missing,expected,warnings",[
    ("VALID",[],False,"SUCCESS",[]),
    ("INVALID",[],False,"NOT_EVALUATED",[]),
    ("EXPERIMENTAL_FAILURE",[],True,"INCONCLUSIVE",[]),
    ("VALID",["PROBE_FAILED"],True,"INCONCLUSIVE",[]),
    ("VALID",["DISTANCE_FAILED"],True,"INCONCLUSIVE",[]),
    ("VALID",["BOOTSTRAP_CI_FAILED"],False,"SUCCESS",["DISTANCE_CI_INCOMPLETE"]),
    ("VALID",["PIXEL_BASELINE_FAILED"],False,"SUCCESS",["CONTROL_INCOMPLETE"]),
    ("VALID",["PIXEL_BASELINE_FAILED","BOOTSTRAP_CI_FAILED"],False,"SUCCESS",["CONTROL_INCOMPLETE","DISTANCE_CI_INCOMPLETE"]),
    ("VALID",["PROBE_FAILED","DISTANCE_FAILED","PIXEL_BASELINE_FAILED"],True,"INCONCLUSIVE",["CONTROL_INCOMPLETE"]),
    ("INVALID",["PROBE_FAILED","PIXEL_BASELINE_FAILED"],True,"NOT_EVALUATED",["CONTROL_INCOMPLETE"]),
])
def test_table_status_precedence(status,flags,missing,expected,warnings):
    rows=records()
    rows[-1].update(execution_status=status,evaluation_flags=flags)
    if missing: rows[-1]["primary"]={}
    result=aggregate_records(rows)
    assert result["classification"]==expected
    assert result["warnings"]==warnings


@pytest.mark.parametrize("change",["four","duplicate","other_seed","other_commit","other_numpy","fixture","missing_commit","bad_seed"])
def test_formal_set_exclusions(change):
    rows=records()
    if change=="four": rows.pop()
    elif change=="duplicate": rows[-1]=deepcopy(rows[0])
    elif change=="other_seed": rows[-1]["master_seed"]=777
    elif change=="other_commit": rows[-1]["git_commit"]="different"
    elif change=="other_numpy": rows[-1]["numpy_version"]="2.4.0"
    elif change=="fixture": rows[-1]["formal"]=False
    elif change=="missing_commit": rows[-1].pop("git_commit")
    else: rows[-1]["seeds"]["analysis_seed"]+=1
    assert aggregate_records(rows)["classification"]=="NOT_EVALUATED"


def deactivate(rows,attribute):
    for row in rows:
        row["primary"][attribute]={"initial_accuracy":.5,"final_accuracy":.5,"initial_contrast":1.,"final_contrast":1.}


@pytest.mark.parametrize("active",["color","shape","both","neither"])
def test_attribute_success(active):
    rows=records()
    for attribute in ("color","shape"):
        if active not in (attribute,"both"): deactivate(rows,attribute)
    result=aggregate_records(rows)
    assert result["classification"]==("NO_EVIDENCE" if active=="neither" else "SUCCESS")


@pytest.mark.parametrize("positive,expected",[(3,"INCONCLUSIVE"),(4,"SUCCESS")])
@pytest.mark.parametrize("metric",["probe","distance"])
def test_four_of_five_boundary(positive,expected,metric):
    rows=records(); deactivate(rows,"shape")
    for row in rows[positive:]:
        if metric=="probe": row["primary"]["color"]["final_accuracy"]=.6
        else:
            row["primary"]["color"]["initial_contrast"]=-1
            row["primary"]["color"]["final_contrast"]=0
    result=aggregate_records(rows)
    assert result["classification"]==expected
    key="probe_positive_count" if metric=="probe" else "final_contrast_positive_count"
    assert result["attributes"]["color"][key]==positive


@pytest.mark.parametrize("initial,final,expected",[(.6,.7,"SUCCESS"),(.600001,.7,"INCONCLUSIVE"),(.59,.699999,"INCONCLUSIVE"),(.7,.7,"INCONCLUSIVE")])
def test_accuracy_equalities(initial,final,expected):
    rows=records(); deactivate(rows,"shape")
    for row in rows: row["primary"]["color"].update(initial_accuracy=initial,final_accuracy=final)
    assert aggregate_records(rows)["classification"]==expected


@pytest.mark.parametrize("initial,final,expected",[(1,1,"INCONCLUSIVE"),(0,0,"INCONCLUSIVE"),(1,1.00000001,"SUCCESS"),(-1,0,"INCONCLUSIVE")])
def test_distance_strict_equalities(initial,final,expected):
    rows=records(); deactivate(rows,"shape")
    for row in rows: row["primary"]["color"].update(initial_contrast=initial,final_contrast=final)
    assert aggregate_records(rows)["classification"]==expected


@pytest.mark.parametrize("probe,distance,expected",[(0,0,"NO_EVIDENCE"),(-.01,-.1,"NO_EVIDENCE"),(.01,0,"INCONCLUSIVE"),(0,.01,"INCONCLUSIVE")])
def test_positive_trend_or_semantics(probe,distance,expected):
    rows=records()
    for a in ("color","shape"): deactivate(rows,a)
    for row in rows:
        row["primary"]["color"].update(final_accuracy=.5+probe,final_contrast=1+distance)
    assert aggregate_records(rows)["classification"]==expected


@pytest.mark.parametrize("bad",[None,np.nan,np.inf])
def test_missing_nonfinite_metrics(bad):
    rows=records(); rows[0]["primary"]["color"]["initial_accuracy"]=bad
    assert aggregate_records(rows)["classification"]=="INCONCLUSIVE"


def test_all_recorded_conditions_recomputable():
    result=aggregate_records(records())
    for attribute in ("color","shape"):
        a=result["attributes"][attribute]
        assert a["probe_delta"]==[.1]*5
        assert a["distance_delta"]==[1]*5
        assert a["medians"]["final_accuracy"]==.7
        assert a["probe_positive_count"]==5 and a["final_contrast_positive_count"]==5
        assert all(a["conditions"].values())


def test_accuracy_count_boundary_without_tolerance():
    rows=records()
    for row in rows:
        row["primary"]["color"].update(initial_accuracy=320/900,final_accuracy=410/900,
            initial_correct=320,initial_total=900,final_correct=410,final_total=900)
    result=aggregate_records(rows)
    assert result["attributes"]["color"]["probe_delta"]==[.1]*5
    assert result["attributes"]["color"]["conditions"]["median_probe_delta_at_least_010"]


def test_probe_and_distance_must_succeed_on_same_attribute():
    rows=records()
    for row in rows:
        row["primary"]["color"]["final_contrast"]=1
        row["primary"]["shape"]["final_accuracy"]=.6
    assert aggregate_records(rows)["classification"]=="INCONCLUSIVE"


@pytest.mark.parametrize("flags",[["BOOTSTRAP_CI_FAILED"],["PIXEL_BASELINE_FAILED"],["BOOTSTRAP_CI_FAILED","PIXEL_BASELINE_FAILED"]])
def test_secondary_failures_also_allow_no_evidence(flags):
    rows=records()
    for a in ("color","shape"): deactivate(rows,a)
    rows[0]["evaluation_flags"]=flags
    assert aggregate_records(rows)["classification"]=="NO_EVIDENCE"
