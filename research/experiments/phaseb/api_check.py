"""
Phase B: API / report / identity / reproducibility / error-handling validation.

Starts its OWN backend (127.0.0.1:8011, throw-away data dir under the system temp dir) so
it never touches a developer's running backend or data. Requests are sent one at a time
(TECH-DEBT.md #10: overlapping requests can crash the shared SQLite connection).

  H1  capture_id returned by the API == independently computed SHA-256, for every capture
  H2  same bytes under another filename -> same capture_id (idempotent replay);
      one flipped byte -> different capture_id
  R1  `force=true` re-analyses N times: assessment_id / findings / score identical;
      what differs between runs is shown, not assumed
  R2  fetching one stored run's reports repeatedly returns identical bytes
  R3  rendering the same assessment dict twice in-process (render_bytes) returns identical bytes
  C1  one run, every format: API assessment == JSON report == HTML == PDF text == mr == both
  L1  language behaviour: draft notice, English authoritative, bilingual contains English
  E1  error handling and hostile input (status codes, no 5xx, backend healthy afterwards)

    PYTHONPATH=src python3 research/experiments/phaseb/api_check.py
Needs fastapi/uvicorn/httpx/pypdf (the project's own test dependencies) and tshark.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Any, Dict, List

import httpx

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
PORT = 8011
BASE = f"http://127.0.0.1:{PORT}/api/v1"
G = os.path.join(ROOT, "demo", "captures", "deepdive_cross_session_control_endpoint.pcap")
B = os.path.join(ROOT, "demo", "captures", "scene_b_certificate_honesty.pcap")


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def start() -> tuple:
    data = tempfile.mkdtemp(prefix="sms-phaseb-")
    env = dict(os.environ, PYTHONPATH=os.path.join(ROOT, "src"))
    p = subprocess.Popen([sys.executable, "-m", "nyaysaakshya.backend", "--host", "127.0.0.1",
                          "--port", str(PORT), "--data-dir", data],
                         env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(80):
        try:
            if httpx.get(f"{BASE}/health", timeout=1).status_code == 200:
                return p, data
        except Exception:
            time.sleep(0.25)
    p.kill()
    raise RuntimeError("backend did not start")


def upload(c: httpx.Client, name: str, data: bytes, **params) -> httpx.Response:
    return c.post(f"{BASE}/analyses", params=params, files={"file": (name, data, "application/octet-stream")})


def main() -> None:
    from nyaysaakshya.reporting.service import render_bytes
    import pypdf

    proc, data_dir = start()
    c = httpx.Client(timeout=180)
    out: Dict[str, Any] = {}
    try:
        health = c.get(f"{BASE}/health").json()
        out["environment"] = {"health": {k: health[k] for k in ("version", "backend_schema_version", "posture_engine_version", "tshark")},
                              "python": sys.version.split()[0]}

        # ---------------- H1: hash identity for every capture ----------------
        caps: List[str] = []
        for d in ("oq33r/out", "oq28/pcaps", "oq46_47/oq46", "oq46_47/oq47", "p11cert/out", "oq36/corpus/genB", "oq36/corpus/genC"):
            full = os.path.join(ROOT, "research", "experiments", d)
            caps += [os.path.join(full, f) for f in sorted(os.listdir(full)) if f.endswith(".pcap")]
        h1_bad, replays, runs = [], 0, {}
        seen: Dict[str, str] = {}
        for p in caps:
            raw = open(p, "rb").read()
            r = upload(c, os.path.basename(p), raw)
            j = r.json()
            if r.status_code != 201 or j.get("capture_id") != sha(raw):
                h1_bad.append({"file": os.path.basename(p), "status": r.status_code, "capture_id": j.get("capture_id"), "sha": sha(raw)})
            if j.get("replayed"):
                replays += 1
            runs[os.path.basename(p)] = j
        out["H1_capture_hash"] = {"captures_uploaded": len(caps), "mismatches": h1_bad,
                                  "note": "identical bytes under two names in the corpus return replayed=true",
                                  "replayed_on_first_upload": replays}

        # ---------------- H2: rename / one-byte flip -------------------------
        rawG = open(G, "rb").read()
        base = upload(c, "deepdive_cross_session_control_endpoint.pcap", rawG).json()
        ren = upload(c, "completely_different_name.pcap", rawG).json()
        flipped = bytearray(rawG)
        flipped[-1] ^= 0x01          # last payload byte of the last packet
        fl = upload(c, "flipped.pcap", bytes(flipped))
        flj = fl.json()
        out["H2_identity"] = {
            "original": {"capture_id": base["capture_id"], "run_id": base["run_id"]},
            "renamed_same_bytes": {"capture_id": ren["capture_id"], "same_capture_id": ren["capture_id"] == base["capture_id"],
                                   "replayed": ren.get("replayed"), "same_run": ren["run_id"] == base["run_id"]},
            "one_byte_flipped": {"status": fl.status_code, "capture_id": flj.get("capture_id"),
                                 "differs": flj.get("capture_id") != base["capture_id"],
                                 "sha_matches_local": flj.get("capture_id") == sha(bytes(flipped)),
                                 "assessment_id": flj.get("assessment_id")},
        }

        # ---------------- R1: forced re-analysis ---------------------------------
        r1: Dict[str, Any] = {}
        for label, path in (("deepdive(G)", G), ("scene_b", B)):
            raw = open(path, "rb").read()
            recs = []
            for i in range(5):
                time.sleep(1.3)   # generated_at has 1-second resolution; force distinct timestamps
                j = upload(c, os.path.basename(path), raw, force="true").json()
                a = c.get(f"{BASE}/analyses/{j['run_id']}/assessment").json()["assessment"]
                rep = c.get(f"{BASE}/analyses/{j['run_id']}/reports/json").content
                recs.append({"run_id": j["run_id"], "assessment_id": a["assessment_id"], "generated_at": a["generated_at"],
                             "score": a["score"]["value"], "band": a["score"]["band"],
                             "findings": sorted((x["rule_id"], x["status"]) for x in a.get("prioritised", [])) if False else None,
                             "assessment_canon": sha(json.dumps({k: v for k, v in a.items() if k not in ("generated_at", "run_id")},
                                                                sort_keys=True).encode()),
                             "json_report_sha": sha(rep), "json_report": json.loads(rep)})
            diff_keys = set()
            for r in recs[1:]:
                for k in set(r["json_report"]) | set(recs[0]["json_report"]):
                    if r["json_report"].get(k) != recs[0]["json_report"].get(k):
                        diff_keys.add(k)
            r1[label] = {
                "runs": len(recs), "distinct_run_ids": len({r["run_id"] for r in recs}),
                "distinct_assessment_ids": sorted({r["assessment_id"] for r in recs}),
                "distinct_scores": sorted({r["score"] for r in recs}),
                "distinct_assessment_bodies_excluding_generated_at_and_run_id": len({r["assessment_canon"] for r in recs}),
                "distinct_generated_at": len({r["generated_at"] for r in recs}),
                "distinct_json_report_bytes": len({r["json_report_sha"] for r in recs}),
                "json_report_top_level_keys_that_differ": sorted(diff_keys),
            }
        out["R1_forced_reanalysis"] = r1

        # ---------------- R2 / R3 -----------------------------------------------
        run_id = base["run_id"]
        r2 = {}
        for fmt, q in (("json", {}), ("html", {}), ("pdf", {}), ("html", {"lang": "mr"}), ("html", {"lang": "both"})):
            hs = {sha(c.get(f"{BASE}/analyses/{run_id}/reports/{fmt}", params=q).content) for _ in range(5)}
            r2[f"{fmt}{'?lang=' + q['lang'] if q else ''}"] = {"fetches": 5, "distinct_byte_hashes": len(hs)}
        out["R2_stored_report_refetch"] = r2
        a = c.get(f"{BASE}/analyses/{run_id}/assessment").json()["assessment"]
        r3 = {}
        for fmt, lang in (("json", "en"), ("html", "en"), ("pdf", "en"), ("html", "mr"), ("html", "both")):
            x, y = render_bytes(a, fmt, lang)[0], render_bytes(a, fmt, lang)[0]
            r3[f"{fmt}/{lang}"] = {"identical": x == y, "bytes": len(x), "sha256_16": sha(x)[:16]}
        out["R3_render_twice_in_process"] = r3

        # ---------------- C1: cross-format consistency ----------------------------
        api_a = c.get(f"{BASE}/analyses/{run_id}/assessment").json()
        asm = api_a["assessment"]
        jrep = json.loads(c.get(f"{BASE}/analyses/{run_id}/reports/json").content)
        html_en = c.get(f"{BASE}/analyses/{run_id}/reports/html").text
        pdf_b = c.get(f"{BASE}/analyses/{run_id}/reports/pdf").content
        pdf_t = " ".join((pg.extract_text() or "") for pg in pypdf.PdfReader(io.BytesIO(pdf_b)).pages)
        html_mr = c.get(f"{BASE}/analyses/{run_id}/reports/html", params={"lang": "mr"}).text
        html_both = c.get(f"{BASE}/analyses/{run_id}/reports/html", params={"lang": "both"}).text

        def flat(o: Any) -> str:
            return json.dumps(o, sort_keys=True, default=str)
        jflat = flat(jrep)
        score_txt = f"{asm['score']['value']:.2f}"
        first_title = api_a["assessment"]["issue_groups"][0]["issue_class"] if asm.get("issue_groups") else ""
        pdf_norm = re.sub(r"\s+", "", pdf_t)
        checks: Dict[str, Dict[str, bool]] = {}
        for name, text in (("json", jflat), ("html_en", html_en), ("pdf", pdf_t), ("html_mr", html_mr), ("html_both", html_both)):
            t = re.sub(r"\s+", "", text) if name == "pdf" else text
            checks[name] = {
                "assessment_id": asm["assessment_id"] in t,
                "capture_sha256": (asm["capture_id"] in t) if name != "pdf" else (asm["capture_id"][:32] in t or asm["capture_id"] in t),
                "score_22.15": score_txt in t,
                "generated_at_date": asm["generated_at"][:10] in t,
            }
        out["C1_cross_format"] = {
            "run": {"capture": os.path.basename(G), "assessment_id": asm["assessment_id"], "score": score_txt, "generated_at": asm["generated_at"]},
            "json_report_equals_api_assessment_exactly": jrep == asm,
            "contains": checks,
            "pdf_pages": len(pypdf.PdfReader(io.BytesIO(pdf_b)).pages),
        }

        # ---------------- L1: language behaviour ----------------------------------
        reports_meta = c.get(f"{BASE}/analyses/{run_id}/reports").json()["items"]
        mr_meta = [m for m in reports_meta if m.get("language") == "mr"]
        both_meta = [m for m in reports_meta if m.get("language") == "both"]
        pdf_mr = c.get(f"{BASE}/analyses/{run_id}/reports/pdf", params={"lang": "mr"})
        json_mr = c.get(f"{BASE}/analyses/{run_id}/reports/json", params={"lang": "mr"})
        bad_lang = c.get(f"{BASE}/analyses/{run_id}/reports/html", params={"lang": "xx"})
        def vis(h: str) -> str:
            h = re.sub(r"(?is)<(script|style)[^>]*>.*?</\\1>", " ", h)
            return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", h)).strip()
        en_body = re.search(r"(?is)<body[^>]*>(.*)</body>", html_en).group(1)
        both_en = html_both[html_both.index('id="en-report"'):]
        en_text_ok = vis(en_body) in vis(both_en)
        raw_reports_meta = c.get(f"{BASE}/analyses/{run_id}/reports").json()
        out["L1_language"] = {
            "reports_list_keys": sorted(raw_reports_meta.keys()),
            "reports_list_item_languages": sorted({(m.get("format"), m.get("language")) for m in raw_reports_meta["items"]}),
            "reports_list_item_translation_status": sorted({str(m.get("translation_status")) for m in raw_reports_meta["items"]}),
            "translations_block": raw_reports_meta.get("translations"),
            "en_has_draft_notice_phrase": "मसुदा" in html_en,
            "mr_has_draft_notice_phrase": "मसुदा" in html_mr,
            "both_has_draft_notice_phrase": "मसुदा" in html_both,
            "both_contains_english_report_bytes_verbatim": html_en in html_both,
            "both_english_section_text_contains_english_report_text": en_text_ok,
            "both_has_authoritative_english_banner": "English original" in html_both and 'id="en-report"' in html_both,
            "mr_metadata_translation_status": [m.get("translation_status") for m in mr_meta],
            "both_metadata_translation_status": [m.get("translation_status") for m in both_meta],
            "en_metadata_translation_status": [m.get("translation_status") for m in reports_meta if m.get("language") == "en"],
            "pdf_lang_mr": [pdf_mr.status_code, (pdf_mr.json().get("error") or pdf_mr.json()).get("code") if pdf_mr.headers.get("content-type", "").startswith("application/json") else None],
            "json_lang_mr": [json_mr.status_code, (json_mr.json().get("error") or json_mr.json()).get("code") if json_mr.headers.get("content-type", "").startswith("application/json") else None],
            "invalid_lang_xx": bad_lang.status_code,
            "mr_html_lang_attribute": re.findall(r'<html[^>]*lang="([^"]+)"', html_mr)[:1],
        }

        # ---------------- E1: errors & hostile input -------------------------------
        e1: List[Dict[str, Any]] = []

        def rec(name: str, r: httpx.Response) -> None:
            body = ""
            if r.status_code == 201:
                try:
                    a2 = c.get(f"{BASE}/analyses/{r.json()['run_id']}/assessment").json()
                    e1_extra = {"band": a2["assessment"]["score"]["band"], "score": a2["assessment"]["score"]["value"],
                                "warnings": r.json().get("warnings")}
                except Exception:
                    e1_extra = {}
                e1.append({"case": name + " [detail]", "status": 201, "body": json.dumps(e1_extra)})
            try:
                body = json.dumps(r.json())[:160]
            except Exception:
                body = r.text[:80]
            e1.append({"case": name, "status": r.status_code, "body": body})

        rec("garbage bytes as .pcap", upload(c, "garbage.pcap", b"this is not a capture " * 50))
        rec("empty file", upload(c, "empty.pcap", b""))
        rec("truncated pcap header (30 bytes)", upload(c, "trunc.pcap", rawG[:30]))
        rec("valid pcap truncated mid-packet", upload(c, "midpkt.pcap", rawG[: len(rawG) // 2 + 7]))
        rec("pcap bytes with .txt name", upload(c, "capture.txt", rawG))
        trav = bytearray(rawG); trav[-3] ^= 0x01
        rec("traversal filename (fresh bytes)", upload(c, "../../../../etc/passwd.pcap", bytes(trav)))
        rec("multipart without file", c.post(f"{BASE}/analyses", files={"nofile": ("x", b"y")}))
        rec("unsupported content type", c.post(f"{BASE}/analyses", content=b"{}", headers={"content-type": "application/json"}))
        rec("unknown run id", c.get(f"{BASE}/analyses/00000000000000000000000000000000"))
        rec("malformed run id (traversal)", c.get(f"{BASE}/analyses/..%2f..%2fetc%2fpasswd/assessment"))
        rec("unknown report format", c.get(f"{BASE}/analyses/{run_id}/reports/exe"))
        rec("octet-stream body upload", c.post(f"{BASE}/analyses", content=rawG, headers={"content-type": "application/octet-stream", "x-filename": "raw.pcap"}))
        out["E1_errors"] = {"cases": e1, "any_5xx": any(x["status"] >= 500 for x in e1),
                            "health_after": c.get(f"{BASE}/health").json()["status"]}

        # hostile content in a capture: prompt injection + HTML escaping
        xp = os.path.join(ROOT, "research", "experiments", "oq28", "pcaps", "X_prompt_injection.pcap")
        xj = upload(c, "X_prompt_injection.pcap", open(xp, "rb").read()).json()
        xhtml = c.get(f"{BASE}/analyses/{xj['run_id']}/reports/html").text
        xa = c.get(f"{BASE}/analyses/{xj['run_id']}/assessment").json()["assessment"]
        uniq = bytearray(rawG)
        uniq[-2] ^= 0x01
        hostile_name = '"><script>alert(1)</script>../../x.pcap'
        fj = upload(c, hostile_name, bytes(uniq)).json()
        fhtml = c.get(f"{BASE}/analyses/{fj['run_id']}/reports/html").text
        fjson = c.get(f"{BASE}/analyses/{fj['run_id']}/reports/json").text
        disp = c.get(f"{BASE}/analyses/{fj['run_id']}/reports/html", params={"download": "true"}).headers.get("content-disposition")
        runrec = c.get(f"{BASE}/analyses/{fj['run_id']}").json()
        out["E1_hostile"] = {
            "prompt_injection_capture": {"band": xa["score"]["band"], "score": xa["score"]["value"],
                                         "injection_text_in_html_report": "IGNORE ALL PREVIOUS" in xhtml,
                                         "report_says_SECURE_posture": bool(re.search(r"posture\s*[:=]\s*SECURE", xhtml, re.I))},
            "fresh_run_new_capture": fj.get("replayed") is False or fj.get("replayed") is None,
            "stored_source_filename": runrec.get("source_filename"),
            "html_report_contains_raw_script_tag": "<script" in fhtml.lower(),
            "html_report_contains_hostile_filename_text": "alert(1)" in fhtml,
            "json_report_contains_hostile_filename_text": "alert(1)" in fjson,
            "download_content_disposition": disp,
        }
    finally:
        c.close()
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except Exception:
            proc.kill()
        shutil.rmtree(data_dir, ignore_errors=True)

    # ---------------- R4: independent re-analysis in two FRESH data dirs ----------------
    # Storage is idempotent on assessment_id (repository.store_assessment keeps the first stored
    # document), so only separate databases give an honest re-analysis. Spaced > 1 s apart.
    snaps = []
    for _ in range(2):
        pr, dd = start()
        try:
            cl = httpx.Client(timeout=180)
            row = {}
            for label, path in (("deepdive(G)", G), ("scene_b", B), ("weak_cert", os.path.join(ROOT, "demo", "captures", "backup_weak_certificate.pcap"))):
                j = upload(cl, os.path.basename(path), open(path, "rb").read()).json()
                rid = j["run_id"]
                asm = cl.get(f"{BASE}/analyses/{rid}/assessment").json()["assessment"]
                row[label] = {"run_id": rid, "assessment": asm,
                              "reports": {k: cl.get(f"{BASE}/analyses/{rid}/reports/{f}", params=q).content
                                          for k, (f, q) in {"json": ("json", {}), "html": ("html", {}), "pdf": ("pdf", {}),
                                                            "mr": ("html", {"lang": "mr"}), "both": ("html", {"lang": "both"})}.items()}}
            cl.close()
        finally:
            pr.terminate()
            pr.wait(timeout=10)
            shutil.rmtree(dd, ignore_errors=True)
        snaps.append(row)
        time.sleep(1.5)
    r4: Dict[str, Any] = {}
    for label in snaps[0]:
        a0, a1 = snaps[0][label]["assessment"], snaps[1][label]["assessment"]
        diff_keys = sorted(k for k in set(a0) | set(a1) if a0.get(k) != a1.get(k))
        body_equal = {k: v for k, v in a0.items() if k not in ("generated_at", "run_id")} == \
                     {k: v for k, v in a1.items() if k not in ("generated_at", "run_id")}
        r4[label] = {
            "assessment_id_run1": a0["assessment_id"], "assessment_id_run2": a1["assessment_id"],
            "assessment_id_equal": a0["assessment_id"] == a1["assessment_id"],
            "assessment_keys_that_differ": diff_keys,
            "assessment_equal_excluding_generated_at_and_run_id": body_equal,
            "generated_at": [a0["generated_at"], a1["generated_at"]],
            "report_bytes_identical": {k: snaps[0][label]["reports"][k] == snaps[1][label]["reports"][k]
                                       for k in snaps[0][label]["reports"]},
        }
    out["R4_fresh_data_dirs_reanalysis"] = r4

    with open(os.path.join(HERE, "results", "api_check.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True, default=str)
    print(json.dumps(out, indent=1, sort_keys=True, default=str)[:9000])


if __name__ == "__main__":
    main()
