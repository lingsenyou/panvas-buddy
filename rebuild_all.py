"""
Everything that has to be re-run after the operator changes, in the right order.

Doing this by hand is how a stale artefact ships. Three have already nearly done
so in this project: a workbench built before a refit that still carried the old
baseline rates, a Word file whose competing-interests field was an unfilled
instruction to the authors, and a release archive containing both.

A fourth has since been caught: after the Route B refit the figures were regenerated
but the sentences quoting them were not, so the manuscript printed tau_sc = 124 and 261
days beside a figure printing 128 and 287. Regenerating artefacts cannot fix prose, so
the last step now re-derives every number the prose quotes and compares it with what is
written -- see tests/check_prose.py.

    python rebuild_all.py            # everything except the calibration
    python rebuild_all.py --refit    # calibration too (several minutes)

The calibration is opt-in because it takes minutes and is not always what changed.
Anything that consumes panvas/theta.json is downstream of it, so if you refit you
must run the rest, which is why --refit implies the full sequence.
"""

import argparse
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))

STEPS = [
    ("calibrate.py", "fit the operator's constants on the audited anchors", True),
    ("export_anchors.py", "anchor table with provenance and predictions", False),
    ("export_model.py", "dump the operator for the browser workbench", False),
    ("inner_loop.py", "harness search with the operator frozen", False),
    ("experiments.py", "E1-E3", False),
    ("make_figures.py", "the three preprint figures", False),
    ("build_site.py", "the public page at lingsenyou.com/suitcordance", False),
    ("make_docx.py", "the submission Word file", False),
    ("tests/make_js_reference.py", "reference values for the JS parity check", False),
    ("tests/test_operator.py", "property tests, including the structural ones", False),
    ("tests/check_prose.py", "the numbers quoted in prose still match the code", False),
    ("make_bundle.py", "reassemble the folder that goes to the supervisor", False),
]


def run(script: str, why: str) -> float:
    print(f"\n=== {script}  ({why})", flush=True)
    t0 = time.time()
    # The children are told to emit UTF-8, so decode as UTF-8 here too. Without the
    # explicit encoding, subprocess falls back to the locale codec -- gbk on this
    # machine -- and the first step that printed a Chinese filename crashed the whole
    # rebuild on a decode error rather than reporting the step's result.
    r = subprocess.run([sys.executable, "-u", os.path.join(HERE, script)],
                       cwd=HERE, capture_output=True, text=True,
                       encoding="utf-8", errors="replace",
                       env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    dt = time.time() - t0
    log = os.path.join(HERE, "out", os.path.basename(script).replace(".py", ".log"))
    os.makedirs(os.path.dirname(log), exist_ok=True)
    with open(log, "w", encoding="utf-8") as fh:
        fh.write(r.stdout or "")
        if (r.stderr or "").strip():
            fh.write(os.linesep + "--- stderr ---" + os.linesep + r.stderr)
    tail = [ln for ln in (r.stdout or "").strip().splitlines() if ln.strip()][-4:]
    for ln in tail:
        print("   " + ln)
    if r.returncode != 0:
        print((r.stderr or "").strip()[-1500:])
        raise SystemExit(f"{script} failed after {dt:.0f}s")
    print(f"   [{dt:.0f}s]")
    return dt


def rebuild_workbench() -> None:
    """The private Chinese workbench is built here rather than by its own script."""
    src = open(os.path.join(HERE, "app", "workbench.src.html"), encoding="utf-8").read()
    model = open(os.path.join(HERE, "out", "model.json"), encoding="utf-8").read()
    if "__MODEL__" not in src:
        raise SystemExit("app/workbench.src.html has no __MODEL__ placeholder")
    with open(os.path.join(HERE, "app", "workbench.html"), "w",
              encoding="utf-8", newline="") as fh:
        fh.write(src.replace("__MODEL__", model))
    print("\n=== app/workbench.html  (private workbench, rebuilt on the current model)")


def rebuild_archive() -> None:
    import zipfile
    files = subprocess.run(["git", "ls-files"], cwd=HERE,
                           capture_output=True, text=True).stdout.split()
    out = os.path.join(HERE, "out", "panvas-buddy-v0.1.0.zip")
    if os.path.exists(out):
        os.remove(out)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(set(files)):
            if f.startswith("out/") and f.endswith(".zip"):
                continue
            zf.write(os.path.join(HERE, f), arcname="panvas-buddy-0.1.0/" + f)
    print(f"\n=== out/panvas-buddy-v0.1.0.zip  "
          f"({os.path.getsize(out) / 1e6:.2f} MB, {len(files)} files)")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--refit", action="store_true",
                    help="re-run the calibration first (several minutes)")
    args = ap.parse_args()

    total = 0.0
    for script, why, is_calibration in STEPS:
        if is_calibration and not args.refit:
            print(f"\n=== {script}  SKIPPED (pass --refit to run it)")
            continue
        total += run(script, why)
        if script == "export_model.py":
            rebuild_workbench()

    rebuild_archive()

    print(f"\nall steps passed in {total / 60:.1f} minutes")
    print("\nStill to do by hand, because they touch the world:")
    print("  * push the site repository (lingsenyou.github.io)")
    print("  * republish the private workbench artifact")
    print("  * re-run the JS parity check in the browser (tests/js_parity.md);")
    print("    the operator changed, so the published page and the paper have")
    print("    diverged until you do")


if __name__ == "__main__":
    main()
