"""
Assemble the folder that goes to the supervisor, from the repository.

This was done by hand once, and by the next day the folder held a Word file built from a
manuscript that had since been corrected, beside figures that had been regenerated. The
numbered names are for a reader, not for the code, so the mapping lives here and the
folder is rebuilt from source every time rather than patched.

    python make_bundle.py
"""

import hashlib
import io
import os
import shutil
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
DEST = os.path.join(os.path.dirname(HERE), "panvas_for_shen")
ZIP = "PanVas-Buddy_给沈老师_2026-09-19.zip"

# destination name <- source, relative to the repository root
COPY = [
    ("00_先读我_项目简报.md", "给沈老师_项目简报.md"),
    ("01_稿件_Suitcordance_preprint.docx", "preprint/Suitcordance_preprint.docx"),
    ("02_图1_四轴轨迹与tau_sc.png", "out/figures/fig1_trajectories.png"),
    ("03_图2_标定_12条锚点.png", "out/figures/fig2_calibration.png"),
    ("04_图3_样本效率与跨床迁移.png", "out/figures/fig3_experiments.png"),
    ("05_图4_精度与生理可信的前沿.png", "out/figures/fig4_frontier.png"),
    ("06_已知缺陷_已修与仍开.md", "KNOWN_DEFECTS.md"),
    ("07_引文审计全记录_49个agent.txt", "audit/citation_audit_2026-09-19.txt"),
    ("08_引文审计_方法说明.md", "audit/README.md"),
    ("09_项目说明_README.md", "README.md"),
    ("10_全部代码_panvas-buddy-v0.1.0.zip", "out/panvas-buddy-v0.1.0.zip"),
]

# written and maintained only in the bundle, never copied over
NATIVE = ["00b_给GPT阅读的完整技术简报.md", "00c_给GPT阅读的技术简报_v2.md"]


def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 16), b""):
            h.update(blk)
    return h.hexdigest()[:12]


def main():
    os.makedirs(DEST, exist_ok=True)
    changed, same = [], 0
    for name, src in COPY:
        s = os.path.join(HERE, src)
        d = os.path.join(DEST, name)
        if not os.path.exists(s):
            raise SystemExit("missing source: " + src)
        if os.path.exists(d) and digest(s) == digest(d):
            same += 1
            continue
        shutil.copy2(s, d)
        changed.append(name)

    for name in NATIVE:
        if not os.path.exists(os.path.join(DEST, name)):
            raise SystemExit("bundle-native file missing, and this script cannot "
                             "regenerate it: " + name)

    members = [n for n, _ in COPY] + NATIVE
    zp = os.path.join(DEST, ZIP)
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for n in sorted(members):
            z.write(os.path.join(DEST, n), n)

    for n in changed:
        print("  refreshed  " + n)
    print("%d files refreshed, %d already current, %d in the archive (%.1f MB)"
          % (len(changed), same, len(members), os.path.getsize(zp) / 1e6))
    print("bundle at " + DEST)


if __name__ == "__main__":
    main()
