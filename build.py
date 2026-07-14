#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera as páginas do site Capa a partir de fragmentos de corpo em _bodies/.
Cada página é auto-contida (CSS + logótipo embebidos)."""
import os, re, sys, pathlib

# Por omissao a saida vai para SRC/dist e contem APENAS o site servido (paginas,
# book/, assets, ficheiros de crawler). E o que o Cloudflare (Workers Static
# Assets) publica, sem apanhar .git/, _bodies/, build.py, etc. Manter o root
# limpo e o comportamento pretendido: correr `python build.py` nunca deve
# recriar ficheiros gerados no root nem ressuscitar o CNAME.
#
# --dist e aceite como alias sem efeito do modo por omissao (o comando de build
# do Cloudflare e `python build.py --dist`, tem de continuar a funcionar).
#
# Com --in-place a saida vai para o root (SRC), o velho comportamento: escreve as
# paginas ao lado das entradas de build e emite o CNAME (para o GitHub Pages).
SRC = pathlib.Path(__file__).resolve().parent
IN_PLACE = "--in-place" in sys.argv
# DIST == "estamos a construir para dist/" (o modo por omissao). Toda a logica a
# jusante continua expressa em DIST, so o valor por omissao e que inverteu.
DIST = not IN_PLACE
OUT = SRC if IN_PLACE else (SRC / "dist")
BODIES = SRC / "_bodies"
FONTS = SRC / "fonts"

CSS = r"""
:root{
  --paper:#faf9f5; --paper-2:#f3f1e9; --paper-3:#ece9de; --card:#fff;
  --line:#e6e2d6; --line-2:#d7d2c3;
  --ink:#1c1b17; --ink-2:#56544c; --ink-3:#646257;
  --accent:#6a4bd6; --accent-h:#5a3bc4; --soft:#a885fa; --wash:#f1ecfe; --aline:#ddd0fb; --aink:#4a2f9e;
  --ok:#3f9b6e; --ok-wash:#e7f4ec; --ok-line:#bfe3cd;
  --bad:#cf5b4e; --bad-wash:#fbe9e6; --bad-line:#f1c7c0;
  --code-bg:#1d1830; --code-2:#252038; --code-line:#352c50; --code-fg:#e9e6f5;
  --k:#c4b0ff; --cap:#f2b066; --ty:#86d9c9; --st:#bcd99a; --cm:#7d7799; --fn:#fdfdfe; --pu:#b3acce; --er:#f4978e;
  --serif:'Source Serif 4','Source Serif Pro',Georgia,serif; --sans:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
  --mono:'IBM Plex Mono',ui-monospace,Menlo,monospace;
  --wrap:1140px; --r:16px;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);
  font-size:17px;line-height:1.65;-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility}
a{color:var(--accent);text-decoration:none}
a:hover{color:var(--accent-h);text-decoration:underline;text-underline-offset:3px}
::selection{background:var(--soft);color:#fff}

/* keyboard focus: visible, high-contrast ring on every interactive control */
:focus-visible{outline:3px solid var(--accent);outline-offset:2px;border-radius:4px}
a:focus-visible,.btn:focus-visible,.drop-btn:focus-visible,.nav-toggle:focus-visible,
.drop a:focus-visible,.nav-links a:focus-visible,.card:focus-visible,.nextcard:focus-visible{
  outline:3px solid var(--accent);outline-offset:2px}
.nav .drop-btn:focus-visible,.nav-toggle:focus-visible{outline-offset:3px}

/* skip link: off-screen until focused, then pinned top-left over the nav */
.skip-link{position:absolute;left:8px;top:-60px;z-index:200;background:var(--accent);color:#fff;
  font-family:var(--sans);font-weight:600;font-size:.92rem;padding:.7em 1.1em;border-radius:0 0 10px 10px;
  transition:top .15s}
.skip-link:focus{top:0;color:#fff;text-decoration:none;outline:3px solid var(--ink);outline-offset:2px}
.mark{display:inline-block}
.wrap{max-width:var(--wrap);margin:0 auto;padding:0 26px}
.divider{height:1px;background:var(--line);border:0;margin:0}

h1,h2,h3{font-family:var(--serif);font-weight:500;letter-spacing:-.012em;line-height:1.1;color:var(--ink)}
h1{font-size:clamp(2.6rem,5.5vw,3.9rem);font-weight:500;letter-spacing:-.02em}
h2{font-size:clamp(1.7rem,3vw,2.2rem);margin:0 0 .5em}
h3{font-size:1.25rem;margin:0 0 .4em}
h4{font-family:var(--sans);font-weight:600;font-size:1.05rem;margin:0 0 .4em}
p{margin:0 0 1.1em}
.lead{font-size:1.22rem;color:var(--ink-2);line-height:1.58}
.muted{color:var(--ink-2)}
strong{font-weight:600;color:var(--ink)}
em{font-style:italic}
.eyebrow{font-family:var(--mono);font-size:.73rem;font-weight:500;letter-spacing:.16em;
  text-transform:uppercase;color:var(--accent);display:inline-flex;align-items:center;gap:.6em;margin:0 0 1.2rem}
.eyebrow::before{content:"";width:24px;height:1px;background:var(--aline)}
.ic{font-family:var(--mono);font-size:.85em;background:var(--wash);color:var(--aink);
  padding:.1em .42em;border-radius:6px;border:1px solid var(--aline)}

.btn{display:inline-flex;align-items:center;gap:.5em;font-family:var(--sans);font-size:.96rem;font-weight:500;
  padding:.72em 1.4em;border-radius:999px;border:1px solid transparent;cursor:pointer;line-height:1;
  transition:transform .12s,background .15s,box-shadow .15s,border-color .15s}
.btn:hover{text-decoration:none;transform:translateY(-1px)}
.btn-primary{background:var(--accent);color:#fff;box-shadow:0 1px 2px rgba(74,47,158,.25)}
.btn-primary:hover{background:var(--accent-h);color:#fff;box-shadow:0 8px 22px rgba(106,75,214,.3)}
.btn-ghost{background:transparent;color:var(--ink);border-color:var(--line-2)}
.btn-ghost:hover{color:var(--ink);background:var(--paper-2);border-color:var(--ink-3)}
.btn-soft{background:var(--wash);color:var(--aink);border-color:var(--aline)}
.btn-soft:hover{background:#e7defc;color:var(--aink)}
.btn svg{width:1.05em;height:1.05em}

/* nav */
.nav{position:sticky;top:0;z-index:60;background:rgba(250,249,245,.85);
  backdrop-filter:saturate(160%) blur(12px);border-bottom:1px solid var(--line)}
.nav-inner{max-width:1280px;margin:0 auto;padding:0 26px;height:66px;display:flex;align-items:center;gap:10px}
.brand{display:flex;align-items:center;gap:.4em;font-family:var(--serif);font-size:1.34rem;color:var(--ink);font-weight:600}
.brand:hover{text-decoration:none;color:var(--ink)}
.brand .mark{height:30px;width:22.1px;flex:0 0 auto}
.nav-links{display:flex;align-items:center;gap:1px;margin-left:18px}
.nav-links a,.drop-btn{color:var(--ink-2);font-size:.92rem;font-weight:500;font-family:var(--sans);
  padding:.46em .72em;border-radius:8px;background:none;border:0;cursor:pointer;display:inline-flex;align-items:center;gap:.35em}
.nav-links a:hover,.drop-btn:hover{color:var(--ink);background:var(--paper-2);text-decoration:none}
.nav-links a.active{color:var(--accent);background:var(--wash)}
.has-drop{position:relative}
.drop-btn .car{width:9px;height:9px;opacity:.6;transition:transform .15s}
.has-drop:hover .drop-btn .car{transform:rotate(180deg)}
.drop-btn[aria-expanded="true"] .car{transform:rotate(180deg)}
.drop{position:absolute;top:calc(100% + 4px);left:0;min-width:216px;background:var(--paper);
  border:1px solid var(--line);border-radius:14px;box-shadow:0 18px 44px -18px rgba(40,32,60,.28);
  padding:8px;display:none;flex-direction:column;gap:1px}
.has-drop:hover .drop,.drop-btn[aria-expanded="true"]+.drop{display:flex}
.drop a{color:var(--ink-2);font-size:.91rem;padding:.55em .7em;border-radius:9px}
.drop a:hover{background:var(--paper-2);color:var(--ink);text-decoration:none}
.nav-cta{display:flex;align-items:center;gap:10px;margin-left:auto}
.nav-ico{color:var(--ink-2);display:inline-flex;padding:.4em;border-radius:8px}
.nav-ico:hover{color:var(--ink);background:var(--paper-2)}
.nav-toggle{display:none;background:none;border:1px solid var(--line-2);border-radius:9px;width:42px;height:42px;cursor:pointer;align-items:center;justify-content:center}
.nav-toggle span,.nav-toggle span::before,.nav-toggle span::after{content:"";display:block;width:18px;height:2px;background:var(--ink);position:relative}
.nav-toggle span::before{position:absolute;top:-6px}.nav-toggle span::after{position:absolute;top:6px}

/* hero / page hero */
.phero{padding:74px 0 8px;position:relative;overflow:hidden}
.phero-glow{position:absolute;inset:0;pointer-events:none;background:radial-gradient(640px 360px at 85% 0%,rgba(168,133,250,.16),transparent 70%)}
.phero .wrap{position:relative;max-width:900px}
.phero .lead{max-width:66ch;margin-top:.4em}
.phero-actions{display:flex;flex-wrap:wrap;gap:12px;margin-top:24px}

section{padding:60px 0}
.band{background:var(--paper-2);border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
.article{max-width:900px;margin:0 auto;padding:0 26px}
.article-narrow{max-width:820px;margin:0 auto;padding:0 26px}
.section-intro{max-width:72ch;margin-bottom:26px}
.article h2{margin:0 0 .5em}
.article h2.mt{margin-top:2em}
.article h3{margin-top:1.5em}

/* code */
.code{background:var(--code-bg);border:1px solid var(--code-line);border-radius:var(--r);overflow:hidden;
  box-shadow:0 20px 54px -28px rgba(29,24,48,.55);margin:18px 0}
.code-head{display:flex;align-items:center;gap:7px;padding:11px 16px;background:var(--code-2);border-bottom:1px solid var(--code-line)}
.code-head .o{width:11px;height:11px;border-radius:50%;background:#3b3357}
.code-head .t{margin-left:8px;font-family:var(--mono);font-size:.75rem;color:#8a83a8}
.code pre{margin:0;padding:20px;overflow-x:auto;font-family:var(--mono);font-size:.85rem;line-height:1.72;color:var(--code-fg)}
.k{color:var(--k)}.cp{color:var(--cap);font-weight:500}.ty{color:var(--ty)}.st{color:var(--st)}
.cm{color:var(--cm);font-style:italic}.fn{color:var(--fn)}.pu{color:var(--pu)}.nu{color:var(--cap)}.er{color:var(--er)}

/* pull / note / callout */
.pull{border-left:3px solid var(--soft);background:var(--wash);border-radius:0 14px 14px 0;
  padding:20px 26px;margin:26px 0;font-family:var(--serif);font-size:1.24rem;line-height:1.45;color:var(--aink)}
.note{background:var(--card);border:1px solid var(--line);border-left:3px solid var(--soft);
  border-radius:0 14px 14px 0;padding:18px 22px;margin:22px 0;color:var(--ink-2);font-size:.97rem}
.note strong{color:var(--ink)}
.callout{background:var(--wash);border:1px solid var(--aline);border-radius:var(--r);padding:22px 24px;color:var(--aink);margin:20px 0}
.callout p:last-child{margin-bottom:0}

/* lists */
.bullets{list-style:none;padding:0;margin:18px 0;display:grid;gap:14px}
.bullets li{padding-left:30px;position:relative;color:var(--ink-2)}
.bullets li::before{content:"";position:absolute;left:6px;top:.62em;width:8px;height:8px;border-radius:50%;background:var(--soft);box-shadow:0 0 0 4px var(--wash)}
.bullets li strong{color:var(--ink)}
.emitters{list-style:none;padding:0;margin:18px 0;display:grid;gap:10px}
.emitters li{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 18px;color:var(--ink-2);font-size:.96rem}
.linklist{list-style:none;padding:0;margin:18px 0;display:grid;gap:2px;max-width:82ch}
.linklist li{padding:14px 0;border-top:1px solid var(--line)}
.linklist li:first-child{border-top:0}
.linklist a{font-weight:600}
.linklist .desc{color:var(--ink-2);font-weight:400}

/* cards / grid */
.grid{display:grid;gap:18px}
.g2{grid-template-columns:1fr 1fr}
.g3{grid-template-columns:repeat(3,1fr)}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:26px;position:relative;
  transition:transform .15s,box-shadow .15s,border-color .15s}
a.card:hover,.card:has(.card-cover):hover{transform:translateY(-3px);border-color:var(--aline);box-shadow:0 18px 44px -24px rgba(74,47,158,.4);text-decoration:none}
.card-cover{position:absolute;inset:0;border-radius:inherit;z-index:1}
.card a:not(.card-cover){position:relative;z-index:2}
.card h3{font-size:1.18rem}
.card p{color:var(--ink-2);font-size:.96rem;margin:0}

/* comparison rows */
.cmp{border:1px solid var(--line);border-radius:var(--r);overflow:hidden;background:var(--card);margin:8px 0}
.cmp-row{display:grid;grid-template-columns:230px 1fr;gap:28px;padding:20px 24px;border-top:1px solid var(--line);align-items:start}
.cmp-row:first-child{border-top:0}
.cmp-term{font-weight:600;color:var(--ink);font-size:.98rem}
.cmp-term .sub{display:block;font-weight:400;color:var(--ink-3);font-family:var(--mono);font-size:.78rem;margin-top:4px}
.cmp-term .tag{display:inline-block;font-family:var(--mono);font-size:.72rem;color:var(--aink);background:var(--wash);border:1px solid var(--aline);border-radius:6px;padding:.1em .45em;margin-right:.5em}
.cmp-desc{color:var(--ink-2);font-size:.95rem;margin:0}
.cmp-row.is-capa{background:var(--wash);box-shadow:inset 3px 0 0 var(--accent)}
.cmp-row.is-capa .cmp-desc{color:#3b2a73}

/* next cards */
.nextgrid{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:8px 0}
.nextcard{display:block;background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:20px 22px;transition:transform .15s,box-shadow .15s,border-color .15s}
.nextcard:hover{transform:translateY(-3px);border-color:var(--aline);box-shadow:0 18px 44px -24px rgba(74,47,158,.4);text-decoration:none}
.nextcard h4{display:flex;align-items:center;gap:.4em;color:var(--aink)}
.nextcard h4 .arr{transition:transform .15s}
.nextcard:hover h4 .arr{transform:translateX(3px)}
.nextcard p{margin:6px 0 0;color:var(--ink-2);font-size:.93rem}

/* steps */
.steps{margin-top:14px}
.step{display:grid;grid-template-columns:64px 1fr;gap:24px;padding:26px 0;border-top:1px solid var(--line);align-items:start}
.step:first-child{border-top:0}
.step-n{font-family:var(--serif);font-size:2rem;color:var(--soft);font-weight:500;line-height:1}
.step-b h3{margin-bottom:.3em;font-size:1.2rem}
.step-b p{color:var(--ink-2);margin:0}

/* chips */
.chips{display:flex;flex-wrap:wrap;gap:9px;margin:8px 0}
.chip{font-family:var(--mono);font-size:.83rem;font-weight:500;color:var(--aink);background:var(--card);
  border:1px solid var(--aline);border-radius:9px;padding:.34em .7em}

/* ctaband */
.ctaband{background:var(--paper-2);border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:60px 0;text-align:center}
.ctaband h2{margin-bottom:.3em}
.ctaband .row{display:flex;gap:12px;justify-content:center;flex-wrap:wrap;margin-top:18px}

/* tables (generic) */
.tbl{width:100%;border-collapse:collapse;font-size:.95rem;margin:10px 0;background:var(--card);border:1px solid var(--line);border-radius:var(--r);overflow:hidden}
.tbl th,.tbl td{text-align:left;padding:13px 16px;border-bottom:1px solid var(--line)}
.tbl th{font-family:var(--mono);font-size:.74rem;text-transform:uppercase;letter-spacing:.07em;color:var(--ink-3);font-weight:500;background:var(--paper-2)}
.tbl tr:last-child td{border-bottom:0}
.tbl td .ic{white-space:nowrap}

/* level pills (regulatory mapping) */
.lv{font-family:var(--mono);font-size:.72rem;font-weight:600;padding:.18em .5em;border-radius:6px;display:inline-block;white-space:nowrap}
.lv-d{color:var(--ok);background:var(--ok-wash);border:1px solid var(--ok-line)}
.lv-i{color:#a9772a;background:#fbf2df;border:1px solid #ecdab0}
.lv-p{color:var(--ink-3);background:var(--paper-2);border:1px solid var(--line)}
.lv-n{color:var(--ink-3);font-family:var(--mono);font-size:.72rem}
.tbl td .cl{display:block;font-family:var(--mono);font-size:.72rem;color:var(--ink-3);margin-bottom:3px}
.tbl.matrixtbl td,.tbl.matrixtbl th{text-align:center}
.tbl.matrixtbl td:first-child,.tbl.matrixtbl th:first-child{text-align:left}

/* docs layout (reference) */
.docs{display:grid;grid-template-columns:230px 1fr;gap:46px;max-width:1180px;margin:0 auto;padding:0 26px;align-items:start}
.toc{position:sticky;top:84px;align-self:start}
.toc h6{font-family:var(--mono);font-size:.7rem;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-3);margin:0 0 12px;font-weight:500}
.toc ol{list-style:none;margin:0;padding:0;counter-reset:t;display:grid;gap:1px}
.toc li{counter-increment:t}
.toc a{display:block;color:var(--ink-2);font-size:.88rem;padding:.34em .6em;border-radius:8px;border-left:2px solid transparent}
.toc a::before{content:counter(t) ". ";color:var(--ink-3);font-family:var(--mono);font-size:.78rem}
.toc a:hover{background:var(--paper-2);color:var(--ink);text-decoration:none;border-left-color:var(--aline)}
.docbody{min-width:0}
.docbody h2{font-size:1.6rem;margin:0 0 .5em;scroll-margin-top:84px;padding-top:8px}
.docbody h2:not(:first-child){margin-top:2.2em;padding-top:24px;border-top:1px solid var(--line)}
.docbody h3{font-size:1.1rem;margin:1.5em 0 .4em;color:var(--ink);scroll-margin-top:84px}
.docbody h2 .nx{font-family:var(--mono);font-size:.9rem;color:var(--accent);margin-right:.5em}
@media(max-width:900px){
  .docs{grid-template-columns:1fr;gap:24px}
  .toc{position:static}
  .toc ol{grid-template-columns:1fr 1fr;gap:2px 16px}
}

/* footer */
.footer{background:var(--paper-2);border-top:1px solid var(--line);padding:60px 0 38px}
.footer-grid{display:grid;grid-template-columns:1.5fr repeat(4,1fr);gap:36px;max-width:var(--wrap);margin:0 auto;padding:0 26px}
.footer-brand .brand{margin-bottom:13px;justify-content:flex-start}
.footer-brand .brand .mark{height:26px;width:19.2px;flex:0 0 auto}
.footer-brand p{color:var(--ink-2);font-size:.92rem;max-width:32ch}
.footer h5{font-family:var(--mono);font-size:.73rem;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-3);margin:0 0 14px;font-weight:500}
.footer ul{list-style:none;padding:0;margin:0;display:grid;gap:9px}
.footer ul a{color:var(--ink-2);font-size:.92rem}
.footer ul a:hover{color:var(--accent)}
.footer-base{max-width:var(--wrap);margin:42px auto 0;padding:22px 26px 0;border-top:1px solid var(--line);display:flex;justify-content:space-between;flex-wrap:wrap;gap:10px;font-family:var(--mono);font-size:.78rem;color:var(--ink-3)}

@media(max-width:980px){
  .g3{grid-template-columns:1fr}
  .nextgrid,.depth{grid-template-columns:1fr}
  .footer-grid{grid-template-columns:1fr 1fr;gap:30px}
  .footer-brand{grid-column:1/-1}
  .nav-links{display:none;position:absolute;top:66px;left:0;right:0;flex-direction:column;align-items:stretch;background:var(--paper);border-bottom:1px solid var(--line);padding:12px 18px 18px;margin:0;gap:2px}
  .nav-links.open{display:flex}
  .nav-links a,.drop-btn{padding:.7em .6em;width:100%;justify-content:flex-start}
  .has-drop{width:100%}
  .drop{position:static;display:flex;border:0;box-shadow:none;padding:0 0 6px 14px;min-width:0}
  .has-drop .drop-btn .car{display:none}
  .nav-toggle{display:flex}
}
@media(max-width:860px){
  .cmp-row{grid-template-columns:1fr;gap:8px}
  .g2{grid-template-columns:1fr}
  .step{grid-template-columns:1fr;gap:8px}
}
@media(prefers-reduced-motion:reduce){*{transition:none!important;scroll-behavior:auto!important}}

/* helpers replacing former inline styles (kept CSP-clean: no inline style attrs) */
.svg-defs{position:absolute}
.mark-26{height:26px}
"""

SYMBOL = r"""<svg width="0" height="0" class="svg-defs" aria-hidden="true">
 <symbol id="capa-mark" viewBox="0 0 577.22 782.7">
  <path fill="#a885fa" d="M515.82,258.55c1.6,9.06-14.34-4.03-22.58-5.07-128.33-58.01-269.07,69.8-197.88,196.88,54.82,97.82,196.29,106.26,275.81,34.39,7.59-3.13,6.02,11.39,5.7,16.08,3.09,87.71-138.58,190.41-66.46,248.48,2.83,2.37,15.3,9.63,16,11.02,3.47,6.87-14.56,10.48-19.31,11.72-233.4,62-442.98-157.08-369.29-387.95-47,68.7-43.12,183.85-3.79,263.59.91,1.87,6.52,11.33,9.7,17.43.74,1.42-.95,2.87-2.23,1.91-20.32-15.17-40.98-28.25-64.64-38.16-21.07-8.82-65.58-18.79-76.15-39.85-11.95-141.41,132.91-331.75,245.19-408.17,27.89-10.82,56.49.72,81.86,13.37,9.26-.26-16.46-16.32-18.85-17.4-42.73-25.62-91.55,3.89-75.56-28.52,3.84-7.75,13.77-16.2,22-19,10.08-3.44,28.13-.72,16.54-16.46-5.41-7.34-16.48-14.32-24.64-18.36-6.77-3.35-33.51-10.83-32.19-19.41,61.39-110.77,222.44-79.82,314.35-28.77,26.38,17.14-27.13,108.94-38.71,131.34-46.28,52.42-2.25,17.23,25.13,80.91ZM530.68,69.52c.89,1.01,2.6.26,2.61-1.08.07-14.22-18.12-14.02-29.89-13.09-37.48,2.97-62.22,29.45-84.49,56.51-28.27,33.92-75.86,88.32-2.74,100.66,1.67.24,2.41-2.03.92-2.83l-8.44-4.52c-14.22-9.07-21.16-18.6-12.57-35.14,25.37-41.11,80.49-112.17,134.61-100.51Z"/>
  <path fill="#fdfdfe" d="M533.29,68.44c0,1.34-1.72,2.08-2.61,1.08-.07-.08-.15-.16-.24-.24-10.04-8.31-43.94,6.95-54.23,12.88-25.39,14.64-66.61,61.78-80.14,87.86-8.56,16.51-1.72,25.98,12.45,35.08.04.02.07.05.11.07l8.44,4.52c1.49.8.75,3.08-.92,2.83-19.72-2.89-41.34-12.65-39.32-35.73,1.36-15.52,31.22-51.76,42.07-64.93,22.27-27.06,47.01-53.54,84.49-56.51,11.77-.93,29.97-1.13,29.89,13.09Z"/>
 </symbol>
</svg>"""

GH = ('<svg width="20" height="20" viewBox="0 0 16 16" fill="currentColor"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>')

NAV_ITEMS = [("why","Why Capa","why.html"),("compare","Compare","compare.html"),
             ("learn","Learn","learn/index.html"),("reference","Reference","reference.html")]
DROP_ITEMS = [("study","Study","study.html"),("migrating","Migrating","migrating.html"),
              ("regulatory","Regulatory","regulatory.html"),("agent","Agent demo","agent-demo.html"),
              ("stdlib","Standard library","stdlib.html"),("packages","Packages","packages.html"),
              ("community","Community","community.html"),
              ("book","The book","book/Capa-The-Capability-Typed-Programming-Language.pdf")]

def nav(active, P):
    links=""
    for key,label,href in NAV_ITEMS:
        cls=' class="active"' if key==active else ''
        links+=f'<a href="{P}{href}"{cls}>{label}</a>\n      '
    drop=""
    for key,label,href in DROP_ITEMS:
        drop+=f'<a href="{P}{href}">{label}</a>'
    roadcls=' class="active"' if active=="roadmap" else ''
    return f'''<header class="nav">
  <div class="nav-inner">
    <a class="brand" href="{P}index.html"><svg class="mark"><use href="#capa-mark"/></svg>Capa</a>
    <nav class="nav-links" id="navlinks">
      {links}<div class="has-drop">
        <button class="drop-btn" id="docsbtn" aria-haspopup="true" aria-expanded="false">Docs
          <svg class="car" viewBox="0 0 10 6" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M1 1l4 4 4-4"/></svg>
        </button>
        <div class="drop">{drop}</div>
      </div>
      <a href="{P}roadmap.html"{roadcls}>Roadmap</a>
    </nav>
    <div class="nav-cta">
      <a class="nav-ico" href="https://github.com/nelsonduarte/capa-language" aria-label="GitHub">{GH}</a>
      <a class="btn btn-primary" href="{P}start.html">Get started</a>
      <button class="nav-toggle" id="navtoggle" aria-label="Menu"><span></span></button>
    </div>
  </div>
</header>'''

def footer(P):
    return f'''<footer class="footer">
  <div class="footer-grid">
    <div class="footer-brand">
      <a class="brand" href="{P}index.html"><svg class="mark mark-26"><use href="#capa-mark"/></svg>Capa</a>
      <p>A capability-typed programming language. Every function declares the authorities it holds; the compiler checks the discipline statically.</p>
    </div>
    <div><h5>Pages</h5><ul>
      <li><a href="{P}index.html">Home</a></li><li><a href="{P}why.html">Why Capa</a></li>
      <li><a href="{P}learn/index.html">Learn</a></li><li><a href="{P}roadmap.html">Roadmap</a></li>
    </ul></div>
    <div><h5>Documentation</h5><ul>
      <li><a href="{P}start.html">Getting started</a></li><li><a href="{P}reference.html">Reference</a></li>
      <li><a href="{P}stdlib.html">Standard library</a></li><li><a href="{P}packages.html">Packages</a></li>
      <li><a href="{P}migrating.html">Migrating</a></li>
    </ul></div>
    <div><h5>Specification</h5><ul>
      <li><a href="https://github.com/nelsonduarte/capa-language/blob/main/docs/positioning.md">Positioning</a></li>
      <li><a href="https://github.com/nelsonduarte/capa-language/blob/main/Capa-EBNF.md">EBNF grammar</a></li>
      <li><a href="https://github.com/nelsonduarte/capa-language/blob/main/docs/semantics.md">&#955;cap &amp; soundness</a></li>
      <li><a href="{P}regulatory.html">CRA / NIS2 / DORA</a></li>
    </ul></div>
    <div><h5>Project</h5><ul>
      <li><a href="https://github.com/nelsonduarte/capa-language">Source</a></li>
      <li><a href="{P}community.html">Community</a></li><li><a href="{P}brand.html">Brand assets</a></li>
      <li><a href="{P}privacy.html">Privacy</a></li>
    </ul></div>
  </div>
  <div class="footer-base">
    <span>Built by Nelson Duarte &middot; v1.15.1 &middot; MIT or Apache-2.0</span>
    <span>&copy; 2026 Capa</span>
  </div>
</footer>'''

# Mobile menu toggle + accessible Docs dropdown. Lives in an external file
# (menu.js) so the strict CSP can use script-src 'self' with no inline scripts
# and no 'unsafe-inline'. The dropdown opens on click (works for touch) with
# aria-expanded reflected, closes on Escape and on outside click; CSS still
# provides hover-open on the desktop.
MENU_JS = (
    "var t=document.getElementById('navtoggle'),"
    "l=document.getElementById('navlinks');"
    "if(t)t.addEventListener('click',function(){l.classList.toggle('open')});"
    "var d=document.getElementById('docsbtn');"
    "if(d){"
    "var close=function(){d.setAttribute('aria-expanded','false');};"
    "d.addEventListener('click',function(e){"
    "e.preventDefault();"
    "var open=d.getAttribute('aria-expanded')==='true';"
    "d.setAttribute('aria-expanded',open?'false':'true');"
    "});"
    "document.addEventListener('keydown',function(e){"
    "if(e.key==='Escape'){close();d.focus();}"
    "});"
    "document.addEventListener('click',function(e){"
    "if(!d.parentNode.contains(e.target))close();"
    "});"
    "}\n")

# Strict Content-Security-Policy, matching the production site's posture:
# everything first-party, no inline script/style, no third parties.
CSP = ("default-src 'self'; img-src 'self' data:; style-src 'self'; "
       "script-src 'self'; font-src 'self'; object-src 'none'; "
       "base-uri 'self'; form-action 'self'; frame-ancestors 'none'; "
       "upgrade-insecure-requests")

# Production domain (parity with repos/capa-language-website). Used for absolute
# URLs in canonical/OG/Twitter meta, the sitemap, robots.txt and CNAME.
DOMAIN = "capa-language.com"
SITE = "https://" + DOMAIN

# --- inline-style extraction (CSP: style-src 'self', no 'unsafe-inline') -------
# The body fragments use one-off inline style="" attributes. Browsers block those
# under a strict style-src with no 'unsafe-inline'. We extract each distinct
# inline style at build time into a generated class (.u<n>) and rewrite the
# attribute to reference it, so the rendered output is visually identical but
# carries zero inline styles. New fragments are handled automatically.
_STYLE_CLASSES = {}            # normalised decls -> class name
_STYLE_RE = re.compile(r'\sstyle="([^"]*)"')

def _norm(decls):
    parts=[p.strip() for p in decls.split(";") if p.strip()]
    return ";".join(parts)

def extract_inline_styles(body):
    """Replace every style="..." in `body` with a class reference, registering
    the declarations in _STYLE_CLASSES for later emission into styles.css."""
    def repl(m):
        decls=_norm(m.group(1))
        if not decls:
            return ""
        cls=_STYLE_CLASSES.get(decls)
        if cls is None:
            cls=f"u{len(_STYLE_CLASSES)}"
            _STYLE_CLASSES[decls]=cls
        # fold the new class into an existing class="" on the same tag if present,
        # otherwise the caller's second pass adds class="". Here we just emit a
        # marker the post-pass merges.
        return f' \x00{cls}\x00'
    return _STYLE_RE.sub(repl, body)

def merge_style_classes(body):
    """Fold the \x00cls\x00 markers left by extract_inline_styles into class="".
    A marker adjacent to an existing class="..." joins it; otherwise it becomes a
    new class attribute."""
    # case 1: tag already has class="..."; append our class inside it.
    def into_existing(m):
        return f'{m.group(1)}{m.group(2)} {m.group(3)}{m.group(4)}'
    # markers look like:  \x00clsname\x00
    # First, attach a marker that sits before/after an existing class attr on the
    # same element by a simple tag-level rewrite.
    # Strategy: walk each tag, collect markers within it, and emit one class attr.
    out=[]
    i=0
    tag_re=re.compile(r'<[a-zA-Z][^>]*>')
    pos=0
    result=[]
    for tm in tag_re.finditer(body):
        result.append(body[pos:tm.start()])
        tag=tm.group(0)
        markers=re.findall('\x00([^\x00]+)\x00', tag)
        if markers:
            tag=re.sub('\\s*\x00[^\x00]+\x00','',tag)
            classes=" ".join(markers)
            cm=re.search(r'class="([^"]*)"', tag)
            if cm:
                tag=tag[:cm.start(1)]+ (cm.group(1)+" "+classes).strip() + tag[cm.end(1):]
            else:
                # insert class="" right after the tag name
                tag=re.sub(r'^(<[a-zA-Z][a-zA-Z0-9]*)', r'\1 class="'+classes+'"', tag, count=1)
        result.append(tag)
        pos=tm.end()
    result.append(body[pos:])
    return "".join(result)

def style_classes_css():
    lines=["/* generated: former inline style=\"\" attributes, one class each */"]
    for decls,cls in _STYLE_CLASSES.items():
        lines.append(f".{cls}{{{decls}}}")
    return "\n".join(lines)+"\n"

def page(filename, title, desc, active, body, depth=0):
    P = "../"*depth
    canonical = SITE + "/" + filename
    og_image = SITE + "/capa_logo.svg"
    html=f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="Content-Security-Policy" content="{CSP}">
<meta name="referrer" content="strict-origin-when-cross-origin">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Capa">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og_image}">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{og_image}">
<link rel="icon" href="{P}capa_logo.svg" type="image/svg+xml">
<link rel="stylesheet" href="{P}styles.css">
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
{SYMBOL}
{nav(active,P)}
<main id="main">
{body}
</main>
{footer(P)}
<script src="{P}menu.js"></script>
</body>
</html>'''
    out=OUT/filename
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(html,encoding="utf-8")
    return len(html)

# Configuração das páginas: (ficheiro, título, descrição, chave-ativa, fragmento, profundidade)
PAGES=[
 ("index.html","Capa | a capability-typed programming language","Capa is a programming language where every function declares the authorities it holds. The compiler checks the discipline statically. Pythonic syntax.","home","index.html",0),
 ("why.html","Why Capa? | the case for capability-based security","The case for Capa: ambient authority, the event-stream supply-chain attack, capability discipline as a language-level answer.","why","why.html",0),
 ("compare.html","How Capa compares | Capa","Where Capa sits among capability-typed languages (Pony, Koka, Roc, the Wasm Component Model, Zero) and among the existing sources of capability claims.","compare","compare.html",0),
 ("study.html","The capability-recall study | Capa","Capa measured head-to-head against a dependency SBOM, Semgrep, and CodeQL on 25 Python / Capa pairs. 0 false-clearances against CodeQL's 10.","study","study.html",0),
 ("learn/index.html","Learn Capa | Capa","A guided tour of Capa in 14 chapters, from hello world to the audit artefacts.","learn","learn_index.html",1),
 ("learn/01-hello.html","1. Hello, Capa | Learn Capa","Chapter 1 of Learn Capa: write your first program and understand the shape of main.","learn","learn_01_hello.html",1),
 ("learn/02-values.html","2. Values and types | Learn Capa","Chapter 2 of Learn Capa: primitives, let vs var, type inference and string interpolation.","learn","learn_02_values.html",1),
 ("learn/03-functions.html","3. Functions | Learn Capa","Chapter 3 of Learn Capa: signatures, parameters, return types and named arguments.","learn","learn_03_functions.html",1),
 ("learn/04-control-flow.html","4. Control flow | Learn Capa","Chapter 4 of Learn Capa: if, while, for, ranges, and statement versus expression.","learn","learn_04_control_flow.html",1),
 ("learn/05-collections.html","5. Collections | Learn Capa","Chapter 5 of Learn Capa: List, Map, Set and their higher-order methods.","learn","learn_05_collections.html",1),
 ("learn/06-structs-and-sum-types.html","6. Structs and sum types | Learn Capa","Chapter 6 of Learn Capa: defining your own types and pattern matching on variants.","learn","learn_06_structs.html",1),
 ("learn/07-errors-as-values.html","7. Errors as values | Learn Capa","Chapter 7 of Learn Capa: Option, Result and the ? operator.","learn","learn_07_errors.html",1),
 ("learn/08-your-first-capability.html","8. Your first capability | Learn Capa","Chapter 8 of Learn Capa: what Stdio really is, why main declares it, and the capability discipline.","learn","learn_08_first_capability.html",1),
 ("learn/09-attenuating-capabilities.html","9. Attenuating capabilities | Learn Capa","Chapter 9 of Learn Capa: restrict_to, monotonic narrowing and least-authority programs.","learn","learn_09_attenuating.html",1),
 ("learn/10-defining-your-own-capability.html","10. Defining your own capability | Learn Capa","Chapter 10 of Learn Capa: capability X, impl X for Y, and library contracts.","learn","learn_10_defining.html",1),
 ("learn/11-modules-and-visibility.html","11. Modules and visibility | Learn Capa","Chapter 11 of Learn Capa: import, pub and CAPA_PATH.","learn","learn_11_modules.html",1),
 ("learn/12-a-small-project.html","12. A small project | Learn Capa","Chapter 12 of Learn Capa: putting it together in a real CLI tool.","learn","learn_12_project.html",1),
 ("learn/13-information-flow.html","13. Information-flow control | Learn Capa","Chapter 13 of Learn Capa: @secret, declassify, and proving data cannot leak.","learn","learn_13_information_flow.html",1),
 ("learn/14-from-source-to-sbom.html","14. From source to SBOM | Learn Capa","Chapter 14 of Learn Capa: generate the capability manifest, CycloneDX and SPDX SBOMs, VEX and SLSA provenance.","learn","learn_14_sbom.html",1),
 ("reference.html","Language reference | Capa","Full syntax and semantics of Capa: types, capabilities, information-flow control, and the CLI.","reference","reference.html",0),
 ("start.html","Get started | Capa","Install Capa on Linux, macOS or Windows and run your first program.","start","start.html",0),
 ("migrating.html","Migrating to Capa | Capa","How Python and Rust concepts map onto Capa.","migrating","migrating.html",0),
 ("regulatory.html","Regulatory mapping | Capa","How Capa's artefacts map onto CRA, NIS2, DORA, NIST SSDF and OWASP SCVS.","regulatory","regulatory.html",0),
 ("agent-demo.html","Agent demo | Capa","A worked example where the per-function capability bound is the security argument for an LLM agent.","agent","agent_demo.html",0),
 ("roadmap.html","Roadmap | Capa","What is done, what is next, and what is explicitly out of scope for Capa.","roadmap","roadmap.html",0),
 ("stdlib.html","Standard library | Capa","The Capa standard library: modules, capabilities and core types.","stdlib","stdlib.html",0),
 ("packages.html","Packages | Capa","The Capa package registry: curated, first-party libraries installed by name with capa add over a GPG-signed index.","packages","packages.html",0),
 ("community.html","Community | Capa","How to get involved with Capa.","community","community.html",0),
 ("brand.html","Brand assets | Capa","The Capa logo, colours and usage guidelines.","brand","brand.html",0),
 ("privacy.html","Privacy | Capa","The Capa website privacy policy.","privacy","privacy.html",0),
]

def copy_static():
    """Copy first-party static assets into OUT (logo, menu.js, fonts).

    When OUT == SRC (building in-place into the repo root) the logo and fonts
    already live at their destination, so we skip self-copies that the OS would
    reject; only the generated menu.js is (re)written."""
    import shutil
    OUT.mkdir(parents=True, exist_ok=True)
    def _copy(src, dst):
        if src.resolve() != dst.resolve():
            shutil.copy2(src, dst)
    # logo
    _copy(SRC/"capa_logo.svg", OUT/"capa_logo.svg")
    # external menu script
    (OUT/"menu.js").write_text(MENU_JS, encoding="utf-8")
    # self-hosted fonts (woff2 + licenses + provenance)
    dst=OUT/"fonts"; dst.mkdir(exist_ok=True)
    for f in sorted(FONTS.iterdir()):
        if f.is_file() and f.name != "fonts.css":
            _copy(f, dst/f.name)
    # book PDF: linked from the nav of every page. In-place ja vive em book/,
    # por isso o guard salta o self-copy; em --dist copia o diretorio todo.
    if (SRC/"book").resolve() != (OUT/"book").resolve():
        shutil.copytree(SRC/"book", OUT/"book", dirs_exist_ok=True)
    return sorted(p.name for p in dst.glob("*.woff2"))

def emit_deploy():
    """Emit deploy parity files: CNAME, sitemap.xml, robots.txt, _headers.

    Em --dist o CNAME e omitido: e so-GitHub-Pages; no Cloudflare o dominio
    personalizado e configurado no dashboard, nao por um ficheiro CNAME."""
    OUT.mkdir(parents=True, exist_ok=True)
    # custom domain for GitHub Pages (nao emitido em --dist / Cloudflare)
    if not DIST:
        (OUT/"CNAME").write_text(DOMAIN + "\n", encoding="utf-8")
    # sitemap with absolute URLs for every built page
    urls="".join(
        f"  <url><loc>{SITE}/{fn}</loc></url>\n" for fn,*_ in PAGES)
    sitemap=('<?xml version="1.0" encoding="UTF-8"?>\n'
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
             f"{urls}</urlset>\n")
    (OUT/"sitemap.xml").write_text(sitemap, encoding="utf-8")
    # robots pointing at the sitemap
    (OUT/"robots.txt").write_text(
        "User-agent: *\nAllow: /\nSitemap: " + SITE + "/sitemap.xml\n",
        encoding="utf-8")
    # Cloudflare Pages _headers: serve the CSP as a real HTTP response header
    # (stronger than the meta tag, which stays as a fallback). Reuse the single
    # CSP constant so the header never drifts from the meta-tag value.
    headers=("/*\n"
             f"  Content-Security-Policy: {CSP}\n"
             "  X-Content-Type-Options: nosniff\n"
             "  Referrer-Policy: strict-origin-when-cross-origin\n"
             "  Permissions-Policy: geolocation=(), microphone=(), camera=()\n")
    (OUT/"_headers").write_text(headers, encoding="utf-8")

if __name__=="__main__":
    # 0) modo por omissao: recria dist/ do zero para nunca deixar ficheiros
    #    obsoletos. Com --in-place escrevemos no root e nao ha nada a recriar.
    if DIST:
        import shutil
        if OUT.exists():
            shutil.rmtree(OUT)
        OUT.mkdir(parents=True, exist_ok=True)
        print(f"  saida para {OUT.name}/ recriado (site servido isolado)")

    # 0) bodies first: load + strip inline styles so the generated classes exist
    #    before we write styles.css.
    prepared=[]
    for fn,title,desc,active,frag,depth in PAGES:
        fp=BODIES/frag
        if not fp.exists():
            print(f"  (falta corpo) {frag} -> ignorado")
            continue
        body=fp.read_text(encoding="utf-8")
        body=merge_style_classes(extract_inline_styles(body))
        prepared.append((fn,title,desc,active,body,depth))

    # 1) static assets (logo, menu.js, fonts) + deploy parity files
    woff=copy_static()
    print(f"  copiados {len(woff)} ficheiros de fonte + menu.js + logo")
    emit_deploy()
    print("  emitidos " + ("sitemap.xml, robots.txt, _headers (sem CNAME)"
                           if DIST else "CNAME, sitemap.xml, robots.txt, _headers"))

    # 2) stylesheet: self-hosted @font-face, base CSS, page additions, then the
    #    classes generated from former inline styles.
    fonts_css = (FONTS/"fonts.css").read_text(encoding="utf-8")
    add_path = SRC/"_additions.css"
    additions = add_path.read_text(encoding="utf-8") if add_path.exists() else ""
    (OUT/"styles.css").write_text(
        fonts_css + "\n" + CSS + "\n\n/* ====================================================\n"
        "   Adições específicas de páginas (index, why, compare, study)\n"
        "   ==================================================== */\n" + additions +
        "\n\n/* ====================================================\n"
        "   Classes geradas (ex-inline styles, CSP-safe)\n"
        "   ==================================================== */\n" + style_classes_css(),
        encoding="utf-8")
    print(f"  escrito styles.css ({len(_STYLE_CLASSES)} classes ex-inline)")

    # 3) gera as páginas
    built=0
    for fn,title,desc,active,body,depth in prepared:
        n=page(fn,title,desc,active,body,depth)
        print(f"  build {fn:26} {n:6} bytes")
        built+=1
    print(f"feito: {built} páginas")
