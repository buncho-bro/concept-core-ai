# VERIFICATION_PLAN

FIX 後も formal RUN には進まず VERIFY を実施する。

1. successor baseline の Human authorization provenance を固定・検証し、未承認または改竄済み reference の freeze を拒否する nonformal tests を追加する。
2. process-start OMP/MKL environment と frozen manifest values の一致を、runner が scientific execution より前に検証するか、fresh-process launcher が強制することを確認する。全6 performance knobs の mismatch tests を追加する。
3. clean source stateで full suite を実行し、verification receipt・implementation fingerprint・environment・normative document identityを記録する。
4. baseline manifest integrity、canonical first-registration、crash window、retry non-replacement、canonical-only aggregationを再度検証する。
5. performance benchmark、real baseline freeze、formal seeds、formal aggregation、formal RUN は行わない。
