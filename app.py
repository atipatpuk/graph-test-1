#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Graph Theory Lab (Logistics & Urban Planning)
อัลกอริทึม: Dijkstra, Prim, Graph Coloring (Welsh-Powell), Network Flow (Edmonds-Karp)

วิธีรัน:  python app.py
- ติดตั้งครั้งแรก: python -m pip install -r requirements.txt
- เปิดเบราว์เซอร์อัตโนมัติที่ http://localhost:8765
- มือถือ/แท็บเล็ตใน Wi-Fi เดียวกัน: เปิด URL แบบ LAN ที่แสดงใน Terminal
- จะสร้างไฟล์ graph_lab.html ไว้ข้าง ๆ (การรันอัลกอริทึมต้องเปิดผ่านเซิร์ฟเวอร์นี้)
- ใช้ภาพตกแต่ง city_header.png ซึ่งต้องอยู่โฟลเดอร์เดียวกัน
กด Ctrl+C เพื่อปิด
"""
import http.server
import json
import socket
import sys
import threading
import webbrowser
from pathlib import Path

from graph_algorithms import run_algorithm

HTML = r"""<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="theme-color" content="#1a1c2c">
<link rel="manifest" href="/manifest.webmanifest">
<title>Graph Theory Lab</title>
<link rel="icon" type="image/png" href="web.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Pixelify+Sans:wght@400;700&family=Mitr:wght@400;500&display=swap" rel="stylesheet">
<style>
:root{
  --ink:#1a1c2c; --paper:#f4efe1; --navy:#333c57; --yellow:#ffcd75; --green:#a7f070; --dgreen:#38b764;
  --blue:#41a6f6; --dblue:#3b5dc9; --orange:#ef7d57; --red:#b13e53; --purple:#5d275d; --gray:#94b0c2; --cyan:#73eff7;
  --font:'Mitr','Tahoma',sans-serif;
}
*{box-sizing:border-box}
html,body{margin:0;height:100%;overflow:hidden;background:var(--navy);font-family:var(--font);color:var(--ink);
  -webkit-user-select:none;user-select:none;-webkit-tap-highlight-color:transparent;touch-action:manipulation;-webkit-text-size-adjust:100%}
#app{display:flex;flex-direction:column;height:100%;height:100dvh;
  padding:env(safe-area-inset-top) env(safe-area-inset-right) env(safe-area-inset-bottom) env(safe-area-inset-left)}
header{position:relative;isolation:isolate;padding-top:46px;background:var(--ink);border-bottom:4px solid #000;flex:0 0 auto}
header::before{content:"";position:absolute;z-index:-1;inset:0;height:46px;background:url('head.png') center center/cover no-repeat;image-rendering:pixelated;pointer-events:none}
.titlebar{position:absolute;inset:0 0 auto;z-index:1;height:46px;display:flex;align-items:center;gap:10px;padding:4px 12px}
.logo{position:relative;display:inline-flex;align-items:center;color:#ffb52e;background:linear-gradient(180deg,#9b5b27 0 20%,#633518 20% 100%);border:3px solid #241b20;border-radius:6px;padding:1px 9px 1px 32px;font-family:'Pixelify Sans','Mitr',sans-serif;font-weight:700;font-size:19px;letter-spacing:1px;text-shadow:2px 2px 0 var(--red),-1px -1px 0 #ffd783;white-space:nowrap;box-shadow:0 0 0 2px #8e5a27,3px 4px 0 #000,inset 0 2px 0 #ffd783}
.logo::before{content:"";position:absolute;inset:-4px;border:1px solid #63c74d;border-radius:8px;pointer-events:none}
.logo-cat{position:absolute;left:-6px;top:-9px;width:30px;height:30px;display:grid;place-items:center;font:20px/1 'Mitr','Tahoma',sans-serif;filter:drop-shadow(2px 2px 0 #000);z-index:2}
.sub{color:#241b20;background:#ffcd75;border:2px solid #281b1b;border-radius:3px;padding:0 6px;font-size:12px;font-weight:500;box-shadow:2px 3px 0 #000;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.scroll{position:relative;z-index:1;display:flex;gap:8px;overflow-x:auto;overflow-y:hidden;scrollbar-width:none;-ms-overflow-style:none;-webkit-overflow-scrolling:touch;padding:8px 10px 11px;background:#604025;border-top:3px solid #b17836}
.scroll::-webkit-scrollbar{display:none}
.sep{flex:0 0 3px;background:#566c86;margin:4px 2px}
.btn{font-family:var(--font);font-size:15px;min-height:44px;min-width:44px;padding:6px 12px;background:#f4dfb5;color:var(--ink);
  border:3px solid #30201b;box-shadow:inset 2px 2px 0 rgba(255,255,255,.72),inset -2px -2px 0 rgba(111,75,43,.26),4px 4px 0 #000;
  cursor:pointer;white-space:nowrap;display:inline-flex;align-items:center;justify-content:center;gap:6px;border-radius:5px;text-decoration:none;
  flex:0 0 auto;transition:transform .08s steps(2,end),box-shadow .08s steps(2,end)}
.btn:hover:not(:disabled){transform:translate(-1px,-1px);box-shadow:inset 2px 2px 0 rgba(255,255,255,.72),inset -2px -2px 0 rgba(111,75,43,.26),5px 5px 0 #000}
.btn:active:not(:disabled){transform:translate(4px,4px);box-shadow:inset 2px 2px 0 rgba(255,255,255,.72),inset -2px -2px 0 rgba(111,75,43,.26),0 0 0 #000}
.btn:focus-visible{outline:3px solid var(--blue);outline-offset:2px}
.btn:disabled{opacity:.55;cursor:not-allowed}
.btn.on{background:var(--yellow)}
.btn.primary{background:var(--green)}
.btn.danger{background:var(--orange)}
.btn.mini{min-height:34px;font-size:13px;padding:2px 8px}
.tbtn{flex-direction:column;gap:0;font-size:12px;min-width:66px;padding:3px 8px;line-height:1.2}
.tbtn .ic{font-size:20px;line-height:1.15}
@media (min-width:1400px){
  #toolbar::after{content:"";align-self:center;flex:0 0 62px;height:58px;margin-left:auto;background:url('mascot_clean.png') center/contain no-repeat;filter:drop-shadow(2px 2px 0 #241b20);pointer-events:none}
}
#hint{background:var(--yellow);border-bottom:3px solid var(--ink);padding:6px 12px;font-size:14px;line-height:1.35;flex:0 0 auto}
#toolStatus{background:#fff9e8;border-bottom:2px solid #6b4727;padding:3px 12px;font-size:12px;line-height:1.3;flex:0 0 auto}
#quickTools{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:6px;margin:8px 0}
#quickTools input{min-width:0;width:100%;font:13px var(--font);padding:6px;border:2px solid var(--ink);background:#fff}
#quickTools .btn{font-size:12px;min-height:36px;padding:3px 6px}
main{flex:1;display:flex;flex-direction:column;min-height:0}
#stage{flex:1;position:relative;min-height:150px;overflow:hidden;background:var(--paper);border:5px solid #6b4727;box-shadow:inset 0 0 0 2px #d3a45c}
#cv{position:absolute;inset:0;touch-action:none;display:block;cursor:crosshair}
#isoRightPane{display:none;position:absolute;left:50%;top:0;right:0;bottom:0;border-left:3px solid #6b4727;background:var(--paper)}
#stage.isomorphism-mode #cv{width:50%}
#stage.isomorphism-mode #isoRightPane{display:block}
#isoCv{position:absolute;inset:0;width:100%;height:100%;display:block;pointer-events:auto;touch-action:none;cursor:crosshair}
.iso-pane-title.left{display:none}
#stage.isomorphism-mode .iso-pane-title.left{display:block}
.iso-pane-title{position:absolute;z-index:2;left:8px;top:8px;background:#fff;border:2px solid var(--ink);box-shadow:2px 2px 0 var(--ink);padding:3px 7px;font-size:12px;font-weight:bold;pointer-events:none}
#isoRightStatus{position:absolute;z-index:2;left:8px;right:8px;top:42px;text-align:center;background:rgba(255,255,255,.9);padding:5px;font-size:12px;pointer-events:none}
#isoMappingLegend{display:none;max-height:125px;overflow:auto;background:#fff;border:2px solid var(--ink);box-shadow:2px 2px 0 var(--ink);padding:6px;gap:6px 10px;flex-wrap:wrap;margin:8px 0}
#isoMappingLegend.visible{display:flex}
.iso-pair-chip{display:inline-flex;align-items:center;gap:4px;font-size:11px;white-space:nowrap}
.iso-pair-chip i{width:11px;height:11px;border:1px solid var(--ink);display:inline-block;flex:0 0 auto}
#stage.isomorphism-mode #zoom{right:calc(50% + 10px)}
#stage.isomorphism-mode #badge{top:42px}
#badge{position:absolute;left:8px;top:8px;background:#fff;border:3px solid var(--ink);box-shadow:3px 3px 0 var(--ink);padding:4px 8px;font-size:13px;pointer-events:none}
#zoom{position:absolute;right:10px;bottom:10px;display:flex;flex-direction:column;gap:8px}
#zoom .btn{font-size:20px;padding:0;width:46px}
#dock{flex:0 0 auto;max-height:48vh;overflow-y:auto;background:#e8e4d8;border-top:4px solid #6b4727;padding:4px 10px 10px;-webkit-overflow-scrolling:touch}
@media (min-width:900px){
  main{flex-direction:row}
  #dock{width:390px;max-height:none;border-top:none;border-left:4px solid #6b4727}
  .scroll{padding:4px 10px 6px}
  .tbtn{min-height:36px;font-size:11px}
  .tbtn .ic{font-size:16px}
  .logo{font-size:15px;letter-spacing:.5px;padding:1px 7px 1px 27px;border-width:2px;box-shadow:0 0 0 2px #8e5a27,2px 3px 0 #000,inset 0 2px 0 #ffd783}
  .logo-cat{left:-5px;top:-7px;width:25px;height:25px;font-size:17px}
  .sub{font-size:10px}
}
.dockhead{display:flex;align-items:flex-start;gap:6px;padding-top:6px}
.dockhead #dockToggle{flex:0 0 auto;margin-top:2px}
.tabgrid{flex:1;display:grid;grid-template-columns:repeat(auto-fill,minmax(100px,1fr));gap:8px;padding:2px 4px 8px 0}
.btn.tab{font-size:14px;min-width:0;width:100%;padding:6px 6px;white-space:normal;line-height:1.2;text-align:center}

.row{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin:8px 0}
.desc{background:#fff9e8;border:3px solid #6b4727;padding:8px 10px;font-size:14px;line-height:1.5;box-shadow:3px 3px 0 #241b20}
.desc .app{display:block;margin-top:4px;color:#257179;font-weight:bold}
label.sel{display:flex;flex-direction:column;font-size:13px;flex:1;min-width:130px;gap:3px}
select{font-family:var(--font);font-size:15px;min-height:44px;border:3px solid var(--ink);background:#fff;padding:4px;border-radius:0;box-shadow:3px 3px 0 var(--ink);color:var(--ink);width:100%}
#mbody input[type=text]{font-family:var(--font);font-size:15px;min-height:44px;border:3px solid var(--ink);background:#fff;padding:6px 8px;border-radius:0;box-shadow:3px 3px 0 var(--ink);color:var(--ink);width:100%;margin-top:4px}
#mbody input[type=number],#mbody textarea{font-family:var(--font);font-size:15px;min-height:44px;border:3px solid var(--ink);background:#fff;padding:6px 8px;border-radius:0;box-shadow:3px 3px 0 var(--ink);color:var(--ink);width:100%;margin-top:4px}
#mbody textarea{min-height:82px;resize:vertical}
.bigbtn{width:100%;font-size:17px;min-height:50px}
.player .btn{flex:1;font-size:18px;padding:4px;min-width:44px}
input[type=range]{flex:1;accent-color:var(--red);height:34px;min-width:120px}
#stepLbl{font-size:13px;min-width:80px;text-align:right}
.speed .btn{flex:1;font-size:14px}
.stepbox{background:var(--ink);color:var(--green);border:3px solid #000;padding:10px 12px;min-height:72px;font-size:15px;line-height:1.55;box-shadow:inset 0 0 0 3px var(--navy);-webkit-user-select:text;user-select:text}
.legend{font-size:12px;display:flex;flex-wrap:wrap;gap:6px 12px;margin-top:6px}
.lg{display:inline-flex;align-items:center;gap:5px}
.lg i{display:inline-block;width:16px;height:16px;border:2px solid var(--ink)}
.lg i.ln{height:6px;width:24px;border:none}
.lg i.dash{height:0;width:24px;border:none;border-top:5px dashed var(--red)}
#quick{font-size:13px;background:#fff;border:2px solid var(--ink);padding:4px 8px}
#dock.collapsed .collapsible{display:none}
@keyframes blink{50%{background:var(--yellow)}}
.glow{animation:blink .9s steps(2) infinite}
/* modal */
#modal{position:fixed;inset:0;background:rgba(26,28,44,.65);display:flex;align-items:center;justify-content:center;z-index:50;
  padding:calc(env(safe-area-inset-top) + 10px) calc(env(safe-area-inset-right) + 10px) calc(env(safe-area-inset-bottom) + 10px) calc(env(safe-area-inset-left) + 10px)}
#modal.hidden{display:none}
.win{background:#fff;border:4px solid var(--ink);box-shadow:8px 8px 0 #000;max-width:780px;width:100%;max-height:100%;display:flex;flex-direction:column}
.winbar{background:var(--dblue);color:#fff;display:flex;justify-content:space-between;align-items:center;padding:4px 4px 4px 12px;border-bottom:4px solid var(--ink);font-weight:bold;gap:8px}
.winbar .btn{min-height:38px;min-width:38px;padding:0 8px;background:var(--orange)}
#mbody{overflow:auto;padding:14px;-webkit-user-select:text;user-select:text;line-height:1.55;-webkit-overflow-scrolling:touch}
#mbody h3{margin:16px 0 6px;font-size:17px;border-bottom:3px solid var(--ink);display:inline-block}
.hero{background:var(--green);border:3px solid var(--ink);box-shadow:4px 4px 0 var(--ink);padding:12px 14px;font-size:17px;margin-bottom:12px}
.hero.warn{background:var(--yellow)}
.hero.bad{background:var(--orange)}
.bignum{font-size:30px;font-weight:bold;display:inline-block;padding:0 6px;background:#fff;border:3px solid var(--ink);margin-left:4px}
.route{margin-top:8px;line-height:2.1}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px;margin:10px 0}
.card{border:3px solid var(--ink);box-shadow:3px 3px 0 var(--ink);padding:8px 10px;background:#fffbe6}
.card .k{font-size:12px;opacity:.75}
.card .v{font-size:22px;font-weight:bold}
.tw{overflow:auto;max-width:100%}
.tbl{border-collapse:collapse;margin:6px 0;font-size:14px}
.tbl th,.tbl td{border:2px solid var(--ink);padding:4px 9px;text-align:center;white-space:nowrap}
.tbl th{background:var(--yellow)}
.tbl td.l{text-align:left;white-space:normal}
.chip{display:inline-block;border:2px solid var(--ink);padding:1px 8px;margin:2px;background:#fff;box-shadow:2px 2px 0 var(--ink)}
.sw{display:inline-block;width:20px;height:20px;border:3px solid var(--ink);vertical-align:middle;margin-right:6px}
.grp{border:3px solid var(--ink);padding:8px;margin:8px 0;background:#fff;box-shadow:3px 3px 0 var(--ink)}
.grp .gh{display:flex;align-items:center;justify-content:space-between;gap:8px;font-weight:bold;margin-bottom:4px}
.note{background:#fff7d6;border:3px dashed var(--ink);padding:8px 10px;margin-top:12px}
.preview{max-width:100%;border:3px solid var(--ink);display:block;margin-top:10px;-webkit-touch-callout:default;-webkit-user-select:auto;user-select:auto}
.pgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}
.pcard{border:3px solid var(--ink);box-shadow:4px 4px 0 var(--ink);padding:10px;background:#fffbe6;display:flex;flex-direction:column;gap:8px}
.pcard b{font-size:16px}
ol.steps li{margin-bottom:6px}
#toast{position:fixed;left:50%;top:calc(env(safe-area-inset-top) + 120px);transform:translateX(-50%);background:var(--ink);color:#fff;
  padding:8px 14px;border:3px solid #fff;box-shadow:4px 4px 0 #000;z-index:60;opacity:0;transition:opacity .2s;pointer-events:none;max-width:90vw;text-align:center;font-size:14px}
</style>
</head>
<body>
<div id="app">
  <header>
    <div class="titlebar"><span class="logo"><span class="logo-cat" aria-hidden="true">🐱</span>GRAPH LAB</span><span class="sub">Logistics &amp; Urban Planning</span></div>
    <div class="scroll" id="toolbar">
      <button type="button" class="btn tbtn on" data-tool="move"><span class="ic">✋</span>ย้าย/เลื่อน</button>
      <button type="button" class="btn tbtn" data-tool="node"><span class="ic">⬛</span>เพิ่มจุด</button>
      <button type="button" class="btn tbtn" data-tool="edge"><span class="ic">🔗</span>เชื่อมเส้น</button>
      <button type="button" class="btn tbtn" data-tool="edit"><span class="ic">✏️</span>แก้ชื่อ/น้ำหนัก</button>
      <button type="button" class="btn tbtn" data-tool="bend"><span class="ic">〰️</span>ดัดเส้น</button>
      <button type="button" class="btn tbtn" data-tool="del"><span class="ic">🗑️</span>ลบ</button>
      <button type="button" class="btn tbtn" data-tool="edgeColor"><span class="ic">🎨</span>ระบายสีเส้น</button>
      <span class="sep"></span>
      <button type="button" class="btn tbtn" id="aDir"><span class="ic" id="dirIc">—</span><span id="dirTxt">ไม่มีทิศ</span></button>
      <button type="button" class="btn tbtn" id="aUndo"><span class="ic">↶</span>Undo</button>
      <button type="button" class="btn tbtn" id="aRedo" disabled><span class="ic">↷</span>Redo</button>
      <button type="button" class="btn tbtn" id="aStraight"><span class="ic">📏</span>เส้นตรงหมด</button>
      <button type="button" class="btn tbtn" id="aPreset"><span class="ic">📂</span>ตัวอย่าง</button>
      <button type="button" class="btn tbtn" id="aGenerate"><span class="ic">🧩</span>สร้างกราฟ</button>
      <button type="button" class="btn tbtn" id="aLayout"><span class="ic">🪄</span>จัดวาง</button>
      <button type="button" class="btn tbtn" id="aPNG"><span class="ic">🖼️</span>PNG</button>
      <button type="button" class="btn tbtn" id="aClear"><span class="ic">🧹</span>ล้างกราฟ</button>
      <button type="button" class="btn tbtn" id="aHelp"><span class="ic">❓</span>วิธีใช้</button>
    </div>
  </header>
  <div id="hint"></div>
  <div id="toolStatus" role="status" aria-live="polite"></div>
  <main>
    <div id="stage">
      <canvas id="cv"></canvas>
      <div id="badge"></div>
      <div class="iso-pane-title left">กราฟที่ 1</div>
      <div id="isoRightPane" aria-label="กราฟที่สองสำหรับเปรียบเทียบ">
        <canvas id="isoCv"></canvas>
        <div class="iso-pane-title">กราฟที่ 2</div>
        <div id="isoRightStatus">เลือก Isomorphic Graphs แล้วเริ่มเปรียบเทียบเพื่อแสดงกราฟที่สอง</div>
      </div>
      <div id="zoom">
        <button type="button" class="btn" id="zIn" title="ซูมเข้า">+</button>
        <button type="button" class="btn" id="zOut" title="ซูมออก">−</button>
        <button type="button" class="btn" id="zFit" title="จัดกึ่งกลาง">⌖</button>
      </div>
    </div>
    <aside id="dock">
      <div class="dockhead">
        <div class="tabgrid" id="tabs"></div>
        <button type="button" class="btn mini" id="dockToggle" title="ย่อ/ขยายแผง">▾</button>
      </div>
      <div id="algoDesc" class="desc collapsible"></div>
      <div id="isoMappingLegend" aria-live="polite"></div>
      <div id="quickTools" class="collapsible">
        <input id="nodeSearch" type="search" placeholder="ค้นหาจุดยอด..." aria-label="ค้นหาจุดยอด">
        <button type="button" class="btn" id="searchNode">🔎 ไปยังจุด</button>
        <input id="quickCommand" type="text" placeholder="คำสั่ง: v1-v2:5" aria-label="คำสั่งสร้างเส้น">
        <button type="button" class="btn" id="runCommand">↵ ทำคำสั่ง</button>
      </div>
      <div class="row collapsible" id="selRow">
        <label class="sel" id="lblS"><span id="lblSText">ต้นทาง</span><select id="selS"></select></label>
        <label class="sel" id="lblT"><span id="lblTText">ปลายทาง</span><select id="selT"></select></label>
      </div>
      <div class="row"><button type="button" class="btn primary bigbtn" id="runBtn">▶ เริ่มรัน</button></div>
      <div id="player" class="player">
        <div class="row">
          <button type="button" class="btn" id="bFirst" title="ขั้นแรก">⏮</button>
          <button type="button" class="btn" id="bPrev" title="ย้อน">◀</button>
          <button type="button" class="btn" id="bPlay" title="เล่นอัตโนมัติ">▶</button>
          <button type="button" class="btn" id="bNext" title="ถัดไป">▶|</button>
          <button type="button" class="btn" id="bLast" title="ขั้นสุดท้าย">⏭</button>
        </div>
        <div class="row"><input type="range" id="slider" min="0" max="0" value="0"><span id="stepLbl">ขั้น 0/0</span></div>
        <div class="row speed">
          <button type="button" class="btn" data-sp="0.5">0.5×</button>
          <button type="button" class="btn on" data-sp="1">1×</button>
          <button type="button" class="btn" data-sp="2">2×</button>
          <button type="button" class="btn" data-sp="4">4×</button>
        </div>
        <div id="stepText" class="stepbox"></div>
        <div class="row">
          <button type="button" class="btn" id="sumBtn" style="flex:1">📊 สรุปผล</button>
          <button type="button" class="btn danger" id="clearRunBtn" style="flex:1">✖ ล้างผล</button>
        </div>
      </div>
      <div id="legend" class="legend collapsible"></div>
      <div class="row collapsible"><div id="quick"></div></div>
    </aside>
  </main>
</div>
<div id="modal" class="hidden"><div class="win"><div class="winbar"><span id="mtitle"></span><button type="button" class="btn" id="mclose">✖</button></div><div id="mbody"></div></div></div>
<div id="toast"></div>

<script>
(() => {
'use strict';
const $ = s => document.querySelector(s);
const $$ = s => [...document.querySelectorAll(s)];
const cv = $('#cv'), ctx = cv.getContext('2d');
const isoCv = $('#isoCv'), isoCtx = isoCv.getContext('2d');
const FONT = "'Mitr',Tahoma,sans-serif";
const INK = '#1a1c2c', PAPER = '#f4efe1';
const PALETTE = ['#ef7d57','#41a6f6','#a7f070','#ffcd75','#f4a6d7','#73eff7','#b13e53','#38b764','#c28a4a','#94b0c2','#5d275d','#3b5dc9','#257179','#d4a5ff','#566c86'];
const NODE_FILL = {current:'#d7263d', consider:'#3a86ff', visited:'#2a9d8f', path:'#f4a261', inS:'#8338ec'};
const EDGE_STY = {
  base:{c:INK,w:3}, consider:{c:'#ef7d57',w:6,hl:1}, soft:{c:'#38b764',w:4}, tree:{c:'#38b764',w:6,hl:1},
  path:{c:'#38b764',w:8,hl:1}, reject:{c:'#94b0c2',w:3,dash:1}, cut:{c:'#b13e53',w:7,dash:1,hl:1},
  flow:{c:'#3b5dc9',w:5}, sat:{c:'#5d275d',w:6,hl:1}
};
const NR = 22, MINS = 0.2, MAXS = 4, EPS = 1e-9, LS_KEY = 'graphTheoryLab.v1', UNDO_MAX = 70;
const IOS = /iPad|iPhone|iPod/.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);

function emptyGraph(){ return {nodes:[], edges:[], directed:false, nextId:1, nextEid:1, source:null, sink:null, colorNames:[]}; }
let G = emptyGraph(), view = {x:0, y:0, s:1}, W = 300, H = 300, DPR = 1;
let isoGraph = null, isoFirstGraph = null, isoView = {x:0, y:0, s:1}, isoMapping = null, isoColors = [], isoAnimation = null;
let planarityAnimation = null;
let isoSplitView = false, isoPreviousView = null;
let tool = 'move', selNode = null, isoSelNode = null, undoStack = [], redoStack = [], algo = 'dijkstra';
let activeSide = 'left', lastActiveSide = 'left', sideContext = null;
let run = null, stepIdx = 0, playing = false, timer = null, speed = 1;
const pointers = new Map(); let drag = null, pinch = null, lastTap = {t:0, key:''};
let hoverNode = null, hoverEdge = null, hoverStarted = 0, hoverFrame = 0;
let edgePreview = null, isoEdgePreview = null;

/* ---------- utils ---------- */
const clamp = (v,a,b) => Math.max(a, Math.min(b, v));
const fmt = x => x === Infinity ? '∞' : (Number.isInteger(x) ? String(x) : String(+(+x).toFixed(3)));
const esc = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const nodeById = id => G.nodes.find(n => n.id === id);
const nm = id => { const n = nodeById(id); return n ? n.label : '?'; };
const edgeName = e => `${nm(e.u)} ${G.directed ? '→' : '–'} ${nm(e.v)}`;
const cName = i => G.colorNames[i] || `สี ${i+1}`;
const cmpNum = (a,b) => a === b ? 0 : (a < b ? -1 : 1);
const card = (k,v) => `<div class="card"><div class="k">${k}</div><div class="v">${v}</div></div>`;
const appNote = t => `<div class="note">💡 <b>การประยุกต์:</b> ${t}</div>`;
function textOn(hex){ const r=parseInt(hex.slice(1,3),16), g=parseInt(hex.slice(3,5),16), b=parseInt(hex.slice(5,7),16); return (0.299*r+0.587*g+0.114*b) < 140 ? '#ffffff' : INK; }
let toastT;
function toast(msg){ const t=$('#toast'); t.textContent=msg; t.style.opacity=1; clearTimeout(toastT); toastT=setTimeout(()=>t.style.opacity=0, 2000); }
function openModal(title, html){ $('#mtitle').textContent=title; $('#mbody').innerHTML=html; $('#modal').classList.remove('hidden'); $('#mbody').scrollTop=0; }
function closeModal(){ $('#modal').classList.add('hidden'); }
function alertBox(msg){ openModal('⚠ แจ้งเตือน', `<div class="hero warn">${msg}</div>`); }

/* ---------- save / undo ---------- */
function sanitize(g){
  g = Object.assign(emptyGraph(), g);
  g.nodes = (g.nodes||[]).filter(n => n && typeof n.id === 'number');
  g.nodes.forEach(n => { if(n.label == null) n.label = 'v'+n.id; if(n.color === undefined) n.color = null; });
  const ids = new Set(g.nodes.map(n => n.id));
  g.edges = (g.edges||[]).filter(e => ids.has(e.u) && ids.has(e.v));
  g.edges.forEach(e => { e.w = Number(e.w)||0; e.curve = e.curve||0; if(e.color === undefined) e.color = null; });
  g.nextId = Math.max(g.nextId||1, 1, ...g.nodes.map(n => n.id+1));
  g.nextEid = Math.max(g.nextEid||1, 1, ...g.edges.map(e => e.id+1));
  if(!ids.has(g.source)) g.source = null;
  if(!ids.has(g.sink)) g.sink = null;
  if(!Array.isArray(g.colorNames)) g.colorNames = [];
  return g;
}
function save(){
  try{
    const leftGraph=sideContext ? sideContext.graph : G;
    const leftView=sideContext ? sideContext.view : view;
    localStorage.setItem(LS_KEY, JSON.stringify({
      G:leftGraph, view:leftView, tab:algo,
      isoGraph:activeSide==='right' ? G : isoGraph,
      isoView:activeSide==='right' ? view : isoView
    }));
  }catch(error){ console.error('Could not save graph state:',error); }
}
function load(){
  try{
    const d = JSON.parse(localStorage.getItem(LS_KEY));
    if(d && d.G){
      G=sanitize(d.G);
      if(d.view && isFinite(d.view.s)) view=d.view;
      if(d.isoGraph) isoGraph=sanitize(d.isoGraph);
      if(d.isoView && isFinite(d.isoView.s)) isoView=d.isoView;
      return d.tab || 'dijkstra';
    }
  }catch(error){ console.error('Could not load saved graph state:',error); }
  return null;
}
function updateHistoryButtons(){
  $('#aUndo').disabled = !undoStack.length;
  $('#aRedo').disabled = !redoStack.length;
}
function pushUndo(){
  undoStack.push({side:activeSide, graph:JSON.stringify(G)});
  if(undoStack.length > UNDO_MAX) undoStack.shift();
  redoStack = [];
  updateHistoryButtons();
}
function graphForSide(side){ return side==='right' ? isoGraph : G; }
function restoreGraphForSide(side, graph){
  if(side==='right') isoGraph=sanitize(graph);
  else G=sanitize(graph);
}
function historyChange(side){
  if(side==='right'){
    if(algo==='isomorphism')invalidateIsomorphismResult();
    isoSelNode=null;isoEdgePreview=null;
    save();updateHistoryButtons();updateBadge();updateHint();
    if(algo==='isomorphism')$('#isoRightStatus').textContent=`กราฟที่สองมี ${isoGraph?isoGraph.nodes.length:0} จุด • ${isoGraph?isoGraph.edges.length:0} เส้น — ใช้เครื่องมือด้านบนแก้ไขได้`;
    draw();
  }else{
    selNode=null;edgePreview=null;afterChange();
  }
}
function undo(){
  if(!undoStack.length) return toast('ไม่มีขั้นให้ย้อนแล้ว');
  const entry=undoStack.pop(), current=graphForSide(entry.side) || emptyGraph();
  redoStack.push({side:entry.side,graph:JSON.stringify(current)});
  if(redoStack.length > UNDO_MAX) redoStack.shift();
  restoreGraphForSide(entry.side,JSON.parse(entry.graph)); clearRun(); historyChange(entry.side);
  toast(`↶ ย้อนแล้ว (ไปข้างหน้าได้อีก ${redoStack.length} ขั้น)`);
}
function redo(){
  if(!redoStack.length) return toast('ไม่มีขั้นให้ไปข้างหน้าแล้ว');
  const entry=redoStack.pop(), current=graphForSide(entry.side) || emptyGraph();
  undoStack.push({side:entry.side,graph:JSON.stringify(current)});
  if(undoStack.length > UNDO_MAX) undoStack.shift();
  restoreGraphForSide(entry.side,JSON.parse(entry.graph)); clearRun(); historyChange(entry.side);
  toast(`↷ ไปข้างหน้าแล้ว (ไปข้างหน้าได้อีก ${redoStack.length} ขั้น)`);
}
function commit(fn, invalidate = true){ pushUndo(); fn(); if(invalidate) clearRun(); afterChange(); }
function afterChange(){
  if(algo==='isomorphism') invalidateIsomorphismResult();
  save(); updateHistoryButtons(); draw();
  if(activeSide==='right') return;
  refreshSelects(); updateBadge(); updateHint();
}

function withCanvasSide(side, action){
  if(side!=='right' || !isoSplitView){ activeSide='left';lastActiveSide='left';return action(); }
  const previous={G,view,selNode,edgePreview};
  sideContext={graph:G,view};
  G=isoGraph || emptyGraph();
  if(!isoGraph) G.directed=previous.G.directed;
  view=isoView;
  selNode=isoSelNode;
  edgePreview=isoEdgePreview;
  activeSide='right';lastActiveSide='right';
  try{ return action(); }
  finally{
    isoGraph=G;isoView=view;isoSelNode=selNode;isoEdgePreview=edgePreview;
    G=previous.G;view=previous.view;selNode=previous.selNode;edgePreview=previous.edgePreview;
    activeSide='left';sideContext=null;
    updateHistoryButtons();updateBadge();updateHint();
      if(algo==='isomorphism'&&!isoFirstGraph&&isoGraph){
      $('#isoRightStatus').textContent=`กราฟที่สองมี ${isoGraph.nodes.length} จุด • ${isoGraph.edges.length} เส้น — ใช้เครื่องมือด้านบนแก้ไขได้`;
    }
    draw();
  }
}
function withLastCanvasSide(action){
  return withCanvasSide(lastActiveSide,action);
}

/* ---------- geometry ---------- */
function toWorld(sx, sy){ return {x:(sx-view.x)/view.s, y:(sy-view.y)/view.s}; }
function parallelEdgeCurves(graph){
  const groups=new Map(),curves=new Map();
  for(const edge of graph.edges){
    const key=edge.u===edge.v?`loop:${edge.u}`:`pair:${Math.min(edge.u,edge.v)}:${Math.max(edge.u,edge.v)}`;
    if(!groups.has(key))groups.set(key,[]);
    groups.get(key).push(edge);
  }
  for(const group of groups.values()){
    if(group.length<2)continue;
    group.sort((a,b)=>a.id-b.id);
    group.forEach((edge,index)=>curves.set(edge.id,(index-(group.length-1)/2)*28));
  }
  return curves;
}
function edgeGeom(e, curveMap=null){
  const a = nodeById(e.u), b = nodeById(e.v); if(!a || !b) return null;
  const curve=curveMap&&curveMap.has(e.id)?curveMap.get(e.id)*(e.u<=e.v?1:-1):(e.curve||0);
  if(a === b){
    const offset = curve, lift = 48 + Math.abs(offset);
    return {a:{x:a.x-12,y:a.y-17},b:{x:a.x+12,y:a.y-17},mx:a.x+offset,my:a.y-lift/2,
      nx:1,ny:0,cx:a.x+offset,cy:a.y-lift,px:a.x+offset,py:a.y-lift/2};
  }
  const mx=(a.x+b.x)/2, my=(a.y+b.y)/2, dx=b.x-a.x, dy=b.y-a.y, L=Math.hypot(dx,dy)||1;
  const nx=-dy/L, ny=dx/L, c=curve;
  return {a, b, mx, my, nx, ny, cx:mx+nx*c*2, cy:my+ny*c*2, px:mx+nx*c, py:my+ny*c};
}
function bez(g, t){ const u=1-t; return {x:u*u*g.a.x+2*u*t*g.cx+t*t*g.b.x, y:u*u*g.a.y+2*u*t*g.cy+t*t*g.b.y}; }
function distSeg(p, a, b){ const dx=b.x-a.x, dy=b.y-a.y, L=dx*dx+dy*dy; let t=L?((p.x-a.x)*dx+(p.y-a.y)*dy)/L:0; t=clamp(t,0,1); return Math.hypot(p.x-(a.x+t*dx), p.y-(a.y+t*dy)); }
function hitNode(w){ const r=NR+6/view.s; for(let i=G.nodes.length-1;i>=0;i--){ const n=G.nodes[i]; if(Math.abs(w.x-n.x)<=r && Math.abs(w.y-n.y)<=r) return n; } return null; }
function hitEdge(w){
  const tol = 12/view.s, curveMap=parallelEdgeCurves(G); let best=null, bd=tol;
  for(const e of G.edges){
    const g = edgeGeom(e,curveMap); if(!g) continue;
    const dl = Math.hypot(w.x-g.px, w.y-g.py); if(dl < 16/view.s && dl < bd){ bd=dl; best=e; }
    let prev = bez(g,0);
    for(let i=1;i<=24;i++){ const p=bez(g,i/24); const d=distSeg(w,prev,p); if(d<bd){ bd=d; best=e; } prev=p; }
  }
  return best;
}

/* ---------- rendering ---------- */
function resize(){
  const r = $('#stage').getBoundingClientRect(); DPR = window.devicePixelRatio || 1;
  W = Math.max(1, isoSplitView ? r.width/2 : r.width); H = Math.max(1, r.height);
  cv.width = Math.round(W*DPR); cv.height = Math.round(H*DPR); cv.style.width = W+'px'; cv.style.height = H+'px';
  if(isoSplitView){
    const rightW = Math.max(1, r.width-W);
    isoCv.width = Math.round(rightW*DPR); isoCv.height = Math.round(H*DPR);
    isoCv.style.width = rightW+'px'; isoCv.style.height = H+'px';
  }
  draw();
}
function currentStep(){ return run ? run.steps[stepIdx] : null; }
function draw(){
  ctx.setTransform(DPR,0,0,DPR,0,0);
  renderScene(ctx, W, H, view, algo === 'isomorphism' && isoFirstGraph ? isoFirstGraph : G, algo === 'isomorphism' ? null : undefined, false);
  if(isoSplitView){
    const r = $('#stage').getBoundingClientRect(), rightW = Math.max(1,r.width-W);
    isoCtx.setTransform(DPR,0,0,DPR,0,0);
    if(isoGraph) renderScene(isoCtx, rightW, H, isoView, isoGraph, null, true);
    else { isoCtx.clearRect(0,0,rightW,H); isoCtx.fillStyle=PAPER; isoCtx.fillRect(0,0,rightW,H); }
  }
}
const CURSOR_STYLES = {
  move: 'grab',
  node: 'crosshair',
  edge: 'crosshair',
  edit: 'text',
  bend: 'move',
  del: 'not-allowed',
  edgeColor: 'crosshair'
};
function updateCanvasCursor(){
  cv.style.cursor = CURSOR_STYLES[tool] || 'default';
  isoCv.style.cursor = CURSOR_STYLES[tool] || 'default';
}
function setHover(node, edge){
  const nodeId = node ? node.id : null, edgeId = edge ? edge.id : null;
  updateCanvasCursor();
  if(nodeId === hoverNode && edgeId === hoverEdge) return;
  hoverNode = nodeId; hoverEdge = edgeId; hoverStarted = performance.now();
  updateCanvasCursor();
  draw();
  if((node || edge) && !hoverFrame) hoverFrame = requestAnimationFrame(animateHover);
}
function animateHover(){
  if(hoverNode == null && hoverEdge == null){ hoverFrame = 0; return; }
  draw(); hoverFrame = requestAnimationFrame(animateHover);
}
function renderScene(c, w, h, v, graph=G, stepOverride=undefined, comparisonPanel=false){
  const previousGraph=G; G=graph;
  try{
    c.fillStyle = PAPER; c.fillRect(0,0,w,h);
    const gs = 40*v.s;
    if(gs > 12){
      c.fillStyle = '#d6cdb5';
      const ox = ((v.x%gs)+gs)%gs, oy = ((v.y%gs)+gs)%gs;
      for(let x=ox;x<w;x+=gs) for(let y=oy;y<h;y+=gs) c.fillRect(Math.round(x)-1, Math.round(y)-1, 3, 3);
    }
    c.save(); c.translate(v.x, v.y); c.scale(v.s, v.s);
    const st = stepOverride === undefined ? currentStep() : stepOverride, showW = algo !== 'color';
    const curveMap=parallelEdgeCurves(G);
    for(const e of G.edges) drawEdge(c, e, st, showW, comparisonPanel, curveMap);
    const preview=graph===isoGraph ? {node:isoSelNode,point:isoEdgePreview} : {node:selNode,point:edgePreview};
    if(tool==='edge' && preview.node!=null && preview.point) drawEdgePreview(c,preview.node,preview.point);
    for(const n of G.nodes) drawNode(c, n, st, comparisonPanel);
    c.restore();
  }finally{ G=previousGraph; }
}
function drawEdgePreview(c, sourceId, target){
  const source = nodeById(sourceId); if(!source) return;
  const dx = target.x-source.x, dy = target.y-source.y, length = Math.hypot(dx,dy);
  if(length < 1) return;
  const ux = dx/length, uy = dy/length, endNode = hitNode(target);
  const start = {x:source.x+ux*NR, y:source.y+uy*NR};
  const endDistance = endNode && endNode.id !== sourceId ? Math.max(NR, length-NR) : length;
  const end = {x:source.x+ux*endDistance, y:source.y+uy*endDistance};
  c.save(); c.beginPath(); c.moveTo(start.x,start.y); c.lineTo(end.x,end.y);
  c.setLineDash([8,6]); c.lineWidth=4; c.strokeStyle='#ffcd75'; c.lineCap='round';
  c.shadowColor=INK; c.shadowBlur=2; c.stroke(); c.restore();
}
function pill(c, x, y, text, bg, fg, border){
  c.font = `bold 13px ${FONT}`;
  const tw = c.measureText(text).width, pw = tw+12, ph = 20;
  c.fillStyle = INK; c.fillRect(x-pw/2+2, y-ph/2+2, pw, ph);
  c.fillStyle = bg; c.fillRect(x-pw/2, y-ph/2, pw, ph);
  c.lineWidth = 2; c.strokeStyle = border || INK; c.strokeRect(x-pw/2, y-ph/2, pw, ph);
  c.fillStyle = fg; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText(text, x, y+1);
}
function tag(c, x, y, t, bg){
  c.fillStyle = INK; c.fillRect(x-9, y-9, 18, 18);
  c.fillStyle = bg; c.fillRect(x-7, y-7, 14, 14);
  c.fillStyle = '#fff'; c.font = `bold 11px ${FONT}`; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText(t, x, y+1);
}
function roundedBox(c, x, y, size, radius=6){
  const r = Math.min(radius, size/2);
  c.beginPath(); c.moveTo(x+r,y); c.lineTo(x+size-r,y); c.quadraticCurveTo(x+size,y,x+size,y+r);
  c.lineTo(x+size,y+size-r); c.quadraticCurveTo(x+size,y+size,x+size-r,y+size);
  c.lineTo(x+r,y+size); c.quadraticCurveTo(x,y+size,x,y+size-r);
  c.lineTo(x,y+r); c.quadraticCurveTo(x,y,x+r,y); c.closePath();
}
function drawEdge(c, e, st, showW, comparisonPanel=false, curveMap=null){
  const g = edgeGeom(e,curveMap); if(!g) return;
  const hovered = !comparisonPanel && hoverEdge === e.id, key = st && st.edge ? st.edge[e.id] : null;
  const S = EDGE_STY[key] || EDGE_STY.base;
  if(hovered){
    const wobble = Math.sin((performance.now()-hoverStarted)/75)*2.5;
    g.cx += g.nx*wobble; g.cy += g.ny*wobble; g.px += g.nx*wobble/2; g.py += g.ny*wobble/2;
  }
  const path = () => { c.beginPath(); c.moveTo(g.a.x,g.a.y); c.quadraticCurveTo(g.cx,g.cy,g.b.x,g.b.y); };
  c.save(); c.lineCap = 'round'; c.lineJoin = 'round';
  if(S.hl){ c.setLineDash([]); c.strokeStyle = INK; c.lineWidth = S.w+4; path(); c.stroke(); }
  const edgeColor = !key && e.color != null ? PALETTE[e.color % PALETTE.length] : S.c;
  c.setLineDash(S.dash ? [12,8] : []); c.strokeStyle = hovered ? '#ef7d57' : edgeColor; c.lineWidth = S.w+(hovered?3:0); path(); c.stroke(); c.setLineDash([]);
  if(G.directed){
    let t1 = 1;
    for(let i=0;i<=60;i++){ const t=1-i/60, p=bez(g,t); if(Math.abs(p.x-g.b.x)>NR+4 || Math.abs(p.y-g.b.y)>NR+4){ t1=t; break; } }
    const tip = bez(g,t1);
    const dx = 2*(1-t1)*(g.cx-g.a.x)+2*t1*(g.b.x-g.cx), dy = 2*(1-t1)*(g.cy-g.a.y)+2*t1*(g.b.y-g.cy);
    const L = Math.hypot(dx,dy)||1, ux = dx/L, uy = dy/L, sz = 10+S.w;
    c.beginPath(); c.moveTo(tip.x, tip.y);
    c.lineTo(tip.x-ux*sz-uy*sz*0.55, tip.y-uy*sz+ux*sz*0.55);
    c.lineTo(tip.x-ux*sz+uy*sz*0.55, tip.y-uy*sz-ux*sz*0.55); c.closePath();
    c.fillStyle = edgeColor; c.fill(); c.lineWidth = 2; c.strokeStyle = INK; c.stroke();
  }
  const txt = st && st.etext ? st.etext[e.id] : (showW ? fmt(e.w) : null);
  if(txt != null) pill(c, g.px, g.py, txt, '#ffffff', INK, S.hl ? S.c : INK);
  c.restore();
}
function drawNode(c, n, st, comparisonPanel=false){
  const hovered = !comparisonPanel && hoverNode === n.id;
  if(hovered){
    const phase = (performance.now()-hoverStarted)/75;
    c.save(); c.translate(n.x,n.y); c.rotate(Math.sin(phase)*0.035);
    const scale = 1.04+Math.sin(phase*2)*0.025; c.scale(scale,scale); c.translate(-n.x,-n.y);
  }
  const sty = st && st.node ? st.node[n.id] : null, r = NR;
  let fill = '#8bea3c';
  if(st && st.fill){ if(st.fill[n.id] != null) fill = PALETTE[st.fill[n.id] % PALETTE.length]; }
  else if(!st && n.color != null) fill = PALETTE[n.color % PALETTE.length];
  if(!(st && st.fill) && sty && NODE_FILL[sty]) fill = NODE_FILL[sty];
  let ring = null; if(sty === 'current') ring = '#b13e53'; if((comparisonPanel?isoSelNode:selNode)===n.id) ring = '#41a6f6';
  if(ring){ roundedBox(c, n.x-r-8, n.y-r-8, 2*r+16, 10); c.fillStyle = ring; c.fill(); c.strokeStyle = INK; c.lineWidth = 2; c.stroke(); }
  roundedBox(c, n.x-r+5, n.y-r+5, 2*r, 9); c.fillStyle = 'rgba(26,28,44,0.9)'; c.fill();
  roundedBox(c, n.x-r, n.y-r, 2*r, 9); c.fillStyle = fill; c.fill(); c.lineWidth = 3; c.strokeStyle = INK; c.stroke();
  c.fillStyle = 'rgba(255,255,255,0.85)'; c.fillRect(n.x-r+5, n.y-r+5, 7, 4); c.fillRect(n.x-r+5, n.y-r+9, 4, 5);
  c.fillStyle = 'rgba(26,28,44,0.18)'; c.fillRect(n.x+r-6, n.y-r+8, 3, 2*r-16); c.fillRect(n.x-r+8, n.y+r-6, 2*r-16, 3);
  const short = n.label.length <= 4;
  const label = short ? n.label : 'v'+n.id, numericLabel = /^\d+$/.test(label);
  c.fillStyle = textOn(fill); c.font = `bold ${numericLabel?16:(short?14:12)}px ${numericLabel?"Arial,Tahoma,sans-serif":FONT}`; c.textAlign = 'center'; c.textBaseline = 'middle';
  c.fillText(label, n.x, n.y+1);
  if(!short) pill(c, n.x, n.y+r+17, n.label, '#fffbe6', INK, INK);
  const T = TABS[algo];
  if(T && T.s && G.source === n.id) tag(c, n.x-r, n.y+r, 'S', '#38b764');
  if(T && T.t && G.sink === n.id) tag(c, n.x+r, n.y+r, 'T', '#b13e53');
  if(st && st.ntext && st.ntext[n.id] != null) pill(c, n.x, n.y-r-17, st.ntext[n.id], '#ffcd75', INK, INK);
  if(hovered) c.restore();
}

/* ---------- view ---------- */
function zoomAt(sx, sy, f){
  const ns = clamp(view.s*f, MINS, MAXS); f = ns/view.s;
  view.x = sx-(sx-view.x)*f; view.y = sy-(sy-view.y)*f; view.s = ns; draw(); saveSoon();
}
let saveT; function saveSoon(){ clearTimeout(saveT); saveT = setTimeout(save, 400); }
function fitGraphView(graph, width, height){
  if(!graph || !graph.nodes.length) return {x:width/2,y:height/2,s:1};
  let x0=Infinity,y0=Infinity,x1=-Infinity,y1=-Infinity;
  graph.nodes.forEach(node=>{x0=Math.min(x0,node.x);y0=Math.min(y0,node.y);x1=Math.max(x1,node.x);y1=Math.max(y1,node.y);});
  x0-=80;x1+=80;y0-=60;y1+=90;
  const top=88,bottom=52,availableHeight=Math.max(1,height-top-bottom);
  const scale=clamp(Math.min(width/(x1-x0),availableHeight/(y1-y0)),MINS,1.6);
  return {s:scale,x:width/2-(x0+x1)/2*scale,y:top+availableHeight/2-(y0+y1)/2*scale};
}
function setIsomorphismSplit(enabled){
  if(enabled===isoSplitView) return;
  if(enabled){
    isoPreviousView={...view};
    isoSplitView=true;
    lastActiveSide='left';
    $('#stage').classList.add('isomorphism-mode');
    resize();
    fitView();
    if(isoGraph){
      const r=$('#stage').getBoundingClientRect();
      isoView=fitGraphView(isoGraph,Math.max(1,r.width-W),H);
    }
  }else{
    isoSplitView=false;
    lastActiveSide='left';isoSelNode=null;isoEdgePreview=null;
    $('#stage').classList.remove('isomorphism-mode');
    if(isoPreviousView) view=isoPreviousView;
    isoPreviousView=null;
    resize();
  }
}
function fitView(){
  if(isoSplitView){
    if(lastActiveSide==='right'&&isoGraph){
      const r=$('#stage').getBoundingClientRect();
      isoView=fitGraphView(isoGraph,Math.max(1,r.width-W),H);
    }else view=fitGraphView(G,W,H);
    draw();save();return;
  }
  if(!G.nodes.length){ view = {x:W/2, y:H/2, s:1}; draw(); return; }
  let x0=Infinity, y0=Infinity, x1=-Infinity, y1=-Infinity;
  G.nodes.forEach(n => { x0=Math.min(x0,n.x); y0=Math.min(y0,n.y); x1=Math.max(x1,n.x); y1=Math.max(y1,n.y); });
  x0-=80; x1+=80; y0-=60; y1+=70;
  const s = clamp(Math.min(W/(x1-x0), H/(y1-y0)), MINS, 1.6);
  view.s = s; view.x = W/2-(x0+x1)/2*s; view.y = H/2-(y0+y1)/2*s; draw(); save();
}

/* ---------- pointer / touch ---------- */
function ptr(e,canvas){ const r=canvas.getBoundingClientRect();return {x:e.clientX-r.left,y:e.clientY-r.top}; }
function bindCanvas(canvas,side){
  const listen=(name,handler,options)=>canvas.addEventListener(name,e=>withCanvasSide(side,()=>handler(e)),options);
  listen('pointerdown',e=>{
    e.preventDefault();lastActiveSide=side;
    if(side==='left')setHover(null,null);
    if(side==='left'){updateBadge();updateHint();}
    try{canvas.setPointerCapture(e.pointerId);}catch(_){}
    const p=ptr(e,canvas);pointers.set(e.pointerId,p);
    if(pointers.size===2){
      const [a,b]=[...pointers.values()];
      pinch={side,d:Math.hypot(a.x-b.x,a.y-b.y)||1,cx:(a.x+b.x)/2,cy:(a.y+b.y)/2,v:{...view}};
      if(drag&&drag.undo)save();
      drag=null;return;
    }
    if(pointers.size>2)return;
    const w=toWorld(p.x,p.y),n=hitNode(w),ed=n?null:hitEdge(w);
    let type='tap';
    if(n&&(tool==='move'||tool==='node'))type='node';
    else if(ed&&tool==='bend')type='bend';
    else if(!n&&!ed)type='pan';
    drag={side,type,n,ed,w,sx:p.x,sy:p.y,lx:p.x,ly:p.y,moved:false,undo:false,offX:n?n.x-w.x:0,offY:n?n.y-w.y:0};
  });
  listen('pointermove',e=>{
    if(!pointers.has(e.pointerId)){
      if(e.pointerType!=='touch'){
        const p=ptr(e,canvas),w=toWorld(p.x,p.y),n=hitNode(w),ed=n?null:hitEdge(w);
        if(tool==='edge'&&(side==='right'?isoSelNode:selNode)!=null){
          if(side==='right')isoEdgePreview=w;else edgePreview=w;
          draw();
        }
        if(side==='left')setHover(n,ed);
      }
      return;
    }
    if(drag&&drag.side!==side)return;
    const p=ptr(e,canvas);pointers.set(e.pointerId,p);
    if(pinch&&pinch.side===side&&pointers.size>=2){
      const [a,b]=[...pointers.values()];
      const d=Math.hypot(a.x-b.x,a.y-b.y)||1,cx=(a.x+b.x)/2,cy=(a.y+b.y)/2;
      const ns=clamp(pinch.v.s*d/pinch.d,MINS,MAXS);
      const wx=(pinch.cx-pinch.v.x)/pinch.v.s,wy=(pinch.cy-pinch.v.y)/pinch.v.s;
      view.s=ns;view.x=cx-wx*ns;view.y=cy-wy*ns;draw();return;
    }
    if(!drag)return;
    if(!drag.moved&&Math.hypot(p.x-drag.sx,p.y-drag.sy)>6)drag.moved=true;
    if(!drag.moved)return;
    const w=toWorld(p.x,p.y);
    if(drag.type==='node'){
      if(!drag.undo){pushUndo();drag.undo=true;invalidateIsomorphismResult();}
      drag.n.x=w.x+drag.offX;drag.n.y=w.y+drag.offY;
    }else if(drag.type==='pan'){view.x+=p.x-drag.lx;view.y+=p.y-drag.ly;}
    else if(drag.type==='bend'){
      if(!drag.undo){pushUndo();drag.undo=true;invalidateIsomorphismResult();}
      const g=edgeGeom(drag.ed);
      if(g){let curve=(w.x-g.mx)*g.nx+(w.y-g.my)*g.ny;if(Math.abs(curve)<6)curve=0;drag.ed.curve=curve;}
    }
    drag.lx=p.x;drag.ly=p.y;draw();
  });
  const endPtr=e=>{
    if(!pointers.has(e.pointerId))return;
    pointers.delete(e.pointerId);
    if(pinch&&pinch.side===side){if(pointers.size<2){pinch=null;save();}drag=null;return;}
    if(!drag||drag.side!==side)return;
    const d=drag;drag=null;
    if(d.moved){save();return;}
    if(e.type==='pointercancel')return;
    handleTap(d);
  };
  listen('pointerup',endPtr);
  listen('pointercancel',endPtr);
  listen('pointerleave',()=>{
    if(!pointers.size){
      if(side==='right')isoEdgePreview=null;else edgePreview=null;
      if(side==='left')setHover(null,null);
      draw();
    }
  });
  listen('contextmenu',e=>e.preventDefault());
  listen('wheel',e=>{e.preventDefault();const p=ptr(e,canvas);zoomAt(p.x,p.y,Math.exp(-e.deltaY*0.0015));},{passive:false});
}
bindCanvas(cv,'left');
bindCanvas(isoCv,'right');
document.addEventListener('gesturestart', e => e.preventDefault());

function handleTap(d){
  const {n, ed, w} = d, now = Date.now();
  const key = n ? 'n'+n.id : ed ? 'e'+ed.id : 'bg';
  const dbl = (now-lastTap.t < 400 && lastTap.key === key); lastTap = {t:now, key};
  switch(tool){
    case 'move':
      if(dbl && n) renameNode(n); else if(dbl && ed) editWeight(ed);
      else if(n) toast(nodeInfo(n)); else if(ed) toast(`${edgeName(ed)} • น้ำหนัก = ${fmt(ed.w)} (แตะ 2 ครั้งเพื่อแก้)`);
      break;
    case 'node':
      if(!n && !ed) addNodeAt(w.x, w.y); else if(n && dbl) renameNode(n);
      break;
    case 'edge':
      if(!n){
        if(activeSide==='right'){isoSelNode=null;isoEdgePreview=null;}
        else{selNode=null;edgePreview=null;updateHint();}
        draw();break;
      }
      if(selNode==null||!nodeById(selNode)){selNode=n.id;}
      else{const u=selNode;selNode=null;addEdge(u,n.id);}
      if(activeSide==='right')isoEdgePreview={x:w.x,y:w.y};
      else edgePreview={x:w.x,y:w.y};
      updateHint(); draw();
      break;
    case 'edit': if(n) renameNode(n); else if(ed) editWeight(ed); break;
    case 'del': if(n) deleteNode(n); else if(ed) deleteEdge(ed); break;
    case 'edgeColor': if(ed) showEdgeColors(ed); break;
    case 'bend': if(ed && ed.curve){ commit(() => { ed.curve = 0; }, false); toast('📏 ทำให้เส้นตรงแล้ว'); } break;
  }
}
function nodeInfo(n){
  const d = degreeInfo()[n.id];
  return `${n.label} (v${n.id}) • deg = ${d.deg}` + (G.directed ? ` (เข้า ${d.in} / ออก ${d.out})` : '') + ' • แตะ 2 ครั้งเพื่อเปลี่ยนชื่อ';
}

/* ---------- edit ops ---------- */
function addNodeAt(x, y){
  let id; commit(() => { id = G.nextId++; G.nodes.push({id, x, y, label:'v'+id, color:null}); });
  toast(`➕ เพิ่ม v${id} แล้ว (ตั้งชื่อด้วยเครื่องมือ ✏️)`);
}
function askWeight(def, msg){
  for(;;){
    const s = prompt(msg, String(def)); if(s === null) return null;
    const t = String(s).trim().replace(',', '.'), v = Number(t);
    if(t !== '' && isFinite(v)) return v;
    alert('⚠ น้ำหนักต้องเป็นตัวเลข เช่น 5, 2.5 หรือ -3');
  }
}
function addEdge(u, v){
  const w = askWeight(1, `น้ำหนักของเส้น ${nm(u)} ${G.directed?'→':'–'} ${nm(v)}\n(รองรับจำนวนเต็ม ทศนิยม และค่าติดลบ)`);
  if(w === null) return;
  commit(() => storeEdge(u, v, w));
  toast(`🔗 สร้างเส้น ${nm(u)} ${G.directed?'→':'–'} ${nm(v)} = ${fmt(w)}`);
}
function storeEdge(u, v, w){
  const parallel = G.edges.filter(x => G.directed
    ? x.u === u && x.v === v
    : (x.u === u && x.v === v) || (x.u === v && x.v === u));
  const lanes = [0, 24, -24, 48, -48, 72, -72];
  const e = {id:G.nextEid++, u, v, w, color:null, curve:parallel.length ? lanes[parallel.length % lanes.length] : 0};
  if(u === v && parallel.length) e.curve = 18 * (parallel.length + 1);
  const reverse = G.directed && G.edges.find(x => x.u === v && x.v === u && x.u !== x.v);
  if(reverse){ e.curve = e.curve || 28; if(!reverse.curve) reverse.curve = 28; }
  G.edges.push(e);
}
function renameNode(n){
  const s = prompt('ตั้งชื่อจุดยอด (เช่น คลังสินค้า, ร้านค้า 1, โรงพยาบาล):', n.label);
  if(s === null) return;
  const t = s.trim() || ('v'+n.id);
  commit(() => { n.label = t; }, false);
}
function editWeight(e){
  const w = askWeight(e.w, `น้ำหนักใหม่ของเส้น ${edgeName(e)}:`);
  if(w === null) return;
  commit(() => { e.w = w; });
}
function showEdgeColors(edge){
  openModal(`🎨 ระบายสีเส้น ${edgeName(edge)}`,
    `<p>เลือกสีสำหรับเส้นนี้ (สีจะบันทึกในกราฟและ PNG)</p><div class="pgrid">`+
    PALETTE.map((color,index)=>`<button type="button" class="btn" data-edge-color="${index}" style="background:${color}">สี ${index+1}</button>`).join('')+
    `<button type="button" class="btn" data-edge-color="-1">ล้างสี</button></div>`);
  $('#mbody').dataset.edgeId=String(edge.id);
  $('#mbody').dataset.edgeSide=activeSide;
}
function deleteNode(n){
  commit(() => {
    G.edges = G.edges.filter(e => e.u !== n.id && e.v !== n.id);
    G.nodes = G.nodes.filter(x => x !== n);
    if(G.source === n.id) G.source = null; if(G.sink === n.id) G.sink = null; if(selNode === n.id) selNode = null;
  });
  toast(`🗑 ลบ ${n.label} แล้ว`);
}
function deleteEdge(e){ commit(() => { G.edges = G.edges.filter(x => x !== e); }); toast(`🗑 ลบเส้น ${edgeName(e)} แล้ว`); }

/* ---------- graph helpers ---------- */
function outAdj(){
  const adj = new Map(G.nodes.map(n => [n.id, []]));
  for(const e of G.edges){ adj.get(e.u).push({to:e.v, w:e.w, e}); if(!G.directed) adj.get(e.v).push({to:e.u, w:e.w, e}); }
  return adj;
}
function nbrSets(){
  const m = new Map(G.nodes.map(n => [n.id, new Set()]));
  for(const e of G.edges){ if(e.u === e.v) continue; m.get(e.u).add(e.v); m.get(e.v).add(e.u); }
  return m;
}
function components(){
  const nb = nbrSets(), seen = new Set(), comps = [];
  for(const n of G.nodes){
    if(seen.has(n.id)) continue;
    const comp = [], q = [n.id]; seen.add(n.id);
    while(q.length){ const u = q.shift(); comp.push(u); for(const v of nb.get(u)) if(!seen.has(v)){ seen.add(v); q.push(v); } }
    comps.push(comp);
  }
  return comps;
}
function degreeInfo(){
  const d = {}; G.nodes.forEach(n => d[n.id] = {deg:0, in:0, out:0});
  G.edges.forEach(e => { d[e.u].deg++; d[e.v].deg++; d[e.u].out++; d[e.v].in++; });
  return d;
}
function isBipartite(){
  const color=new Map(),adj=nbrSets();
  for(const n of G.nodes)if(!color.has(n.id)){
    color.set(n.id,0);const q=[n.id];
    while(q.length){const u=q.shift();for(const v of adj.get(u)){if(!color.has(v)){color.set(v,1-color.get(u));q.push(v);}else if(color.get(v)===color.get(u))return false;}}
  }
  return !G.edges.some(e=>e.u===e.v);
}
function isDAG(){
  if(!G.directed)return false;
  const indeg=new Map(G.nodes.map(n=>[n.id,0])),adj=new Map(G.nodes.map(n=>[n.id,[]]));
  for(const e of G.edges){adj.get(e.u).push(e.v);indeg.set(e.v,indeg.get(e.v)+1);}
  const q=G.nodes.filter(n=>indeg.get(n.id)===0).map(n=>n.id);let visited=0;
  while(q.length){const u=q.shift();visited++;for(const v of adj.get(u)){indeg.set(v,indeg.get(v)-1);if(indeg.get(v)===0)q.push(v);}}
  return visited===G.nodes.length;
}
function isStronglyConnected(){
  if(!G.directed||!G.nodes.length)return false;
  const reach=start=>{
    const adj=new Map(G.nodes.map(n=>[n.id,[]]));
    for(const e of G.edges)adj.get(start===-1?e.v:e.u).push(start===-1?e.u:e.v);
    const seen=new Set([G.nodes[0].id]),q=[G.nodes[0].id];
    while(q.length){for(const v of adj.get(q.shift()))if(!seen.has(v)){seen.add(v);q.push(v);}}
    return seen.size===G.nodes.length;
  };
  return reach(1)&&reach(-1);
}
function graphMetrics(){
  const ids=G.nodes.map(n=>n.id),adj=outAdj(),n=ids.length;
  const distances=new Map(),ecc=new Map(),degreeCent=new Map(),closeness=new Map(),betweenness=new Map(),clustering=new Map();
  for(const source of ids){
    const dist=new Map([[source,0]]),q=[source];
    while(q.length){const u=q.shift();for(const a of adj.get(u))if(!dist.has(a.to)){dist.set(a.to,dist.get(u)+1);q.push(a.to);}}
    distances.set(source,dist);
    ecc.set(source,dist.size===n?Math.max(0,...dist.values()):Infinity);
    const sum=[...dist.values()].reduce((a,b)=>a+b,0);
    closeness.set(source,n>1&&sum>0?(dist.size-1)/sum:0);
    const neighbors=nbrSets().get(source),k=neighbors.size;
    let links=0;for(const u of neighbors)for(const v of neighbors)if(u<v&&nbrSets().get(u).has(v))links++;
    clustering.set(source,k<2?0:2*links/(k*(k-1)));
    degreeCent.set(source,n>1?neighbors.size/(n-1):0);
  }
  if(n<=500){
    const centralAdj=new Map(ids.map(id=>[id,adj.get(id).map(a=>a.to)]));
    for(const source of ids){
      const stack=[],pred=new Map(ids.map(id=>[id,[]])),sigma=new Map(ids.map(id=>[id,0])),dist=new Map(ids.map(id=>[id,-1]));
      sigma.set(source,1);dist.set(source,0);const q=[source];
      while(q.length){const v=q.shift();stack.push(v);for(const w of centralAdj.get(v)){
        if(dist.get(w)<0){dist.set(w,dist.get(v)+1);q.push(w);}
        if(dist.get(w)===dist.get(v)+1){sigma.set(w,sigma.get(w)+sigma.get(v));pred.get(w).push(v);}
      }}
      const delta=new Map(ids.map(id=>[id,0]));
      while(stack.length){const w=stack.pop();for(const v of pred.get(w))if(sigma.get(w))delta.set(v,delta.get(v)+sigma.get(v)/sigma.get(w)*(1+delta.get(w)));if(w!==source)betweenness.set(w,(betweenness.get(w)||0)+delta.get(w));}
    }
    const scale=G.directed?((n-1)*(n-2)):((n-1)*(n-2)/2);
    if(scale>0)for(const id of ids)betweenness.set(id,(betweenness.get(id)||0)/(scale*(G.directed?1:2)));
    else for(const id of ids)betweenness.set(id,0);
  }
  let girth=Infinity;
  if(!G.directed){
    for(const e of G.edges)if(e.u===e.v)girth=1;
    const pairs=new Map();
    for(const e of G.edges)if(e.u!==e.v){const key=`${Math.min(e.u,e.v)}:${Math.max(e.u,e.v)}`;pairs.set(key,(pairs.get(key)||0)+1);}
    for(const count of pairs.values())if(count>1)girth=Math.min(girth,2);
    const simpleAdj=new Map(ids.map(id=>[id,[]]));
    for(const e of G.edges)if(e.u!==e.v){simpleAdj.get(e.u).push([e.v,e.id]);simpleAdj.get(e.v).push([e.u,e.id]);}
    for(const source of ids){
      const dist=new Map([[source,0]]),parentEdge=new Map(),q=[source];
      while(q.length){const u=q.shift();for(const [v,eid] of simpleAdj.get(u)){
        if(!dist.has(v)){dist.set(v,dist.get(u)+1);parentEdge.set(v,eid);q.push(v);}
        else if(parentEdge.get(u)!==eid&&parentEdge.get(v)!==eid)girth=Math.min(girth,dist.get(u)+dist.get(v)+1);
      }}
    }
  }
  const connected=n>0&&(G.directed?isStronglyConnected():components().length===1);
  return {ecc,degreeCent,closeness,betweenness,clustering,girth,connected,
    radius:connected?Math.min(...ecc.values()):Infinity,
    diameter:connected?Math.max(...ecc.values()):Infinity,
    center:connected?ids.filter(id=>ecc.get(id)===Math.min(...ecc.values())):[],
    periphery:connected?ids.filter(id=>ecc.get(id)===Math.max(...ecc.values())):[]};
}
function mkStep(msg, b, ex){
  ex = ex || {};
  return {msg, ntext:ex.ntext||b.ntext||null, node:Object.assign({}, b.node, ex.node), edge:Object.assign({}, b.edge, ex.edge), etext:ex.etext||b.etext||null, fill:ex.fill||b.fill||null};
}

/* ---------- analysis ---------- */
function matrixHTML(kind){
  const ids = G.nodes.map(n => n.id), idx = new Map(ids.map((id,i) => [id,i]));
  const A = ids.map(() => ids.map(() => 0)), M = ids.map(() => ids.map(() => null));
  for(const e of G.edges){
    const i = idx.get(e.u), j = idx.get(e.v);
    A[i][j]++; M[i][j] = M[i][j] == null ? e.w : Math.min(M[i][j], e.w);
    if(!G.directed){ A[j][i]++; M[j][i] = M[i][j]; }
  }
  let h = '<div class="tw"><table class="tbl"><tr><th></th>' + ids.map(id => `<th title="${esc(nm(id))}">v${id}</th>`).join('') + '</tr>';
  ids.forEach((id,i) => {
    h += `<tr><th title="${esc(nm(id))}">v${id}</th>` + ids.map((_,j) => {
      if(kind === 'A') return `<td>${A[i][j]}</td>`;
      return `<td>${i===j ? 0 : (M[i][j] == null ? '∞' : fmt(M[i][j]))}</td>`;
    }).join('') + '</tr>';
  });
  return h + '</table></div>';
}
function analysisHTML(){
  const n = G.nodes.length, m = G.edges.length, deg = degreeInfo(), comps = components();
  const sumDeg = G.nodes.reduce((a,x) => a+deg[x.id].deg, 0), neg = G.edges.filter(e => e.w < 0);
  const loops=G.edges.filter(e=>e.u===e.v).length, keys=new Set(),parallel=G.edges.reduce((a,e)=>{
    const k=G.directed?`${e.u}>${e.v}`:`${Math.min(e.u,e.v)}-${Math.max(e.u,e.v)}`;
    if(keys.has(k))return a+1;keys.add(k);return a;
  },0);
  const simple=!loops&&!parallel, maxEdges=G.directed?n*(n-1):n*(n-1)/2;
  const density=maxEdges?m/maxEdges:0, tree=!G.directed&&simple&&n>0&&comps.length===1&&m===n-1;
  const complete=simple&&m===maxEdges, bipartite=isBipartite();
  const degreeSeq=G.nodes.map(x=>deg[x.id].deg).sort((a,b)=>b-a);
  const weightSum=G.edges.reduce((a,e)=>a+e.w,0);
  let h = `<div class="cards">${card('|V| จำนวนจุดยอด', n)}${card('|E| จำนวนเส้นเชื่อม', m)}${card('ชนิดกราฟ', G.directed?'มีทิศทาง →':'ไม่มีทิศทาง —')}${card('Components', comps.length)}</div>`;
  if(!n) return h + '<div class="hero warn">ยังไม่มีจุดยอด ลองกด 📂 ตัวอย่าง หรือ ⬛ เพิ่มจุด</div>';
  h += `<h3>คุณสมบัติ</h3><div class="cards">${card('Simple',simple?'ใช่':'ไม่ใช่')}${card('Self-loop',loops)}${card('เส้นขนานเพิ่มเติม',parallel)}${card('Complete',complete?'ใช่':'ไม่ใช่')}${card('Bipartite',bipartite?'ใช่':'ไม่ใช่')}${card('Tree',tree?'ใช่':'ไม่ใช่')}${card('DAG',isDAG()?'ใช่':'ไม่ใช่')}${card('Strongly Connected',isStronglyConnected()?'ใช่':'ไม่ใช่')}${card('Density',density.toFixed(3))}${card('ผลรวมน้ำหนัก',fmt(weightSum))}</div>`;
  h += `<p><b>Degree Sequence:</b> (${degreeSeq.join(', ')})</p>`;
  const metrics=graphMetrics();
  h += `<h3>ระยะทางและโครงสร้าง</h3><div class="cards">${card('Girth',metrics.girth===Infinity?'ไม่มีวงจร':metrics.girth)}${card('Radius',metrics.connected?fmt(metrics.radius):'กราฟไม่เชื่อมต่อ')}${card('Diameter',metrics.connected?fmt(metrics.diameter):'กราฟไม่เชื่อมต่อ')}${card('Center',metrics.center.map(id=>esc(nm(id))).join(', ') || '—')}${card('Periphery',metrics.periphery.map(id=>esc(nm(id))).join(', ') || '—')}</div>`;
  if(n<=500){
    h += '<div class="tw"><table class="tbl"><tr><th>จุด</th><th>Degree</th><th>Closeness</th><th>Betweenness</th><th>Clustering</th></tr>';
    for(const node of G.nodes)h+=`<tr><td>${esc(nm(node.id))}</td><td>${fmt(metrics.degreeCent.get(node.id))}</td><td>${fmt(metrics.closeness.get(node.id))}</td><td>${fmt(metrics.betweenness.get(node.id)||0)}</td><td>${fmt(metrics.clustering.get(node.id))}</td></tr>`;
    h += '</table></div>';
  }else h += '<p>คำนวณ Centrality เมื่อ |V| ≤ 500</p>';
  h += comps.length <= 1
    ? `<div class="hero">✔ กราฟเชื่อมต่อกัน (Connected)${G.directed?' แบบไม่สนทิศ':''} — Prim จะได้ Spanning Tree เดียว</div>`
    : `<div class="hero warn">⚠ กราฟไม่เชื่อมต่อ มี ${comps.length} ส่วน — Prim จะได้ Spanning Forest และ Flow/Dijkstra อาจไปไม่ถึงบางจุด</div>`;
  h += `<h3>ตรวจ Σdeg = 2|E|</h3><p>Σdeg = ${G.nodes.map(x => deg[x.id].deg).join(' + ')} = <b>${sumDeg}</b> และ 2|E| = 2 × ${m} = <b>${2*m}</b> ${sumDeg===2*m?'✔ ถูกต้อง':'✘'}</p>`;
  if(G.directed) h += `<p>กราฟมีทิศ: Σdeg⁺(ออก) = ${G.nodes.reduce((a,x)=>a+deg[x.id].out,0)} = Σdeg⁻(เข้า) = ${G.nodes.reduce((a,x)=>a+deg[x.id].in,0)} = |E| ✔</p>`;
  h += `<h3>ตรวจน้ำหนักติดลบ</h3>` + (neg.length ? `<div class="hero bad">⚠ พบ ${neg.length} เส้นติดลบ: ${neg.map(e => esc(edgeName(e))).join(', ')} — ห้ามใช้ Dijkstra</div>` : '<p>✔ ไม่มีน้ำหนักติดลบ (Dijkstra ใช้ได้)</p>');
  h += `<h3>Degree ของแต่ละจุด</h3><div class="tw"><table class="tbl"><tr><th>จุด</th><th>ชื่อ</th><th>deg</th>${G.directed?'<th>เข้า (in)</th><th>ออก (out)</th>':''}</tr>`;
  G.nodes.forEach(x => { h += `<tr><td>v${x.id}</td><td class="l">${esc(x.label)}</td><td><b>${deg[x.id].deg}</b></td>${G.directed?`<td>${deg[x.id].in}</td><td>${deg[x.id].out}</td>`:''}</tr>`; });
  h += '</table></div>';
  h += `<h3>Components (${comps.length})</h3>` + comps.map((c,i) => `<div>ส่วนที่ ${i+1}: ${c.map(id => `<span class="chip">${esc(nm(id))}</span>`).join('')}</div>`).join('');
  if(n <= 30){
    h += `<h3>Adjacency Matrix</h3><p style="font-size:13px">แถว = ต้นทาง, คอลัมน์ = ปลายทาง, ตัวเลข = จำนวนเส้น</p>` + matrixHTML('A');
    h += `<h3>Weight Matrix</h3><p style="font-size:13px">∞ = ไม่มีเส้นตรงถึงกัน (ถ้ามีหลายเส้นจะใช้ค่าน้อยสุด)</p>` + matrixHTML('W');
    const ids=G.nodes.map(x=>x.id), adj=outAdj();
    h += '<h3>Adjacency List</h3><div class="tw"><table class="tbl"><tr><th>จุด</th><th class="l">เพื่อนบ้าน (น้ำหนัก)</th></tr>';
    for(const id of ids) h += `<tr><th>${esc(nm(id))}</th><td class="l">${adj.get(id).map(a=>`${esc(nm(a.to))} (${fmt(a.w)})`).join(', ') || '—'}</td></tr>`;
    h += '</table></div>';
    h += '<h3>Incidence Matrix</h3><p style="font-size:13px">คอลัมน์ e = เส้นเชื่อม; loop ในกราฟไม่มีทิศใช้ค่า 2</p><div class="tw"><table class="tbl"><tr><th></th>';
    h += G.edges.map((e,i)=>`<th title="${esc(edgeName(e))}">e${i+1}</th>`).join('')+'</tr>';
    for(const id of ids){
      h += `<tr><th title="${esc(nm(id))}">${esc(nm(id))}</th>`;
      h += G.edges.map(e=>{
        let value=0;
        if(G.directed){if(e.u===id)value--;if(e.v===id)value++;}
        else if(e.u===id&&e.v===id)value=2;
        else if(e.u===id||e.v===id)value=1;
        return `<td>${value}</td>`;
      }).join('')+'</tr>';
    }
    h += '</table></div>';
    const dist=ids.map(()=>ids.map(()=>Infinity));
    ids.forEach((id,i)=>{dist[i][i]=0;const q=[id];while(q.length){const u=q.shift(),ui=ids.indexOf(u);for(const a of adj.get(u))if(dist[i][ids.indexOf(a.to)]===Infinity){dist[i][ids.indexOf(a.to)]=dist[i][ui]+1;q.push(a.to);}}});
    h += '<h3>Distance Matrix (จำนวนเส้น)</h3><div class="tw"><table class="tbl"><tr><th></th>'+ids.map(id=>`<th title="${esc(nm(id))}">${esc(nm(id))}</th>`).join('')+'</tr>';
    ids.forEach((id,i)=>{h+=`<tr><th title="${esc(nm(id))}">${esc(nm(id))}</th>`+dist[i].map(v=>`<td>${v===Infinity?'∞':v}</td>`).join('')+'</tr>';});
    h += '</table></div>';
    const reach=ids.map((_,i)=>dist[i].map(v=>v<Infinity));
    h += '<h3>Reachability Matrix (Transitive Closure)</h3><div class="tw"><table class="tbl"><tr><th></th>'+ids.map(id=>`<th title="${esc(nm(id))}">${esc(nm(id))}</th>`).join('')+'</tr>';
    ids.forEach((id,i)=>{h+=`<tr><th title="${esc(nm(id))}">${esc(nm(id))}</th>`+reach[i].map(v=>`<td>${v?'1':'0'}</td>`).join('')+'</tr>';});
    h += '</table></div>';
  } else h += '<p>(Matrix แสดงเมื่อ |V| ≤ 30)</p>';
  return h;
}
function showAnalysis(){ openModal('🔍 ผลวิเคราะห์กราฟ', analysisHTML()); }

/* ---------- Python algorithm API ---------- */
async function runPythonAlgorithm(algorithm, extra = {}){
  if(!G.nodes.length && algorithm !== 'havelhakimi') return toast('ยังไม่มีจุดยอด');
  try{
    const response = await fetch('/api/run', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({
        algorithm,
        nodes:G.nodes.map(({id,label}) => ({id,label})),
        edges:G.edges.map(({id,u,v,w}) => ({id,u,v,w})),
        directed:G.directed,
        source:G.source,
        sink:G.sink,
        colorNames:G.colorNames,
        ...extra
      })
    });
    const result = await response.json();
    if(!response.ok) throw new Error(result.error || `HTTP ${response.status}`);
    if(result.key==='planarity'){
      if(result.planar===true&&result.planarLayout)preparePlanarityAnimation(result.planarLayout);
      else resetPlanarityAnimation();
    }
    if(result.key === 'pruferDecode' || result.key === 'graphTransform' || (result.key === 'degreeSequence' && result.exists)){
      pushUndo();
      const center = toWorld(W/2, H/2), radius = Math.max(90, result.nodes.length * 18);
      G = emptyGraph();
      G.directed = !!result.directed;
      G.nodes = result.nodes.map((node, index) => {
        const angle = 2*Math.PI*index/result.nodes.length - Math.PI/2;
        return {...node, x:center.x+radius*Math.cos(angle), y:center.y+radius*Math.sin(angle), color:null};
      });
      G.edges = result.edges.map(edge => ({...edge, curve:0, color:null}));
      G.nextId = G.nodes.length + 1;
      G.nextEid = G.edges.length + 1;
      afterChange();
      fitView();
    } else if(result.key === 'color'){
      pushUndo();
      G.nodes.forEach(n => { n.color = result.colors[n.id] ?? null; });
      save();
    } else if(result.key === 'edgeColor'){
      pushUndo();
      G.edges.forEach(edge => { edge.color = result.colors[edge.id] ?? null; });
      save();
    } else if(result.key === 'bipartite' && result.isBipartite){
      pushUndo();
      G.nodes.forEach(node => { node.color = result.colors[node.id] ?? null; });
      save();
    } else if(result.key === 'isomorphism'){
      displayIsomorphismComparison(extra.otherGraph, result);
    }
    setRun({
      key:result.key,
      title:result.title,
      steps:result.key === 'isomorphism' && result.isomorphic ? isomorphismAnimationSteps() :
        result.key === 'planarity' && result.planar === true && result.planarLayout ? planarityAnimationSteps() : result.steps,
      summary:() => result.summary.replace(/\{\{COLOR_NAME_(\d+)\}\}/g, (_, i) => esc(cName(+i))) +
        (result.key === 'isomorphism' && result.isomorphic ? isomorphismMappingSummary() : '')
    });
  }catch(error){
    console.error('Python algorithm request failed:', error);
    toast(`รันอัลกอริทึมไม่สำเร็จ: ${error.message}`);
  }
}
function displayIsomorphismComparison(otherGraph,result){
  isoGraph = JSON.parse(JSON.stringify(otherGraph));
  const nodeCount=isoGraph.nodes.length, radius=Math.min(240,Math.max(90,nodeCount*24));
  isoGraph.nodes=isoGraph.nodes.map((node,index)=>{
    const angle=2*Math.PI*index/nodeCount-Math.PI/2;
    return {...node,x:400+radius*Math.cos(angle),y:300+radius*Math.sin(angle),color:null};
  });
  isoGraph.nextId=Math.max(1,...isoGraph.nodes.map(node=>node.id+1));
  isoGraph.nextEid=Math.max(1,...isoGraph.edges.map(edge=>edge.id+1));
  isoFirstGraph=JSON.parse(JSON.stringify(G));
  isoMapping=result.isomorphic ? result.mapping : null;
  isoColors=[];
  $('#isoMappingLegend').replaceChildren();
  if(isoMapping){
    const leftById=new Map(isoFirstGraph.nodes.map(node=>[String(node.id),node]));
    const rightById=new Map(isoGraph.nodes.map(node=>[String(node.id),node]));
    const colorByLeft=new Map();
    for(const [index,[leftId,rightId]] of Object.entries(isoMapping).entries()){
      const left=leftById.get(String(leftId)),right=rightById.get(String(rightId));
      if(!left||!right) continue;
      const colorIndex=index%PALETTE.length,color=PALETTE[colorIndex];
      left.color=colorIndex;right.color=colorIndex;colorByLeft.set(String(leftId),colorIndex);
      isoColors.push({leftId:String(leftId),rightId:String(rightId),leftLabel:left.label,rightLabel:right.label,color});
    }
    const rightEdgeByPair=new Map();
    const pairKey=(u,v)=>isoGraph.directed?`${u}>${v}`:`${Math.min(u,v)}-${Math.max(u,v)}`;
    isoGraph.edges.forEach(edge=>rightEdgeByPair.set(pairKey(edge.u,edge.v),edge));
    for(const edge of isoFirstGraph.edges){
      const mappedU=isoMapping[String(edge.u)],mappedV=isoMapping[String(edge.v)];
      const matching=rightEdgeByPair.get(pairKey(mappedU,mappedV));
      if(!matching) continue;
      const edgeColor=colorByLeft.get(String(edge.u)) ?? 0;
      edge.color=edgeColor;matching.color=edgeColor;
    }
    $('#isoMappingLegend').innerHTML=isoColors.map(pair=>
      `<span class="iso-pair-chip"><i style="background:${pair.color}"></i>${esc(pair.leftLabel)} → ${esc(pair.rightLabel)}</span>`
    ).join('');
    $('#isoMappingLegend').classList.add('visible');
    $('#isoRightStatus').textContent='Isomorphic ✓ สีเดียวกันแสดงคู่จุดยอดที่ตรงกัน';
  }else{
    $('#isoMappingLegend').classList.remove('visible');
    $('#isoRightStatus').textContent='ไม่ Isomorphic — ไม่พบการจับคู่ที่รักษาเส้นเชื่อม';
  }
  const stageRect=$('#stage').getBoundingClientRect();
  isoView=fitGraphView(isoGraph,Math.max(1,stageRect.width-W),H);
  if(isoMapping){
    const leftById=new Map(isoFirstGraph.nodes.map(node=>[String(node.id),node]));
    isoAnimation={frame:0,initial:new Map(),targets:new Map()};
    for(const node of isoGraph.nodes) isoAnimation.initial.set(String(node.id),{x:node.x,y:node.y});
    for(const pair of isoColors){
      const left=leftById.get(pair.leftId);
      if(!left) continue;
      isoAnimation.targets.set(pair.rightId,{
        x:(view.x+left.x*view.s-isoView.x)/isoView.s,
        y:(view.y+left.y*view.s-isoView.y)/isoView.s
      });
    }
  }else isoAnimation=null;
  draw();
}
function isomorphismAnimationSteps(){
  return [
    {msg:'เริ่มต้น: กราฟที่สองยังอยู่ในตำแหน่งเดิม'},
    ...isoColors.map((pair,index)=>({msg:`ขั้น ${index+1}/${isoColors.length}: จัด ${pair.rightLabel} ให้ตรงกับ ${pair.leftLabel}`}))
  ];
}
function animateIsomorphismTo(index){
  if(!isoAnimation||!isoGraph||algo!=='isomorphism') return;
  if(isoAnimation.frame) cancelAnimationFrame(isoAnimation.frame);
  const matched=new Set(isoColors.slice(0,clamp(index,0,isoColors.length)).map(pair=>pair.rightId));
  const starts=new Map(),destinations=new Map();
  isoGraph.nodes.forEach(node=>{
    const id=String(node.id),target=matched.has(id)?isoAnimation.targets.get(id):isoAnimation.initial.get(id);
    if(target){starts.set(id,{x:node.x,y:node.y});destinations.set(id,target);}
  });
  const startTime=performance.now(),duration=420;
  const frame=now=>{
    if(!isoAnimation) return;
    const progress=clamp((now-startTime)/duration,0,1),eased=1-Math.pow(1-progress,3);
    isoGraph.nodes.forEach(node=>{
      const id=String(node.id),from=starts.get(id),to=destinations.get(id);
      if(from&&to){node.x=from.x+(to.x-from.x)*eased;node.y=from.y+(to.y-from.y)*eased;}
    });
    draw();
    if(progress<1) isoAnimation.frame=requestAnimationFrame(frame);
    else isoAnimation.frame=0;
  };
  isoAnimation.frame=requestAnimationFrame(frame);
}
function invalidateIsomorphismResult(){
  if(!isoFirstGraph&&!isoMapping&&!isoColors.length)return;
  clearRun();
  if(isoAnimation&&isoAnimation.frame) cancelAnimationFrame(isoAnimation.frame);
  isoAnimation=null;
  isoFirstGraph=null;isoMapping=null;isoColors=[];
  if(isoGraph){
    isoGraph.nodes.forEach(node=>{if(node.color!=null)node.color=null;});
    isoGraph.edges.forEach(edge=>{if(edge.color!=null)edge.color=null;});
  }
  const legend=$('#isoMappingLegend');
  if(legend){legend.replaceChildren();legend.classList.remove('visible');}
  const status=$('#isoRightStatus');
  if(status)status.textContent=`กราฟที่สองมี ${isoGraph?isoGraph.nodes.length:0} จุด • ${isoGraph?isoGraph.edges.length:0} เส้น — แก้ไขได้ด้วยเครื่องมือด้านบน`;
}
function isomorphismMappingSummary(){
  if(!isoColors.length) return '';
  const rows=isoColors.map(pair=>
    `<tr><td><span class="sw" style="background:${pair.color}"></span>${esc(pair.leftLabel)}</td><td>→</td><td><span class="sw" style="background:${pair.color}"></span>${esc(pair.rightLabel)}</td></tr>`
  ).join('');
  return `<h3>จุดยอดที่จับคู่กัน</h3><div class="tw"><table class="tbl"><tr><th>กราฟที่ 1</th><th></th><th>กราฟที่ 2</th></tr>${rows}</table></div>`;
}
function runDijkstra(){ return runPythonAlgorithm('dijkstra'); }
function runPrim(){ return runPythonAlgorithm('prim'); }
function runKruskal(){ return runPythonAlgorithm('kruskal'); }
function runEuler(){ return runPythonAlgorithm('euler'); }
function runEdgeColoring(){ return runPythonAlgorithm('edgecolor'); }
function runColoring(){ return runPythonAlgorithm('color'); }
function runFlow(){ return runPythonAlgorithm('flow'); }
function runHamiltonian(){ return runPythonAlgorithm('hamiltonian'); }
function runPlanarity(){ return runPythonAlgorithm('planarity'); }
function runVertexConnectivity(){ return runPythonAlgorithm('vertexconnectivity'); }
function runEdgeConnectivity(){ return runPythonAlgorithm('edgeconnectivity'); }
function showDegreeSequenceInput(){
  openModal('📊 Degree Sequence', `
    <p>ใส่ Degree ของแต่ละจุดยอด คั่นด้วยช่องว่างหรือจุลภาค เช่น <b>3, 2, 2, 1</b></p>
    <label>Degree Sequence
      <input id="degreeSequenceInput" type="text" inputmode="numeric" autocomplete="off" placeholder="เช่น 3, 2, 2, 1">
    </label>
    <p><button type="button" class="btn primary" id="buildDegreeSequence">ตรวจสอบและสร้างกราฟ</button></p>
    <p class="note">ใช้ Havel–Hakimi และ Erdős–Gallai ตรวจว่าลำดับนี้สร้างเป็นกราฟอย่างง่ายได้หรือไม่ (1–500 จุดยอด)</p>`);
  $('#degreeSequenceInput').focus();
}
function runDegreeSequenceFromInput(){
  const raw = $('#degreeSequenceInput').value.trim();
  if(!raw) return toast('กรุณาใส่ Degree Sequence');
  const tokens = raw.split(/[,\s]+/);
  if(tokens.some(token => !/^\d+$/.test(token))) return toast('Degree ต้องเป็นจำนวนเต็มไม่ติดลบ คั่นด้วยช่องว่างหรือจุลภาค');
  const degreeSequence = tokens.map(Number);
  if(degreeSequence.some(value => !Number.isSafeInteger(value))) return toast('มี Degree ที่มีค่ามากเกินไป');
  closeModal();
  return runPythonAlgorithm('havelhakimi', {degreeSequence});
}
function runComplement(){ return runPythonAlgorithm('transform', {operation:'complement'}); }
function runBipartite(){ return runPythonAlgorithm('bipartite'); }
function showIsomorphismInput(){
  const presetOptions = Object.entries(PRESETS)
    .map(([key, preset]) => `<option value="${key}">${esc(preset.name)}</option>`).join('');
  const drawnOption=isoGraph&&isoGraph.nodes.length?`<option value="drawn" selected>ใช้กราฟที่วาดไว้ทางขวา (${isoGraph.nodes.length} จุด, ${isoGraph.edges.length} เส้น)</option>`:'';
  openModal('🔁 Isomorphic Graphs', `<p>สร้างหรือแก้กราฟได้ทั้งสองฝั่ง แล้วเลือกเปรียบเทียบกราฟที่วาดไว้ทางขวา หรือนำเข้าตัวอย่าง/Edge List</p>
    <div class="row"><label class="sel">กราฟที่สอง<select id="isoPreset">${drawnOption}<option value="custom" ${drawnOption?'':'selected'}>กำหนดด้วย Edge List</option>${presetOptions}</select></label></div>
    <div class="row"><label class="sel">จำนวนจุดยอดของกราฟที่สอง <input id="isoNodeCount" type="number" min="1" max="12" value="${Math.max(1, G.nodes.length)}"></label></div>
    <label>Edge List <textarea id="isoEdges" rows="3" placeholder="${G.directed ? 'ตัวอย่างกราฟมีทิศทาง: 1&gt;2, 2&gt;3' : 'ตัวอย่างกราฟไม่มีทิศทาง: 1-2, 2-3'}"></textarea></label>
    <label><input id="isoDirected" type="checkbox" ${G.directed ? 'checked' : ''}> กราฟที่สองมีทิศทาง</label>
    <p class="note">เปรียบเทียบโครงสร้างโดยไม่สนชื่อจุดยอดหรือน้ำหนัก รองรับกราฟอย่างง่ายไม่เกิน 12 จุดยอด (ไม่มี self-loop/เส้นขนาน)</p>
    <p><button type="button" class="btn primary" id="runIsomorphismCompare">เปรียบเทียบกราฟ</button></p>`);
}
function runIsomorphismComparison(){
  let otherGraph;
  const presetKey = $('#isoPreset').value;
  if(presetKey==='drawn'){
    if(!isoGraph||!isoGraph.nodes.length)return toast('เพิ่มจุดยอดทางฝั่งขวาก่อนเปรียบเทียบ');
    otherGraph={
      nodes:isoGraph.nodes.map(({id,label})=>({id,label})),
      edges:isoGraph.edges.map(({id,u,v,w})=>({id,u,v,w})),
      directed:isoGraph.directed
    };
  }else if(presetKey !== 'custom'){
    const preset = PRESETS[presetKey];
    if(!preset) return toast('ไม่พบตัวอย่างกราฟที่เลือก');
    const graph = preset.build();
    otherGraph = {
      nodes:graph.nodes.map(({id,label}) => ({id,label})),
      edges:graph.edges.map(({id,u,v,w}) => ({id,u,v,w})),
      directed:graph.directed
    };
  }else{
    const count = Number($('#isoNodeCount').value), directed = $('#isoDirected').checked;
    if(!Number.isInteger(count) || count < 1 || count > 12) return toast('กราฟที่สองต้องมี 1–12 จุดยอด');
    const raw = $('#isoEdges').value.trim();
    const pairs = raw ? raw.split(/[;,\n]+/).map(item => item.trim()) : [];
    const edges = [], seen = new Set();
    for(const pair of pairs){
      const match = directed ? pair.match(/^(\d+)\s*(?:>|→)\s*(\d+)$/) : pair.match(/^(\d+)\s*-\s*(\d+)$/);
      if(!match) return toast(`รูปแบบ Edge List ไม่ถูกต้อง: ${pair}`);
      const u = Number(match[1]), v = Number(match[2]);
      if(u < 1 || u > count || v < 1 || v > count || u === v) return toast(`เส้น ${pair} ต้องเชื่อมจุด 1–${count} และห้ามเป็น self-loop`);
      const key = directed ? `${u}>${v}` : `${Math.min(u,v)}-${Math.max(u,v)}`;
      if(seen.has(key)) return toast(`พบเส้นซ้ำ: ${pair}`);
      seen.add(key); edges.push({id:edges.length+1,u,v,w:1});
    }
    otherGraph = {
      nodes:Array.from({length:count},(_,index)=>({id:index+1,label:`v${index+1}`})),
      edges,
      directed
    };
    isoGraph=sanitize({
      nodes:otherGraph.nodes.map(node=>({...node,x:100+((node.id-1)%4)*90,y:100+Math.floor((node.id-1)/4)*90,color:null})),
      edges:otherGraph.edges.map(edge=>({...edge,color:null,curve:0})),
      directed,nextId:count+1,nextEid:edges.length+1
    });
  }
  closeModal();
  return runPythonAlgorithm('isomorphism', {otherGraph});
}

/* ---------- player ---------- */
function setRun(r){
  stop(); run = r; stepIdx = 0; updatePlayer(); draw();
  toast(`พร้อมแล้ว ${r.steps.length} ขั้น — กด ▶ เพื่อเล่น หรือ ▶| ทีละขั้น`);
}
function resetPlanarityAnimation(restore=false){
  if(!planarityAnimation)return;
  if(planarityAnimation.frame)cancelAnimationFrame(planarityAnimation.frame);
  if(restore){
    const targets=planarityAnimation.targets;
    G.nodes.forEach(node=>{const point=targets.get(String(node.id));if(point){node.x=point.x;node.y=point.y;}});
    save();
  }
  planarityAnimation=null;
}
function preparePlanarityAnimation(layout){
  resetPlanarityAnimation();
  const points=G.nodes.map(node=>({id:String(node.id),point:layout[String(node.id)]})).filter(item=>Array.isArray(item.point)&&item.point.length===2);
  if(!points.length)return;
  const xs=points.map(item=>item.point[0]),ys=points.map(item=>item.point[1]);
  const minX=Math.min(...xs),maxX=Math.max(...xs),minY=Math.min(...ys),maxY=Math.max(...ys);
  const worldWidth=W/view.s,worldHeight=H/view.s,padding=64;
  const scale=Math.min((worldWidth-2*padding)/Math.max(1,maxX-minX),(worldHeight-2*padding)/Math.max(1,maxY-minY));
  const centerX=(W/2-view.x)/view.s,centerY=(H/2-view.y)/view.s;
  const layoutCenterX=(minX+maxX)/2,layoutCenterY=(minY+maxY)/2;
  planarityAnimation={frame:0,initial:new Map(),targets:new Map()};
  G.nodes.forEach(node=>planarityAnimation.initial.set(String(node.id),{x:node.x,y:node.y}));
  for(const item of points){
    planarityAnimation.targets.set(item.id,{
      x:centerX+(item.point[0]-layoutCenterX)*scale,
      y:centerY+(item.point[1]-layoutCenterY)*scale
    });
  }
}
function planarityAnimationSteps(){
  return [
    {msg:'เริ่มต้น: แสดงกราฟในตำแหน่งปัจจุบัน'},
    ...[25,50,75,100].map(percent=>({msg:`จัดตำแหน่งตาม planar embedding — ${percent}%`}))
  ];
}
function animatePlanarityTo(index){
  if(!planarityAnimation||!run||run.key!=='planarity')return;
  if(planarityAnimation.frame)cancelAnimationFrame(planarityAnimation.frame);
  const fraction=clamp(index/Math.max(1,run.steps.length-1),0,1),starts=new Map(),destinations=new Map();
  G.nodes.forEach(node=>{
    const id=String(node.id),initial=planarityAnimation.initial.get(id),target=planarityAnimation.targets.get(id);
    if(initial&&target){
      starts.set(id,{x:node.x,y:node.y});
      destinations.set(id,{x:initial.x+(target.x-initial.x)*fraction,y:initial.y+(target.y-initial.y)*fraction});
    }
  });
  const startTime=performance.now(),duration=500;
  const frame=now=>{
    if(!planarityAnimation)return;
    const progress=clamp((now-startTime)/duration,0,1),eased=1-Math.pow(1-progress,3);
    G.nodes.forEach(node=>{
      const from=starts.get(String(node.id)),to=destinations.get(String(node.id));
      if(from&&to){node.x=from.x+(to.x-from.x)*eased;node.y=from.y+(to.y-from.y)*eased;}
    });
    draw();
    if(progress<1)planarityAnimation.frame=requestAnimationFrame(frame);
    else{planarityAnimation.frame=0;if(fraction===1)save();}
  };
  planarityAnimation.frame=requestAnimationFrame(frame);
}
function clearRun(){ stop(); resetPlanarityAnimation(true); run = null; stepIdx = 0; updatePlayer(); }
function go(i){ if(!run) return; stepIdx = clamp(i, 0, run.steps.length-1); if(run.key==='isomorphism') animateIsomorphismTo(stepIdx); if(run.key==='planarity') animatePlanarityTo(stepIdx); updatePlayer(); draw(); }
function stop(){ playing = false; clearTimeout(timer); const b = $('#bPlay'); if(b) b.textContent = '▶'; }
function play(){
  if(!run) return toast('กด "เริ่มรัน" ก่อน');
  if(playing) return stop();
  if(stepIdx >= run.steps.length-1) go(0);
  playing = true; $('#bPlay').textContent = '⏸'; tick();
}
function tick(){
  clearTimeout(timer);
  timer = setTimeout(() => {
    if(!playing || !run) return;
    if(stepIdx < run.steps.length-1){
      go(stepIdx+1);
      if(stepIdx >= run.steps.length-1){ stop(); setTimeout(showSummary, 600); } else tick();
    } else stop();
  }, 1200/speed);
}
function manual(fn){ stop(); fn(); }
function updatePlayer(){
  const n = run ? run.steps.length : 0, sl = $('#slider');
  sl.max = Math.max(0, n-1); sl.value = stepIdx;
  $('#stepLbl').textContent = n ? `ขั้น ${stepIdx+1}/${n}` : 'ขั้น 0/0';
  $('#stepText').textContent = run ? run.steps[stepIdx].msg : defaultStepText();
  $('#sumBtn').classList.toggle('glow', !!run && stepIdx === n-1);
}
function defaultStepText(){
  const T = TABS[algo];
  if(algo === 'color') return '👉 กด "▶ เริ่มรัน" เพื่อระบายสีแบบ Welsh–Powell';
  return `👉 ${T.s ? 'เลือก ' + T.s.replace(/^\S+\s/, '') + (T.t ? ' และ ' + T.t.replace(/^\S+\s/, '') : '') + ' แล้ว' : ''}กด "▶ เริ่มรัน"`;
}
function showSummary(){
  if(algo === 'analyze') return showAnalysis();
  if(!run) return toast('กด "เริ่มรัน" ก่อน แล้วค่อยดูสรุปผล');
  openModal(run.title, run.summary());
}

/* ---------- tabs ---------- */
const TABS = {
  analyze:{icon:'🔍', name:'วิเคราะห์', desc:'ดูภาพรวมของกราฟ: |V|, |E|, Degree, Σdeg = 2|E|, Connected/Components, ตรวจน้ำหนักติดลบ, Adjacency & Weight Matrix', s:null, t:null, run:() => showAnalysis()},
  dijkstra:{icon:'🛣️', name:'Dijkstra', desc:'หาเส้นทางสั้นที่สุดจากต้นทางไปทุกจุด โดยใช้น้ำหนักเป็นระยะทางหรือค่าขนส่ง', app:'เส้นทางขนส่งที่สั้น/ถูกที่สุด', s:'🚩 ต้นทาง', t:'🏁 ปลายทาง', run:runDijkstra},
  prim:{icon:'🌳', name:'Prim (MST)', desc:'สร้าง Spanning Tree ที่น้ำหนักรวมน้อยที่สุด โดยเพิ่มเส้นที่ถูกที่สุดทีละเส้น', app:'วางถนน/ท่อ/สายไฟให้ต้นทุนรวมต่ำสุด', s:'🚩 จุดเริ่ม', t:null, run:runPrim},
  kruskal:{icon:'🌲', name:'Kruskal (MST)', desc:'เลือกเส้นน้ำหนักน้อยที่สุดทีละเส้น โดยข้ามเส้นที่จะทำให้เกิดวงจร และแสดง Spanning Forest เมื่อกราฟไม่เชื่อมต่อ', s:null, t:null, run:runKruskal},
  euler:{icon:'🔁', name:'Euler Path/Circuit', desc:'ตรวจเงื่อนไข degree และใช้ Hierholzer หาเส้นทางที่ผ่านทุกเส้นครั้งเดียว รองรับกราฟมีทิศและเส้นขนาน', s:null, t:null, run:runEuler},
  bipartite:{icon:'◐', name:'Bipartite Graph', desc:'ตรวจว่าสามารถแบ่งจุดยอดเป็นสองฝั่งโดยทุกเส้นเชื่อมข้ามฝั่งหรือไม่ พร้อมแสดง partition และระบายสีจุดยอด', s:null, t:null, run:runBipartite},
  isomorphism:{icon:'🔁', name:'Isomorphic Graphs', desc:'เปรียบเทียบกราฟปัจจุบันกับอีกกราฟ แล้วแสดง mapping ของจุดยอดเมื่อมีโครงสร้างเหมือนกัน (กราฟอย่างง่ายไม่เกิน 12 จุด)', s:null, t:null, run:showIsomorphismInput},
  hamiltonian:{icon:'🧭', name:'Hamiltonian Path / Cycle', desc:'ค้นหา Hamiltonian Path และ Hamiltonian Cycle ด้วย Backtracking (ไม่เกิน 15 จุด) พร้อมเงื่อนไข Dirac/Ore', s:null, t:null, run:runHamiltonian},
  planarity:{icon:'📐', name:'Planarity / Kuratowski', desc:'ตรวจเกณฑ์ Euler และค้นหา K₅ / K₃,₃ minors ด้วยการลบจุดและหดเส้น (exact สูงสุด 10 จุดยอด; อาจรายงานว่าสรุปไม่ได้เมื่อค้นหาเกินขีดจำกัด)', s:null, t:null, run:runPlanarity},
  vertexconnectivity:{icon:'🔗', name:'Vertex Connectivity κ(G)', desc:'คำนวณจำนวนจุดยอดน้อยที่สุดที่ต้องตัดให้กราฟไม่เชื่อมต่อ พร้อมระบุชื่อจุดที่ต้องตัด', s:null, t:null, run:runVertexConnectivity},
  edgeconnectivity:{icon:'✂️', name:'Edge Connectivity λ(G)', desc:'คำนวณจำนวนเส้นเชื่อมน้อยที่สุดที่ต้องตัดให้กราฟไม่เชื่อมต่อ พร้อมระบุเส้นที่ต้องตัด', s:null, t:null, run:runEdgeConnectivity},
  degreeSequence:{icon:'🧮', name:'Degree Sequence', desc:'ตรวจด้วย Havel–Hakimi / Erdős–Gallai และสร้างกราฟอย่างง่ายจากลำดับ Degree ที่เป็นไปได้', s:null, t:null, run:showDegreeSequenceInput},
  complement:{icon:'◐', name:'Complement', desc:'สร้างกราฟเติมเต็ม โดยเชื่อมคู่จุดยอดที่ยังไม่มีเส้นเชื่อม (กราฟไม่มีทิศทางและไม่มีเส้นซ้ำ/loop)', s:null, t:null, run:runComplement},
  edgeColor:{icon:'🎨', name:'Edge Coloring', desc:'ระบายสีเส้นแบบ Greedy โดยเส้นที่มีจุดร่วมต้องคนละสี; สีแบบอัตโนมัติเป็นค่าประมาณ', s:null, t:null, run:runEdgeColoring},
  color:{icon:'🎨', name:'Vertex Coloring χ(G)', desc:'ระบายสีจุดแบบ Welsh–Powell พร้อมคำนวณ Chromatic Number แบบ Exact เมื่อมีไม่เกิน 15 จุด; ใช้กับตารางสอบ/แข่งขัน', app:'จุดที่เชื่อมกันต้องใช้สี/ช่วงเวลาต่างกัน; กราฟเชิงระนาบใช้ไม่เกิน 4 สีตามทฤษฎีบทสี่สี', s:null, t:null, run:runColoring},
  flow:{icon:'🚰', name:'Max Flow', desc:'Edmonds–Karp: หา Augmenting Path ด้วย BFS ซ้ำจนไหลเพิ่มไม่ได้ ใช้น้ำหนักเป็นความจุ (Capacity) ควรใช้กราฟแบบมีทิศ', app:'ปริมาณสินค้า/การจราจรสูงสุด และจุดคอขวด', s:'🟢 Source', t:'🔴 Sink', run:runFlow}
};
const LEGENDS = {
  analyze:'',
  dijkstra:'<span class="lg"><i style="background:#d7263d"></i>จุดปัจจุบัน</span><span class="lg"><i style="background:#3a86ff"></i>จุดที่กำลัง Relax</span><span class="lg"><i class="ln" style="background:#ef7d57"></i>เส้นที่กำลังตรวจ</span><span class="lg"><i style="background:#2a9d8f"></i>ปิดแล้ว</span><span class="lg"><i class="ln" style="background:#38b764"></i>เส้นทางสั้นสุด</span><span class="lg">🟨 ตัวเลขเหนือจุด = ระยะ</span>',
  kruskal:'<span class="lg"><i class="ln" style="background:#38b764"></i>เส้นใน Spanning Tree/Forest</span><span class="lg"><i class="ln" style="background:#94b0c2"></i>ข้ามเพราะเกิดวงจร</span>',
  euler:'<span class="lg"><i class="ln" style="background:#38b764"></i>เส้นทาง Euler</span>',
  bipartite:'<span class="lg"><i style="background:#ef7d57"></i>ฝั่งที่ 1</span><span class="lg"><i style="background:#41a6f6"></i>ฝั่งที่ 2</span>',
  isomorphism:'',
  hamiltonian:'<span class="lg"><i class="ln" style="background:#38b764"></i>Path/Cycle ที่ผ่านทุกจุดหนึ่งครั้ง</span>',
  planarity:'<span class="lg">K₅ หรือ K₃,₃ minor → ไม่เป็นกราฟเชิงระนาบ</span><span class="lg">กราฟเชิงระนาบต้องใช้ไม่เกิน 4 สี</span>',
  vertexconnectivity:'<span class="lg"><i style="background:#ef7d57"></i>จุดยอดที่ต้องตัด</span>',
  edgeconnectivity:'<span class="lg"><i class="dash"></i>เส้นเชื่อมที่ต้องตัด</span>',
  degreeSequence:'',
  complement:'',
  edgeColor:'<span class="lg">สีของเส้น = กลุ่มเส้นที่ไม่มีจุดร่วมกัน</span>',
  prim:'<span class="lg"><i class="ln" style="background:#ef7d57"></i>เส้นตัวเลือก</span><span class="lg"><i class="ln" style="background:#38b764"></i>อยู่ในต้นไม้</span><span class="lg"><i style="background:#2a9d8f"></i>จุดในต้นไม้</span>',
  color:'<span class="lg"><i style="background:#fff;border-color:#b13e53;border-width:4px"></i>จุดที่กำลังพิจารณา</span><span class="lg"><i class="ln" style="background:#ef7d57"></i>เส้นขัดแย้ง</span><span class="lg">สีของจุด = กลุ่ม (ช่วงเวลา/ช่องเก็บ)</span>',
  flow:'<span class="lg">ตัวเลข f/c = flow/ความจุ</span><span class="lg"><i class="ln" style="background:#3b5dc9"></i>มี flow</span><span class="lg"><i class="ln" style="background:#5d275d"></i>เต็ม</span><span class="lg"><i class="dash"></i>คอขวด (Min Cut)</span><span class="lg"><i style="background:#8338ec"></i>ฝั่ง S</span>'
};
function setTab(key){
  algo = TABS[key] ? key : 'dijkstra'; const T = TABS[algo];
  setIsomorphismSplit(algo === 'isomorphism');
  if(algo !== 'isomorphism'){
    isoGraph=null;isoFirstGraph=null;isoMapping=null;isoColors=[];
    isoSelNode=null;isoEdgePreview=null;lastActiveSide='left';
    $('#isoMappingLegend').replaceChildren();
    $('#isoMappingLegend').classList.remove('visible');
    $('#isoRightStatus').textContent='เลือก Isomorphic Graphs แล้วเริ่มเปรียบเทียบเพื่อแสดงกราฟที่สอง';
  }else{
    $('#isoRightStatus').textContent=isoGraph
      ? `กราฟที่สองมี ${isoGraph.nodes.length} จุด • ${isoGraph.edges.length} เส้น — ใช้เครื่องมือด้านบนแก้ไขได้`
      : 'เลือกเครื่องมือเพิ่มจุด/เชื่อมเส้น แล้วสร้างกราฟที่สองทางฝั่งขวา';
  }
  clearRun();
  $$('#tabs .btn').forEach(b => b.classList.toggle('on', b.dataset.tab === algo));
  $('#algoDesc').innerHTML = `<b>${T.icon} ${T.name}</b> — ${T.desc}` + (T.app ? `<span class="app">💡 การประยุกต์: ${T.app}</span>` : '');
  $('#lblS').style.display = T.s ? '' : 'none'; $('#lblT').style.display = T.t ? '' : 'none';
  $('#selRow').style.display = (T.s || T.t) ? '' : 'none';
  if(T.s) $('#lblSText').textContent = T.s; if(T.t) $('#lblTText').textContent = T.t;
  $('#runBtn').textContent = algo === 'analyze' ? '🔍 เปิดผลวิเคราะห์' : `▶ เริ่มรัน ${T.name}`;
  $('#player').style.display = algo === 'analyze' ? 'none' : '';
  $('#legend').innerHTML = LEGENDS[algo];
  updatePlayer(); save(); draw();
}
function refreshSelects(){
  for(const [sel, key] of [[$('#selS'), 'source'], [$('#selT'), 'sink']]){
    sel.innerHTML = '<option value="">— เลือกจุด —</option>' + G.nodes.map(n => `<option value="${n.id}">${esc(n.label)}${n.label !== 'v'+n.id ? ' (v'+n.id+')' : ''}</option>`).join('');
    sel.value = G[key] == null ? '' : String(G[key]);
  }
}
function updateBadge(){
  const comps = G.nodes.length ? components().length : 0;
  $('#badge').textContent = `|V| ${G.nodes.length} · |E| ${G.edges.length} · ${G.directed ? 'มีทิศ →' : 'ไม่มีทิศ —'}`;
  const controlGraph=lastActiveSide==='right'&&isoSplitView&&isoGraph?isoGraph:G;
  $('#dirIc').textContent = controlGraph.directed ? '→' : '—';
  $('#dirTxt').textContent = controlGraph.directed ? 'มีทิศ' : 'ไม่มีทิศ';
  $('#quick').textContent = `|V| = ${G.nodes.length} • |E| = ${G.edges.length} • ` + (comps <= 1 ? 'Connected ✔' : `⚠ ไม่ Connected (${comps} ส่วน)`) + ` • Undo ได้ ${undoStack.length} ขั้น`;
}
const HINTS = {
  move:'✋ ลากจุดเพื่อย้าย • ลากพื้นที่ว่างเพื่อเลื่อนจอ • แตะ 2 ครั้งที่จุด/เส้นเพื่อแก้ไข • ล้อเมาส์/บีบ 2 นิ้ว = ซูม',
  node:'⬛ แตะพื้นที่ว่างเพื่อเพิ่มจุดยอด (ลากจุดเดิมเพื่อย้ายได้)',
  edge:'🔗 แตะจุดแรก แล้วแตะจุดที่สอง เพื่อสร้างเส้นและใส่น้ำหนัก',
  edit:'✏️ แตะจุดเพื่อตั้งชื่อ (เช่น คลังสินค้า) • แตะเส้นเพื่อเปลี่ยนน้ำหนัก',
  bend:'〰️ ลากที่เส้นเพื่อดัดให้โค้ง • แตะเส้นเพื่อทำให้ตรง',
  del:'🗑️ แตะจุดหรือเส้นที่ต้องการลบ (กด Undo ได้)',
  edgeColor:'🎨 แตะเส้นที่ต้องการเปลี่ยนสี'
};
function updateHint(){
  let h = HINTS[tool];
  const useRight=lastActiveSide==='right'&&isoSplitView;
  const currentGraph=useRight?isoGraph:G, selected=useRight?isoSelNode:selNode;
  if(tool === 'edge' && selected != null && currentGraph){
    const node=currentGraph.nodes.find(item=>item.id===selected);
    if(node)h=`🔗 เลือก "${node.label}" แล้ว → แตะจุดปลายทาง (แตะจุดเดิมเพื่อสร้าง self-loop, แตะที่ว่างเพื่อยกเลิก)`;
  }
  $('#hint').textContent = h;
  const toolNames = {move:'ย้าย/เลื่อน',node:'เพิ่มจุด',edge:'เชื่อมเส้น',edit:'แก้ชื่อ/น้ำหนัก',bend:'ดัดเส้น',del:'ลบ',edgeColor:'ระบายสีเส้น'};
  $('#toolStatus').textContent = `โหมด: ${toolNames[tool] || tool} · ${(currentGraph||G).directed ? 'Directed' : 'Undirected'}${isoSplitView?` · แก้ไข: กราฟที่ ${useRight?'2':'1'}`:''} · Ctrl/⌘+Z Undo · 1–7 เปลี่ยนโหมด`;
}

/* ---------- presets ---------- */
function mk(directed, nodes, edges, opt){
  const g = emptyGraph(); g.directed = directed;
  nodes.forEach(([x,y,l], i) => g.nodes.push({id:i+1, x, y, label:l, color:null}));
  g.nextId = nodes.length+1;
  edges.forEach(([u,v,w,c]) => g.edges.push({id:g.nextEid++, u, v, w, curve:c||0}));
  return Object.assign(g, opt || {});
}
const PRESETS = {
  transport:{name:'🚚 โครงข่ายขนส่ง', tab:'dijkstra', desc:'หาเส้นทางส่งสินค้าจากคลังไปลูกค้าที่สั้นที่สุด (หน่วย: กม.)', build:() => mk(false,
    [[80,250,'คลังสินค้า'],[250,110,'ศูนย์กระจาย A'],[250,390,'ศูนย์กระจาย B'],[420,250,'จุดพักรถ'],[590,110,'ร้านค้า 1'],[590,390,'ร้านค้า 2'],[760,250,'ลูกค้า']],
    [[1,2,7],[1,3,9],[2,3,10],[2,4,15],[3,4,11],[2,5,20],[4,5,6],[4,6,9],[3,6,21],[5,7,8],[6,7,5]], {source:1, sink:7})},
  city:{name:'🏙️ แผนที่เมือง/โครงสร้างพื้นฐาน', tab:'prim', desc:'วางสายไฟ/ท่อประปาให้ทุกสถานที่เชื่อมกันด้วยต้นทุนต่ำสุด (ล้านบาท)', build:() => mk(false,
    [[100,100,'โรงไฟฟ้า'],[340,60,'โรงพยาบาล'],[580,110,'โรงเรียน'],[200,280,'ตลาด'],[430,260,'ศาลากลาง'],[680,290,'หมู่บ้าน A'],[120,460,'หมู่บ้าน B'],[390,460,'นิคมอุตสาหกรรม'],[640,480,'สถานีรถไฟ']],
    [[1,2,4],[1,4,3],[2,4,5],[2,5,6],[2,3,8],[3,5,7],[3,6,4],[4,5,2],[4,7,6],[5,8,5],[5,6,9],[7,8,7],[8,9,3],[6,9,5],[5,9,8],[4,8,9]], {source:1})},
  exam:{name:'📝 ตารางสอบ/ช่องเก็บสินค้า', tab:'color', desc:'วิชาที่เชื่อมกัน = มีนักเรียนสอบซ้อน ต้องอยู่คนละช่วงเวลา (สี = ช่วงเวลาสอบ)', build:() => {
    const names = ['คณิตศาสตร์','ฟิสิกส์','เคมี','ชีววิทยา','ภาษาอังกฤษ','ภาษาไทย','สังคมศึกษา','คอมพิวเตอร์'];
    const nodes = names.map((l,i) => { const a = (-90+i*45)*Math.PI/180; return [Math.round(400+230*Math.cos(a)), Math.round(300+230*Math.sin(a)), l]; });
    return mk(false, nodes, [[1,2,1],[1,3,1],[1,8,1],[1,7,1],[2,3,1],[2,8,1],[2,4,1],[3,4,1],[4,5,1],[5,6,1],[5,8,1],[6,7,1],[3,8,1]],
      {colorNames:['จันทร์ 09:00','จันทร์ 13:00','อังคาร 09:00','อังคาร 13:00','พุธ 09:00','พุธ 13:00']});
  }},
  k33:{name:'🧩 ปัญหา Utility (K₃,₃)', tab:'bipartite', desc:'บ้าน 3 หลังและสาธารณูปโภค 3 แห่ง: ตรวจการแบ่งสองฝั่งของกราฟสมบูรณ์ K₃,₃', build:() => mk(false,
    [[170,130,'บ้าน 1'],[170,300,'บ้าน 2'],[170,470,'บ้าน 3'],[620,130,'น้ำ'],[620,300,'ไฟฟ้า'],[620,470,'ก๊าซ']],
    Array.from({length:9},(_,i)=>[Math.floor(i/3)+1,4+i%3,1]))},
  koenigsberg:{name:'🌉 สะพานทั้ง 7 แห่งของเคอนิกส์แบร์ก', tab:'euler', desc:'กราฟประวัติศาสตร์ 4 พื้นที่ 7 สะพาน มีจุดยอดดีกรีคี่ 4 จุด จึงไม่มี Euler Path', build:() => mk(false,
    [[130,150,'ฝั่งเหนือ'],[130,450,'ฝั่งใต้'],[440,170,'เกาะ Kneiphof'],[440,430,'เกาะ Lomse']],
    [[1,3,1,-0.3],[1,3,1,0.3],[2,3,1,-0.3],[2,3,1,0.3],[1,4,1,0],[2,4,1,0],[3,4,1,0.12]])},
  pipe:{name:'🚰 โครงข่ายท่อ/ถนน', tab:'flow', desc:'ส่งสินค้าจากโรงงานไปตลาดกลางได้มากที่สุดกี่หน่วย/ชม. และคอขวดอยู่ที่ไหน', build:() => mk(true,
    [[80,260,'โรงงาน'],[280,110,'คลัง A'],[280,410,'คลัง B'],[520,110,'ศูนย์ C'],[520,410,'ศูนย์ D'],[720,260,'ตลาดกลาง']],
    [[1,2,16],[1,3,13],[3,2,4],[2,4,12],[4,3,9],[3,5,14],[5,4,7],[4,6,20],[5,6,4]], {source:1, sink:6})}
};
function showGenerator(){
  openModal('🧩 ตัวสร้างกราฟ', `<p>สร้างกราฟใหม่ (กด Undo เพื่อกลับกราฟเดิม)</p>
    <div class="row"><label class="sel">ชนิดกราฟ<select id="genType">
      <option value="complete">กราฟสมบูรณ์ Kₙ</option><option value="cycle">วงจร Cₙ</option>
      <option value="path">เส้นทาง Pₙ</option><option value="star">ดาว Star</option>
      <option value="bipartite">สองส่วน Kₘ,ₙ</option><option value="grid">Grid</option>
      <option value="hypercube">Hypercube Qₙ</option><option value="random">สุ่ม G(n,p)</option>
      <option value="tree">ต้นไม้สุ่ม</option><option value="dag">DAG สุ่ม</option>
      <option value="petersen">Petersen</option></select></label></div>
    <div class="row"><label class="sel">จำนวนจุด n <input id="genN" type="number" min="1" max="60" value="8"></label>
      <label class="sel">m (Kₘ,ₙ) / แถว <input id="genM" type="number" min="1" max="60" value="4"></label></div>
    <div class="row"><label class="sel">ความน่าจะเป็น p (0–1) <input id="genP" type="number" min="0" max="1" step="0.05" value="0.3"></label></div>
    <button type="button" class="btn primary" id="buildGraph">สร้างกราฟ</button>
    <p class="note">กราฟสมบูรณ์จำกัด n ≤ 40 และจำนวนจุดสูงสุด 60 เพื่อให้แอปตอบสนองได้ดี</p>`);
}
function buildGeneratedGraph(){
  const type = $('#genType').value, n = Number($('#genN').value), m = Number($('#genM').value), p = Number($('#genP').value);
  if(type === 'petersen'){
    const es = [];
    for(let i=0;i<5;i++){ es.push([i+1,(i+1)%5+1,1],[i+6,(i+1)%5+6,1],[i+1,i+6,1]); }
    const ns=Array.from({length:10},(_,i)=>{const a=2*Math.PI*i/10-Math.PI/2;return [400+230*Math.cos(a),300+230*Math.sin(a),`v${i+1}`];});
    return mk(false, ns, es);
  }
  if(!Number.isInteger(n) || n < 1 || n > 60) throw new Error('จำนวนจุดต้องเป็นจำนวนเต็ม 1–60');
  if(!Number.isInteger(m) || m < 1 || m > 60) throw new Error('ค่า m ต้องเป็นจำนวนเต็ม 1–60');
  if(!Number.isFinite(p) || p < 0 || p > 1) throw new Error('p ต้องอยู่ระหว่าง 0 ถึง 1');
  if(type === 'complete' && n > 40) throw new Error('Kₙ จำกัด n ≤ 40 เพื่อไม่ให้มีเส้นมากเกินไป');
  if(type === 'hypercube' && n > 6) throw new Error('Qₙ จำกัด n ≤ 6 (สูงสุด 64 จุด)');
  const count = type === 'bipartite' ? n + m : type === 'hypercube' ? 2 ** n : n;
  if(count > 60) throw new Error('กราฟนี้มีจุดเกินขีดจำกัด 60 จุด');
  const nodes = Array.from({length:count},(_,i)=>{
    const a = 2*Math.PI*i/count - Math.PI/2, r = Math.min(260, 48*count);
    return [400+r*Math.cos(a), 300+r*Math.sin(a), `v${i+1}`];
  });
  const edges = [];
  const add = (u,v) => edges.push([u+1,v+1,1]);
  if(type === 'complete'){
    for(let i=0;i<n;i++) for(let j=i+1;j<n;j++) add(i,j);
  } else if(type === 'cycle'){
    if(n < 3) throw new Error('วงจร Cₙ ต้องมี n ≥ 3');
    for(let i=0;i<n;i++) add(i,(i+1)%n);
  } else if(type === 'path'){
    for(let i=0;i<n-1;i++) add(i,i+1);
  } else if(type === 'star'){
    for(let i=1;i<n;i++) add(0,i);
  } else if(type === 'bipartite'){
    for(let i=0;i<n;i++) for(let j=0;j<m;j++) add(i,n+j);
  } else if(type === 'grid'){
    const rows = Math.max(1, Math.floor(Math.sqrt(n))), cols = Math.ceil(n/rows);
    for(let i=0;i<n;i++){ if(i%cols && i-1>=0) add(i-1,i); if(i-cols>=0) add(i-cols,i); }
    nodes.forEach((v,i)=>{ v[0]=100+(i%cols)*100; v[1]=100+Math.floor(i/cols)*100; });
  } else if(type === 'hypercube'){
    for(let i=0;i<count;i++) for(let b=0;b<n;b++){ const j=i^(1<<b); if(i<j) add(i,j); }
    nodes.forEach((v,i)=>{ v[2]=i.toString(2).padStart(n,'0'); });
  } else if(type === 'tree'){
    for(let i=1;i<n;i++) add(i,Math.floor(Math.random()*i));
  } else if(type === 'random' || type === 'dag'){
    for(let i=0;i<n;i++) for(let j=i+1;j<n;j++) if(Math.random()<p) add(i,j);
  }
  if(edges.length > 1500) throw new Error('กราฟมีเส้นเกิน 1,500 เส้น');
  return mk(type === 'dag', nodes, edges);
}
function showLayouts(){
  const items = [['circular','วงกลม'],['grid','ตาราง'],['force','Force-directed'],
    ['hierarchical','ลำดับชั้น'],['bipartite','สองคอลัมน์']];
  openModal('🪄 จัดวางอัตโนมัติ', '<p>จัดตำแหน่งจุดใหม่โดยไม่เปลี่ยนเส้นเชื่อม</p><div class="row">' +
    items.map(([key,label])=>`<button type="button" class="btn" data-layout="${key}">${label}</button>`).join('') + '</div>');
}
function applyLayout(kind){
  const nodes = G.nodes, n = nodes.length;
  if(!n) return toast('ยังไม่มีจุดยอด');
  const positions = new Map();
  if(kind === 'circular'){
    nodes.forEach((v,i)=>{ const a=2*Math.PI*i/n-Math.PI/2; positions.set(v.id,{x:400+Math.min(280,48*n)*Math.cos(a),y:300+Math.min(280,48*n)*Math.sin(a)}); });
  } else if(kind === 'grid'){
    const cols=Math.ceil(Math.sqrt(n));
    nodes.forEach((v,i)=>positions.set(v.id,{x:120+(i%cols)*100,y:100+Math.floor(i/cols)*100}));
  } else if(kind === 'bipartite'){
    const split=Math.ceil(n/2), left=nodes.slice(0,split), right=nodes.slice(split);
    left.forEach((v,i)=>positions.set(v.id,{x:180,y:100+i*500/Math.max(1,left.length-1)}));
    right.forEach((v,i)=>positions.set(v.id,{x:620,y:100+i*500/Math.max(1,right.length-1)}));
  } else if(kind === 'hierarchical'){
    const levels=new Map(nodes.map((v,i)=>[v.id,0]));
    for(let pass=0;pass<n;pass++) for(const e of G.edges) if(levels.has(e.u)&&levels.has(e.v))
      levels.set(e.v,Math.max(levels.get(e.v),levels.get(e.u)+1));
    const max=Math.max(0,...levels.values()), groups=new Map();
    nodes.forEach(v=>{const l=levels.get(v.id);if(!groups.has(l))groups.set(l,[]);groups.get(l).push(v);});
    for(const [l,group] of groups) group.forEach((v,i)=>positions.set(v.id,{x:100+(i+1)*600/(group.length+1),y:70+l*450/Math.max(1,max)}));
  } else {
    const pos=nodes.map(v=>({x:v.x,y:v.y}));
    for(let step=0;step<60;step++){
      const dx=Array(n).fill(0),dy=Array(n).fill(0);
      for(let i=0;i<n;i++) for(let j=i+1;j<n;j++){
        let x=pos[i].x-pos[j].x,y=pos[i].y-pos[j].y,d=Math.hypot(x,y)||1,f=1800/(d*d);
        dx[i]+=x/d*f;dy[i]+=y/d*f;dx[j]-=x/d*f;dy[j]-=y/d*f;
      }
      for(const e of G.edges){const i=nodes.findIndex(v=>v.id===e.u),j=nodes.findIndex(v=>v.id===e.v);if(i<0||j<0||i===j)continue;
        const x=pos[j].x-pos[i].x,y=pos[j].y-pos[i].y,d=Math.hypot(x,y)||1,f=d*d/500;
        dx[i]+=x/d*f;dy[i]+=y/d*f;dx[j]-=x/d*f;dy[j]-=y/d*f;
      }
      const temp=12*(1-step/60);
      pos.forEach((v,i)=>{v.x+=clamp(dx[i],-temp,temp);v.y+=clamp(dy[i],-temp,temp);});
    }
    nodes.forEach((v,i)=>positions.set(v.id,pos[i]));
  }
  commit(()=>nodes.forEach(v=>Object.assign(v,positions.get(v.id))),false);
  closeModal();fitView();toast('จัดวางกราฟแล้ว');
}
function searchNode(){
  const q=$('#nodeSearch').value.trim().toLocaleLowerCase();
  const n=G.nodes.find(v=>String(v.id)===q.replace(/^v/,'')||v.label.toLocaleLowerCase()===q);
  if(!n) return toast('ไม่พบจุดยอดที่ค้นหา');
  view.s=1.35;view.x=W/2-n.x*view.s;view.y=H/2-n.y*view.s;draw();toast(`พบ ${n.label}`);
}
function runQuickCommand(){
  const input=$('#quickCommand'), match=input.value.match(/^\s*(.+?)\s*-\s*(.+?)\s*:\s*(-?(?:\d+\.?\d*|\.\d+))\s*$/);
  if(!match) return toast('รูปแบบคำสั่งไม่ถูกต้อง ตัวอย่าง: v1-v2:5');
  const find=q=>G.nodes.find(v=>String(v.id)===q.replace(/^v/i,'')||v.label.toLocaleLowerCase()===q.toLocaleLowerCase());
  const u=find(match[1].trim()),v=find(match[2].trim()),w=Number(match[3]);
  if(!u||!v||!Number.isFinite(w)) return toast('ไม่พบจุดยอด หรือค่าน้ำหนักไม่ถูกต้อง');
  commit(()=>storeEdge(u.id,v.id,w));input.value='';toast(`เพิ่มเส้น ${u.label} ${G.directed?'→':'–'} ${v.label} = ${fmt(w)}`);
}
function showPresets(){
  openModal('📂 ตัวอย่างสาธิต', `<p>เลือกตัวอย่าง (กราฟปัจจุบันจะถูกแทนที่ แต่กด Undo กลับได้)</p><div class="pgrid">` +
    Object.entries(PRESETS).map(([k,p]) => `<div class="pcard"><b>${p.name}</b><span style="font-size:14px">${p.desc}</span><span style="font-size:13px">อัลกอริทึม: <b>${TABS[p.tab].name}</b></span><button type="button" class="btn primary" data-preset="${k}">เปิดตัวอย่างนี้</button></div>`).join('') + '</div>');
}
function loadPreset(k){
  const p = PRESETS[k]; if(!p) return;
  pushUndo(); G = p.build(); selNode = null; closeModal(); setTab(p.tab); afterChange(); fitView();
  toast(`โหลด "${p.name}" แล้ว → กด ▶ เริ่มรัน`);
}

/* ---------- export PNG ---------- */
function exportPNG(){
  if(!G.nodes.length) return toast('ยังไม่มีจุดยอดให้ส่งออก');
  let x0=Infinity, y0=Infinity, x1=-Infinity, y1=-Infinity;
  G.nodes.forEach(n => { x0=Math.min(x0,n.x); y0=Math.min(y0,n.y); x1=Math.max(x1,n.x); y1=Math.max(y1,n.y); });
  G.edges.forEach(e => { const g = edgeGeom(e); if(g){ x0=Math.min(x0,g.px); y0=Math.min(y0,g.py); x1=Math.max(x1,g.px); y1=Math.max(y1,g.py); } });
  x0 -= 100; x1 += 100; y0 -= 70; y1 += 70;
  const FOOT = 46, SC = 2, w = Math.ceil(x1-x0), h = Math.ceil(y1-y0)+FOOT;
  const oc = document.createElement('canvas'); oc.width = w*SC; oc.height = h*SC;
  const c = oc.getContext('2d'); c.scale(SC, SC);
  renderScene(c, w, h-FOOT, {x:-x0, y:-y0, s:1});
  c.fillStyle = INK; c.fillRect(0, h-FOOT, w, FOOT);
  c.fillStyle = '#ffcd75'; c.font = `bold 16px ${FONT}`; c.textAlign = 'left'; c.textBaseline = 'middle';
  c.fillText(`GRAPH THEORY LAB   |V| = ${G.nodes.length}   |E| = ${G.edges.length}   ${G.directed?'Directed':'Undirected'}${run ? '   • '+TABS[run.key].name : ''}`, 14, h-FOOT/2);
  const url = oc.toDataURL('image/png');
  openModal('🖼️ ส่งออก PNG', `<p>ขนาด ${w*SC} × ${h*SC} px (Scale 2) พร้อม |V| = ${G.nodes.length}, |E| = ${G.edges.length}</p>
    <a class="btn primary" download="graph-lab.png" href="${url}">⬇ ดาวน์โหลด PNG</a>
    <div class="note">📱 <b>iPhone/iPad หรือดาวน์โหลดไม่ได้:</b> กดค้างที่ภาพด้านล่าง แล้วเลือก "บันทึกลงในรูปภาพ" (Save to Photos)</div>
    <img src="${url}" class="preview" alt="graph">`);
  if(!IOS){ try{ const a = document.createElement('a'); a.href = url; a.download = 'graph-lab.png'; document.body.appendChild(a); a.click(); a.remove(); }catch(_){} }
}

/* ---------- help ---------- */
function showHelp(){
  openModal('❓ วิธีใช้ Graph Theory Lab', `<div class="hero">👋 ยินดีต้อนรับ! ทดลองอัลกอริทึมกราฟสำหรับงานขนส่งและผังเมือง</div>
  <h3>เริ่มใน 3 ขั้น</h3>
  <ol class="steps">
    <li><b>สร้างกราฟ</b> — กด ⬛ เพิ่มจุด แล้วแตะพื้นที่ว่าง → กด 🔗 เชื่อมเส้น แล้วแตะ 2 จุด (หรือกด 📂 ตัวอย่าง)</li>
    <li><b>เลือกอัลกอริทึม</b> ที่แท็บในแผงควบคุม (ด้านล่างบนมือถือ / ด้านขวาบนคอม) แล้วเลือกต้นทาง-ปลายทาง</li>
    <li><b>กด ▶ เริ่มรัน</b> แล้วดูทีละขั้นด้วย ⏮ ◀ ▶ ▶| ⏭ จากนั้นกด 📊 สรุปผล</li>
  </ol>
  <h3>เครื่องมือ</h3>
  <div class="tw"><table class="tbl">
    <tr><td>✋</td><td class="l">ลากจุด / เลื่อนจอ / แตะ 2 ครั้งเพื่อแก้ไข</td></tr>
    <tr><td>⬛</td><td class="l">เพิ่มจุดยอด</td></tr>
    <tr><td>🔗</td><td class="l">สร้างเส้น รวม self-loop, เส้นขนาน และน้ำหนักติดลบ</td></tr>
    <tr><td>✏️</td><td class="l">ตั้งชื่อจุด (เช่น คลังสินค้า) / แก้น้ำหนักเส้น</td></tr>
    <tr><td>〰️</td><td class="l">ดัดเส้นให้โค้ง / แตะเพื่อให้ตรง</td></tr>
    <tr><td>🗑️</td><td class="l">ลบจุดหรือเส้น</td></tr>
    <tr><td>⇄</td><td class="l">สลับกราฟมีทิศ / ไม่มีทิศ</td></tr>
    <tr><td>⌖</td><td class="l">จัดกราฟให้อยู่กึ่งกลางจอ</td></tr>
  </table></div>
  <div class="note">🔁 โหมด Isomorphic Graphs: ใช้เครื่องมือชุดเดียวกันสร้าง/แก้กราฟได้ทั้งฝั่งซ้ายและขวา (เลือกฝั่งด้วยการแตะหรือลากบนกราฟ) แล้วกดเริ่มรันและเลือก “ใช้กราฟที่วาดไว้ทางขวา” เพื่อเปรียบเทียบ</div>
  <h3>ทางลัด</h3>
  <p>Ctrl/⌘+Z = Undo • Ctrl/⌘+Y หรือ Ctrl/⌘+Shift+Z = Redo (ประมาณ 70 ขั้น) • 1–6 = เลือกโหมด • G = สร้างกราฟ • L = จัดวาง • F = จัดกึ่งกลาง • ← → = ย้อน/ถัดไป • Space = เล่น/หยุด • ล้อเมาส์หรือบีบ 2 นิ้ว = ซูม</p>
  <div class="note">🧩 สร้างกราฟ Kₙ, Cₙ, Pₙ, Star, Kₘ,ₙ, Grid, Qₙ, G(n,p), Random Tree, DAG และ Petersen • ตัวอย่างมี K₃,₃ และปัญหาสะพานทั้ง 7 ของเคอนิกส์แบร์ก • ค้นหาจุดยอดหรือพิมพ์คำสั่งเช่น v1-v2:-2</div>
  <div class="note">💾 ระบบบันทึกอัตโนมัติในเบราว์เซอร์ (localStorage): จุด เส้น น้ำหนัก ทิศทาง ชื่อ สี และ Source/Sink</div>
  <p><button type="button" class="btn primary" id="helpPreset">📂 เปิดตัวอย่างสาธิต</button></p>`);
}

/* ---------- bind UI ---------- */
function init(){
  $('#tabs').innerHTML = Object.entries(TABS).map(([k,T]) => `<button type="button" class="btn tab" data-tab="${k}">${T.icon} ${T.name}</button>`).join('');
  $('#tabs').addEventListener('click', e => { const b = e.target.closest('[data-tab]'); if(b) setTab(b.dataset.tab); });
  $('#toolbar').addEventListener('click', e => {
    const b = e.target.closest('[data-tool]'); if(!b) return;
    tool=b.dataset.tool;selNode=null;edgePreview=null;isoSelNode=null;isoEdgePreview=null;
    $$('[data-tool]').forEach(x => x.classList.toggle('on', x === b));
    updateCanvasCursor(); updateHint(); draw();
  });
  $('#aDir').onclick = () => {
    withLastCanvasSide(()=>commit(()=>{G.directed=!G.directed;}));
    updateBadge();updateHint();
    const directed=lastActiveSide==='right'&&isoSplitView&&isoGraph?isoGraph.directed:G.directed;
    toast(directed?'→ เปลี่ยนเป็นกราฟมีทิศทาง':'— เปลี่ยนเป็นกราฟไม่มีทิศทาง');
  };
  $('#aUndo').onclick = undo;
  $('#aRedo').onclick = redo;
  $('#aStraight').onclick = () => withLastCanvasSide(()=>{
    if(!G.edges.some(e=>e.curve))return toast('เส้นตรงอยู่แล้วทั้งหมด');
    commit(()=>G.edges.forEach(e=>e.curve=0),false);toast('📏 รีเซ็ตเป็นเส้นตรงแล้ว');
  });
  $('#aPreset').onclick = showPresets;
  $('#aGenerate').onclick = showGenerator;
  $('#aLayout').onclick = showLayouts;
  $('#searchNode').onclick = () => withLastCanvasSide(searchNode);
  $('#nodeSearch').addEventListener('keydown',e=>{if(e.key==='Enter')withLastCanvasSide(searchNode);});
  $('#runCommand').onclick = () => withLastCanvasSide(runQuickCommand);
  $('#quickCommand').addEventListener('keydown',e=>{if(e.key==='Enter')withLastCanvasSide(runQuickCommand);});
  $('#aPNG').onclick = exportPNG;
  $('#aClear').onclick = () => withLastCanvasSide(()=>{
    if(!G.nodes.length)return;
    if(confirm('ล้างกราฟทั้งหมด? (กด Undo กลับได้)')){
      const directed=G.directed;commit(()=>{G=emptyGraph();G.directed=directed;});
      selNode=null;edgePreview=null;
    }
  });
  $('#aHelp').onclick = showHelp;
  $('#zIn').onclick = () => withLastCanvasSide(()=>zoomAt(W/2,H/2,1.25));
  $('#zOut').onclick = () => withLastCanvasSide(()=>zoomAt(W/2,H/2,0.8));
  $('#zFit').onclick = fitView;
  $('#selS').onchange = e => { G.source = e.target.value === '' ? null : +e.target.value; clearRun(); save(); draw(); };
  $('#selT').onchange = e => { G.sink = e.target.value === '' ? null : +e.target.value; clearRun(); save(); draw(); };
  $('#runBtn').onclick = () => TABS[algo].run();
  $('#bFirst').onclick = () => manual(() => go(0));
  $('#bPrev').onclick = () => manual(() => go(stepIdx-1));
  $('#bPlay').onclick = play;
  $('#bNext').onclick = () => manual(() => go(stepIdx+1));
  $('#bLast').onclick = () => manual(() => go(run ? run.steps.length-1 : 0));
  $('#slider').oninput = e => manual(() => go(+e.target.value));
  $$('[data-sp]').forEach(b => b.onclick = () => { speed = +b.dataset.sp; $$('[data-sp]').forEach(x => x.classList.toggle('on', x === b)); if(playing) tick(); });
  $('#sumBtn').onclick = showSummary;
  $('#clearRunBtn').onclick = () => {
    if(G.nodes.some(n => n.color != null)){ pushUndo(); G.nodes.forEach(n => n.color = null); }
    clearRun(); afterChange(); toast('ล้างผลแล้ว');
  };
  $('#dockToggle').onclick = () => { const d = $('#dock'); d.classList.toggle('collapsed'); $('#dockToggle').textContent = d.classList.contains('collapsed') ? '▴' : '▾'; };
  $('#mclose').onclick = closeModal;
  $('#modal').addEventListener('click', e => { if(e.target.id === 'modal') closeModal(); });
  $('#mbody').addEventListener('click', e => {
    const p = e.target.closest('[data-preset]'); if(p) return loadPreset(p.dataset.preset);
    if(e.target.closest('#buildDegreeSequence')) return runDegreeSequenceFromInput();
    if(e.target.closest('#runIsomorphismCompare')) return runIsomorphismComparison();
    if(e.target.closest('#buildGraph')){
      try{pushUndo();G=buildGeneratedGraph();selNode=null;clearRun();afterChange();closeModal();fitView();setTab('analyze');toast('สร้างกราฟสำเร็จ');}
      catch(error){toast(`สร้างกราฟไม่ได้: ${error.message}`);}
      return;
    }
    const layout=e.target.closest('[data-layout]');if(layout)return withLastCanvasSide(()=>applyLayout(layout.dataset.layout));
    if(e.target.closest('#helpPreset')) return showPresets();
    const edgeColor=e.target.closest('[data-edge-color]');
    if(edgeColor){
      const edgeId=Number($('#mbody').dataset.edgeId),side=$('#mbody').dataset.edgeSide||'left';
      const color=Number(edgeColor.dataset.edgeColor);
      withCanvasSide(side,()=>{
        const edge=G.edges.find(item=>item.id===edgeId);
        if(!edge)return toast('ไม่พบเส้นที่เลือก');
        commit(()=>{edge.color=color<0?null:color;},false);
      });
      closeModal();toast(color<0?'ล้างสีเส้นแล้ว':`เปลี่ยนสีเส้นเป็นสี ${color+1} แล้ว`);return;
    }
    const cn = e.target.closest('[data-cname]');
    if(cn){
      const i = +cn.dataset.cname;
      const s = prompt('ตั้งชื่อความหมายของสีนี้ (เช่น จันทร์ 09:00, ช่องเก็บ A):', cName(i));
      if(s !== null){ G.colorNames[i] = s.trim() || `สี ${i+1}`; save(); if(run && run.key === 'color') $('#mbody').innerHTML = run.summary(); }
    }
  });
  $('#mbody').addEventListener('keydown', e => {
    if(e.target.id === 'degreeSequenceInput' && e.key === 'Enter'){
      e.preventDefault();
      runDegreeSequenceFromInput();
    }
  });
  window.addEventListener('keydown', e => {
    const tg = e.target.tagName; if(tg === 'INPUT' || tg === 'SELECT' || tg === 'TEXTAREA') return;
    if((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'z'){ e.preventDefault(); if(e.shiftKey) redo(); else undo(); }
    else if((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'y'){ e.preventDefault(); redo(); }
    else if(e.key === 'Escape') closeModal();
    else if(e.key.toLowerCase() === 'g') showGenerator();
    else if(e.key.toLowerCase() === 'l') showLayouts();
    else if(e.key.toLowerCase() === 'f') fitView();
    else if(/^[1-7]$/.test(e.key)){
      const tools=['move','node','edge','edit','bend','del','edgeColor'], key=tools[Number(e.key)-1];
      const button=$(`[data-tool="${key}"]`);
      if(button){tool=key;selNode=null;edgePreview=null;$$('[data-tool]').forEach(x=>x.classList.toggle('on',x===button));updateCanvasCursor();updateHint();draw();}
    }
    else if(e.key === 'ArrowRight') manual(() => go(stepIdx+1));
    else if(e.key === 'ArrowLeft') manual(() => go(stepIdx-1));
    else if(e.key === ' '){ e.preventDefault(); play(); }
  });

  const savedTab = load();
  if(!savedTab) G = PRESETS.transport.build();
  if('ResizeObserver' in window) new ResizeObserver(() => resize()).observe($('#stage'));
  else window.addEventListener('resize', resize);
  resize();
  setTab(savedTab || 'dijkstra');
  afterChange();
  if(!savedTab){ fitView(); setTimeout(showHelp, 300); }
}
if(document.fonts && document.fonts.ready) document.fonts.ready.then(() => draw());
if('serviceWorker' in navigator && location.protocol !== 'file:'){
  navigator.serviceWorker.register('/service-worker.js').catch(error => console.error('PWA service worker registration failed:', error));
}
init();
})();
</script>
</body>
</html>
"""

PORT_START = 8765


def lan_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return
        assets = {
            "/head.png": ("head.png", "image/png"),
            "/mascot_clean.png": ("mascot_clean.png", "image/png"),
            "/web.png": ("web.png", "image/png"),
            "/service-worker.js": ("service-worker.js", "text/javascript; charset=utf-8"),
            "/manifest.webmanifest": ("manifest.webmanifest", "application/manifest+json; charset=utf-8"),
        }
        if self.path in assets:
            filename, content_type = assets[self.path]
            asset = Path(__file__).with_name(filename)
            try:
                body = asset.read_bytes()
            except OSError:
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            cache_control = "no-cache" if filename == "service-worker.js" else "public, max-age=3600"
            self.send_header("Cache-Control", cache_control)
            self.end_headers()
            self.wfile.write(body)
            return
        body = HTML.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path != "/api/run":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0 or length > 2_000_000:
            self.send_error(413, "ข้อมูลกราฟไม่ถูกต้องหรือมีขนาดใหญ่เกินไป")
            return
        try:
            payload = json.loads(self.rfile.read(length))
            if not isinstance(payload, dict):
                raise ValueError("ข้อมูลคำขอไม่ถูกต้อง")
            result = run_algorithm(payload)
        except (ValueError, UnicodeDecodeError) as error:
            body = json.dumps({"error": str(error)}, ensure_ascii=False).encode("utf-8")
            self.send_response(400)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        body = json.dumps(result, ensure_ascii=False, allow_nan=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass  # ปิด log เพื่อให้ Terminal สะอาด


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    # สร้างไฟล์ HTML ไว้ข้าง ๆ เพื่อเปิดแบบออฟไลน์ได้
    out = Path(__file__).with_name("graph_lab.html")
    try:
        out.write_text(HTML, encoding="utf-8")
    except OSError:
        out = None

    httpd = None
    port = PORT_START
    for p in range(PORT_START, PORT_START + 40):
        try:
            httpd = http.server.ThreadingHTTPServer(("0.0.0.0", p), Handler)
            port = p
            break
        except OSError:
            continue

    if httpd is None:
        print("เปิดเซิร์ฟเวอร์ไม่ได้ → เปิดไฟล์ HTML สำรอง (การรันอัลกอริทึมต้องใช้ Python server)")
        if out:
            webbrowser.open(out.as_uri())
        return

    url = f"http://localhost:{port}"
    print("=" * 56)
    print("  GRAPH THEORY LAB  (Logistics & Urban Planning)")
    print("=" * 56)
    print(f"  คอมพิวเตอร์นี้ : {url}")
    print(f"  มือถือ/แท็บเล็ต : http://{lan_ip()}:{port}  (Wi-Fi เดียวกัน)")
    if out:
        print(f"  ไฟล์ออฟไลน์    : {out}")
    print("  กด Ctrl+C เพื่อปิดโปรแกรม")
    print("=" * 56)

    threading.Timer(0.7, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nปิดเซิร์ฟเวอร์แล้ว")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()
