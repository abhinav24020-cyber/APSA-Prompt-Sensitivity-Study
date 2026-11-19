"""Build a self-contained HTML viewer for every anchor-paired output in a study.

Reads ``processed/analysis_pairs.csv`` (produced by ``experiments/analyze_study.py``) and
writes ``analysis/output_viewer.html``: filter by model, category, operator, condition,
correctness change or taxonomy label, and compare prompts and outputs side by side.

Usage:
  .\\.venv\\Scripts\\python.exe scripts\\build_output_viewer.py --study-dir results\\study\\main_v1
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent

COLUMNS = [
    "pair_id", "model", "prompt_id", "task_category", "condition", "operator", "family", "repetition",
    "perturbed_prompt", "anchor_output", "comparison_output", "anchor_correct", "comparison_correct",
    "d_in_char", "d_in_sem", "d_out_sem", "d_out_char", "d_out_token", "answer_changed", "taxonomy",
    "audit_status", "audit_kind", "semantic_risk", "anchor_record_id", "comparison_record_id",
]

HTML = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>APSA Output Viewer</title>
<style>
:root{--bg:#fcfcfb;--panel:#ffffff;--ink:#0b0b0b;--ink2:#52514e;--muted:#8a8984;--line:#e4e3df;
--accent:#2a78d6;--bad:#c62f2e;--good:#0b7a0b;--del:#fde2e1;--ins:#dff3e4;--chip:#f1f0ec}
@media (prefers-color-scheme:dark){:root{--bg:#1a1a19;--panel:#222221;--ink:#f0efec;--ink2:#c3c2b7;
--muted:#8f8e86;--line:#3a3936;--accent:#5b9cec;--bad:#ef7372;--good:#4cc24c;--del:#5a2524;--ins:#1f4a2a;--chip:#2c2c2a}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
header{padding:16px;border-bottom:1px solid var(--line);position:sticky;top:0;background:var(--bg);z-index:2}
h1{font-size:18px;margin:0 0 4px}.sub{color:var(--ink2);font-size:12px}
.filters{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}
select,input{font:inherit;padding:5px 8px;border:1px solid var(--line);border-radius:6px;background:var(--panel);color:var(--ink);max-width:100%}
main{padding:16px;max-width:1300px;margin:0 auto}
.count{color:var(--ink2);margin-bottom:10px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;margin-bottom:14px;overflow:hidden}
.head{display:flex;flex-wrap:wrap;gap:6px;align-items:center;padding:10px 12px;border-bottom:1px solid var(--line)}
.chip{background:var(--chip);border-radius:999px;padding:2px 9px;font-size:12px;color:var(--ink2)}
.chip.b{font-weight:600;color:var(--ink)}.chip.bad{color:var(--bad);font-weight:600}.chip.good{color:var(--good);font-weight:600}
.metrics{font-size:12px;color:var(--ink2);padding:6px 12px;border-bottom:1px solid var(--line)}
.prompt{padding:8px 12px;border-bottom:1px solid var(--line);font-size:13px}
.prompt del{background:var(--del);text-decoration:line-through}.prompt ins{background:var(--ins);text-decoration:none}
.cols{display:grid;grid-template-columns:1fr 1fr}.cols>div{padding:10px 12px;min-width:0}
.cols>div+div{border-left:1px solid var(--line)}
.lbl{font-size:11px;text-transform:uppercase;letter-spacing:.04em;color:var(--muted);margin-bottom:4px}
pre{white-space:pre-wrap;word-break:break-word;margin:0;font:12.5px/1.45 ui-monospace,Consolas,monospace;max-height:420px;overflow:auto}
.more{text-align:center;margin:16px}button{font:inherit;padding:7px 14px;border-radius:6px;border:1px solid var(--line);background:var(--panel);color:var(--ink);cursor:pointer}
@media (max-width:760px){.cols{grid-template-columns:1fr}.cols>div+div{border-left:0;border-top:1px solid var(--line)}}
</style></head><body>
<header><h1>APSA Output Viewer: __STUDY__</h1>
<div class="sub">Every control and treatment output paired with the anchor (original-prompt) output of the same model and prompt. Live API data only. Correctness: answer key or unit tests (automated, not human).</div>
<div class="filters">
<select id="f_model"></select><select id="f_cat"></select><select id="f_op"></select><select id="f_cond"></select>
<select id="f_flip"><option value="">any correctness</option><option value="c2i">correct → incorrect</option><option value="i2c">incorrect → correct</option><option value="flip">any flip</option><option value="same">no flip</option></select>
<select id="f_tax"></select><select id="f_audit"></select>
<select id="f_sort"><option value="">original order</option><option value="dsem">largest output change first</option><option value="din">smallest input change first</option></select>
<input id="f_q" placeholder="search prompt id / text" size="22">
</div></header>
<main><div class="count" id="count"></div><div id="list"></div><div class="more"><button id="more">Show 50 more</button></div></main>
<script>
const DATA = __DATA__;
const PROMPTS = __PROMPTS__;
const $ = id => document.getElementById(id);
function fill(id, label, key){const vals=[...new Set(DATA.map(d=>d[key]).filter(v=>v!==null&&v!==undefined))].sort();
 $(id).innerHTML=`<option value="">all ${label}</option>`+vals.map(v=>`<option>${v}</option>`).join("");}
fill("f_model","models","model");fill("f_cat","categories","task_category");fill("f_op","operators","operator");
fill("f_cond","conditions","condition");fill("f_tax","taxonomy labels","taxonomy");fill("f_audit","audit statuses","audit_status");
const esc = s => (s??"").toString().replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));
function wordDiff(a,b){const A=a.split(/(\s+)/),B=b.split(/(\s+)/);const n=A.length,m=B.length;
 if(n*m>250000) return esc(b);
 const L=Array.from({length:n+1},()=>new Int32Array(m+1));
 for(let i=n-1;i>=0;i--)for(let j=m-1;j>=0;j--)L[i][j]=A[i]===B[j]?L[i+1][j+1]+1:Math.max(L[i+1][j],L[i][j+1]);
 let i=0,j=0,out="";while(i<n&&j<m){if(A[i]===B[j]){out+=esc(A[i]);i++;j++;}else if(L[i+1][j]>=L[i][j+1]){out+=`<del>${esc(A[i])}</del>`;i++;}else{out+=`<ins>${esc(B[j])}</ins>`;j++;}}
 while(i<n)out+=`<del>${esc(A[i++])}</del>`;while(j<m)out+=`<ins>${esc(B[j++])}</ins>`;return out;}
const f3 = v => v===null||v===undefined||Number.isNaN(v) ? "–" : Number(v).toFixed(3);
const corr = v => v===true?"✔ correct":v===false?"✘ incorrect":"not scored";
let shown=50, filtered=[];
function apply(){const g=id=>$(id).value;const q=g("f_q").toLowerCase();
 filtered=DATA.filter(d=>(!g("f_model")||d.model===g("f_model"))&&(!g("f_cat")||d.task_category===g("f_cat"))
 &&(!g("f_op")||d.operator===g("f_op"))&&(!g("f_cond")||d.condition===g("f_cond"))&&(!g("f_tax")||d.taxonomy===g("f_tax"))
 &&(!g("f_audit")||d.audit_status===g("f_audit"))
 &&(!g("f_flip")||(g("f_flip")==="c2i"&&d.anchor_correct===true&&d.comparison_correct===false)||(g("f_flip")==="i2c"&&d.anchor_correct===false&&d.comparison_correct===true)
   ||(g("f_flip")==="flip"&&d.anchor_correct!==null&&d.comparison_correct!==null&&d.anchor_correct!==d.comparison_correct)||(g("f_flip")==="same"&&d.anchor_correct===d.comparison_correct))
 &&(!q||d.prompt_id.toLowerCase().includes(q)||(PROMPTS[d.prompt_id]||"").toLowerCase().includes(q)));
 if(g("f_sort")==="dsem")filtered.sort((a,b)=>b.d_out_sem-a.d_out_sem);if(g("f_sort")==="din")filtered.sort((a,b)=>a.d_in_char-b.d_in_char);
 shown=50;render();}
function card(d){const orig=PROMPTS[d.prompt_id]||"";const flip=d.anchor_correct!==d.comparison_correct&&d.anchor_correct!==null&&d.comparison_correct!==null;
 const fc=flip?(d.comparison_correct?"good":"bad"):"";
 return `<div class="card"><div class="head"><span class="chip b">${esc(d.prompt_id)}</span><span class="chip">${esc(d.model)}</span>
 <span class="chip">${esc(d.task_category)}</span><span class="chip b">${esc(d.condition==="control"?"control (unchanged prompt) #"+d.repetition:d.operator)}</span>
 <span class="chip">${esc(d.taxonomy)}</span>${d.audit_status==="meaning_altering"?`<span class="chip bad">audit: meaning-altering (${esc(d.audit_kind)})</span>`:""}
 ${flip?`<span class="chip ${fc}">${d.comparison_correct?"incorrect → correct":"correct → incorrect"}</span>`:""}</div>
 <div class="metrics">input change: char ${f3(d.d_in_char)} · semantic ${f3(d.d_in_sem)} &nbsp;|&nbsp; output change: semantic ${f3(d.d_out_sem)} · char ${f3(d.d_out_char)} · token ${f3(d.d_out_token)} · final answer changed: ${d.answer_changed===null?"–":d.answer_changed?"yes":"no"}</div>
 <div class="prompt"><div class="lbl">${d.condition==="control"?"prompt (unchanged)":"prompt edit (red = removed, green = added)"}</div>${d.condition==="control"?esc(orig):wordDiff(orig,d.perturbed_prompt||orig)}</div>
 <div class="cols"><div><div class="lbl">anchor output (original prompt): ${corr(d.anchor_correct)}</div><pre>${esc(d.anchor_output)}</pre></div>
 <div><div class="lbl">${d.condition==="control"?"repeat output (same prompt)":"perturbed-prompt output"}: ${corr(d.comparison_correct)}</div><pre>${esc(d.comparison_output)}</pre></div></div></div>`;}
function render(){$("count").textContent=`${filtered.length} of ${DATA.length} pairs`;
 $("list").innerHTML=filtered.slice(0,shown).map(card).join("");$("more").style.display=shown<filtered.length?"":"none";}
document.querySelectorAll("select,input").forEach(e=>e.addEventListener("input",apply));
$("more").onclick=()=>{shown+=50;render();};apply();
</script></body></html>"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--study-dir", type=Path, default=Path("results/study/main_v1"))
    args = parser.parse_args()
    study = args.study_dir if args.study_dir.is_absolute() else ROOT / args.study_dir
    pairs = pd.read_csv(study / "processed/analysis_pairs.csv", keep_default_na=True)
    pairs = pairs[[c for c in COLUMNS if c in pairs.columns]]
    records = json.loads(pairs.to_json(orient="records"))
    for r in records:
        for k in ("anchor_correct", "comparison_correct"):
            v = r.get(k)
            r[k] = None if v is None else (v if isinstance(v, bool) else str(v).lower() == "true")
    manifest = json.loads((study / "study_manifest.json").read_text(encoding="utf-8"))
    dataset = pd.read_csv(ROOT / manifest["dataset_path"])
    prompts = dict(zip(dataset["prompt_id"], dataset["original_prompt"]))
    html = (HTML.replace("__STUDY__", manifest["study_id"])
            .replace("__DATA__", json.dumps(records, ensure_ascii=False).replace("</", "<\\/"))
            .replace("__PROMPTS__", json.dumps(prompts, ensure_ascii=False).replace("</", "<\\/")))
    out = study / "analysis/output_viewer.html"
    out.write_text(html, encoding="utf-8")
    print(f"Wrote {out} ({out.stat().st_size / 1e6:.1f} MB, {len(records)} pairs)")


if __name__ == "__main__":
    main()
