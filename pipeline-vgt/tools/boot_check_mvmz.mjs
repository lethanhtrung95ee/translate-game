// Khoi dong thu ban Viet hoa RPG Maker MV/MZ trong Edge/Chrome headless. KHONG chep game, KHONG ghi vao game:
// may chu HTTP noi bo tra file tu patch\files truoc, thieu thi lay tu game goc.
// Nap ban luu that cua game (www/save/*.rpgsave -> localStorage) de giong may nguoi choi
// (vd ngon ngu da chon = EN), roi thu tung ngon ngu trong --langs.
// Dat: toi Scene_Title, font nap duoc, khong loi JS, chu hien ra la tieng Viet (khong con chu goc).
//
// Dung: node tools/boot_check_mvmz.mjs <thu muc game goc> [--patch "../<Ten game>"]
//         [--langs ",EN,JP,CH"] [--lang-key language] [--expr "<JS tra ve chuoi UI can kiem>"] [--secs 60]
//         [--measure] [--report do_khung.json] [--shots <thu muc anh>] [--samples "Map006.json:ev4p0,..."]
// --measure (tang 1, 0 token): do MOI dong thoai (401) bang chinh font + khung thoai cua game
//   (Window_Base.drawTextEx/textSizeEx, xu ly ma \C \N \V \I); tran khung hoac qua so dong -> KHONG DAT.
// --shots (tang 3): chup man hinh tieu de + khung thoai mau (dong rong nhat, canh trong --samples) ra PNG
//   de AI/nguoi xem. Trinh duyet khac Edge/Chrome: dat bien moi truong VGT_BROWSER.
// Thoat 0 = dat het; 1 = co loi. Bat buoc chay sau moi lan apply, truoc khi bao "xong" (G-011).
import { spawn, execSync } from 'node:child_process';
import { createServer } from 'node:http';
import { existsSync, mkdirSync, mkdtempSync, readFileSync, readdirSync, rmSync, statSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { extname, join, normalize, resolve } from 'node:path';

const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf(k); return i >= 0 ? argv.splice(i, 2)[1] : d; };
const patchDir = opt('--patch', '');
const langs = opt('--langs', null);
const langKey = opt('--lang-key', 'language');
const extra = opt('--expr', '');
const secs = Number(opt('--secs', '60'));
const measure = argv.includes('--measure') ? (argv.splice(argv.indexOf('--measure'), 1), true) : false;
const reportFile = opt('--report', '');
const shotsDir = opt('--shots', '');
const samples = (opt('--samples', '') || '').split(',').map(x => x.trim()).filter(Boolean);
if (!argv[0]) { console.error('Dung: node tools/boot_check_mvmz.mjs <game goc> [--patch <dir>] [--langs ",EN"]'); process.exit(2); }
const game = resolve(argv[0]);
const overlay = patchDir ? join(resolve(patchDir), '_viethoa', 'files') : null;
if (overlay && !existsSync(overlay)) { console.error('Khong thay ' + overlay); process.exit(2); }
const www = existsSync(join(game, 'www', 'index.html')) ? 'www' : '';
if (!existsSync(join(game, www, 'index.html'))) { console.error('Khong thay index.html trong ' + game); process.exit(2); }
const browser = [process.env.VGT_BROWSER, 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
  'C:/Program Files/Google/Chrome/Application/chrome.exe'].filter(Boolean).find(existsSync);
if (!browser) { console.error('Khong thay Edge/Chrome'); process.exit(2); }

// ---- may chu: patch truoc, game goc sau (chi doc) ----
const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.css': 'text/css',
  '.png': 'image/png', '.ttf': 'font/ttf', '.otf': 'font/otf', '.woff': 'font/woff', '.ogg': 'audio/ogg',
  '.m4a': 'audio/mp4', '.webm': 'video/webm', '.mp4': 'video/mp4' };
const pick = rel => {
  for (const base of [overlay, game]) {
    if (!base) continue;
    const f = normalize(join(base, rel));
    if (f.startsWith(base) && existsSync(f) && statSync(f).isFile()) return f;
  }
  return null;
};
const server = createServer((req, res) => {
  const rel = decodeURIComponent(new URL(req.url, 'http://x').pathname).replace(/^\/+/, '');
  const f = pick(rel);
  if (!f) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': MIME[extname(f).toLowerCase()] || 'application/octet-stream' });
  res.end(readFileSync(f));
});
await new Promise(r => server.listen(0, '127.0.0.1', r));
const base = `http://127.0.0.1:${server.address().port}/`;

// ---- ban luu that -> localStorage (StorageManager.webStorageKey: config/global/file<X>) ----
const saveDir = join(game, www, 'save');
const store = {};
if (existsSync(saveDir)) for (const n of readdirSync(saveDir)) {
  const m = n.match(/^(config|global|file(.+))\.rpgsave$/);
  if (!m) continue;
  const key = m[1] === 'config' ? 'RPG Config' : m[1] === 'global' ? 'RPG Global' : 'RPG File' + m[2];
  store[key] = readFileSync(join(saveDir, n), 'utf8');
}
const lzFile = pick(join(www, 'js', 'libs', 'lz-string.js'));
const LZ = lzFile ? new Function(readFileSync(lzFile, 'utf8') + ';return LZString')() : null;
const runs = langs === null ? [null] : langs.split(',');

// ---- hop thoai (101 + cac dong 401) tu data da patch: de do khung ----
function collectBoxes() {
  const dataRel = join(www, 'data');
  const boxes = [];
  const scan = (list, grp) => {
    for (let i = 0; i < (list || []).length; i++) {
      if (list[i].code !== 101) continue;
      const lines = [];
      for (let j = i + 1; j < list.length && list[j].code === 401; j++) lines.push(String(list[j].parameters[0] ?? ''));
      if (lines.some(l => l.trim())) boxes.push({ grp, i, face: list[i].parameters[0] || '', lines });
    }
  };
  for (const n of readdirSync(join(game, dataRel)).sort()) {
    if (!/^(Map\d+|CommonEvents|Troops)\.json$/.test(n)) continue;
    const doc = JSON.parse(readFileSync(pick(join(dataRel, n)), 'utf8').replace(/^\uFEFF/, ''));
    if (n.startsWith('Map')) for (const ev of doc.events || []) { if (ev) (ev.pages || []).forEach((p, k) => scan(p.list, `${n}:ev${ev.id}p${k}`)); }
    else if (n === 'CommonEvents.json') for (const ce of doc) { if (ce) scan(ce.list, `${n}:ce${ce.id}`); }
    else for (const tr of doc) { if (tr) (tr.pages || []).forEach((p, k) => scan(p.list, `${n}:tr${tr.id}p${k}`)); }
  }
  return boxes;
}
// Ham chay trong trang: do bang chinh engine cua game (MV: drawTextEx, MZ: textSizeEx)
const MEASURE_FN = `window.__vgtWin=window.__vgtWin||(()=>{const MZ=Utils.RPGMAKER_NAME==='MZ';
 const h=Graphics.boxHeight/3;let mw=null;try{mw=MZ?null:new Window_Message();}catch(e){}
 const w=MZ?new Window_Base(new Rectangle(0,0,Graphics.boxWidth,h)):new Window_Base(0,0,(mw&&mw.width)||Graphics.boxWidth,h);
 const rows=(mw&&mw.numVisibleRows&&mw.numVisibleRows())||4;
 const faceW=MZ?(ImageManager.faceWidth+20):168;
 const width=t=>{if(MZ)return w.textSizeEx(t).width;w.contents.clear();return w.drawTextEx(t,0,0);};
 return {w,rows,faceW,width,avail:w.contentsWidth?w.contentsWidth():w.width-w.standardPadding()*2};})();
window.__vgtMeasure=boxes=>{const W=window.__vgtWin,bad=[];let n=0;
 for(const b of boxes){const lim=W.avail-(b.face?W.faceW:0);
  if(b.lines.length>W.rows)bad.push({grp:b.grp,i:b.i,kind:'qua_dong',n:b.lines.length,max:W.rows,text:b.lines.join(' / ')});
  for(const l of b.lines){n++;let px=0;try{px=W.width(l);}catch(e){px=-1;}
   if(px>lim)bad.push({grp:b.grp,i:b.i,kind:'tran',px:Math.round(px),max:lim,text:l});}}
 return JSON.stringify({n,bad,avail:W.avail,rows:W.rows});};`;

// ---- trinh duyet ----
const port = 9300 + Math.floor(Math.random() * 600);
const profile = mkdtempSync(join(tmpdir(), 'vgt_boot_'));  // khong dung chuoi '\\' tu go (de sai)
const proc = spawn(browser, ['--headless=new', `--remote-debugging-port=${port}`, `--user-data-dir=${profile}`,
  '--autoplay-policy=no-user-gesture-required', '--mute-audio',
  ...(process.platform !== 'win32' && process.getuid?.() === 0 ? ['--no-sandbox'] : []), 'about:blank']);
const sleep = ms => new Promise(r => setTimeout(r, ms));
let ws, id = 0; const pend = {}; let errors = [];
const send = (method, params = {}) => new Promise(r => {
  const i = ++id; pend[i] = r; ws.send(JSON.stringify({ id: i, method, params }));
});
const evalJs = async e => (await send('Runtime.evaluate', { expression: e, returnByValue: true }))?.result?.value;

const probe = `(()=>{try{const e=document.getElementById('ErrorPrinter');
 // Chi chu nguoi choi thay: bo ten switch/bien, ten su kien, chu thich (108/408), note, nhan 402 (chi trong editor).
 const out=[];const S=$dataSystem;
 out.push(S.gameTitle,S.currencyUnit,S.elements,S.skillTypes,S.weaponTypes,S.armorTypes,S.equipTypes,S.terms);
 for(const db of [$dataActors,$dataClasses,$dataItems,$dataWeapons,$dataArmors,$dataSkills,$dataStates,$dataEnemies])
  for(const o of db||[]) if(o) out.push(o.name,o.nickname,o.profile,o.description,o.message1,o.message2,o.message3,o.message4);
 for(const ev of $dataCommonEvents||[]) for(const c of (ev&&ev.list)||[]){
  if(c.code===401||c.code===405) out.push(c.parameters[0]); else if(c.code===102) out.push(c.parameters[0]);
  else if(c.code===101) out.push(c.parameters[4]);}
 const t=JSON.stringify(out)+' '+(${extra ? `String(${extra})` : "''"});
 return JSON.stringify({scene:SceneManager._scene&&SceneManager._scene.constructor.name,font:Graphics.isFontLoaded('GameFont'),
  db:DataManager.isDatabaseLoaded(),err:e?e.innerText.trim().slice(0,300):'',
  cjk:(t.match(/[\\u3040-\\u30ff\\u3400-\\u9fff]/g)||[]).length,
  vi:(t.match(/[ăâđêôơưàáảãạằắẳẵặầấẩẫậèéẻẽẹềếểễệìíỉĩịòóỏõọồốổỗộờớởỡợùúủũụừứửữựỳýỷỹỵ]/gi)||[]).length})}
 catch(x){return JSON.stringify({exc:String(x)})}})()`;

let allOk = true;
try {
  let page;
  for (let t = 0; t < 30 && !page; t++) {
    await sleep(1000);
    try { page = (await (await fetch(`http://127.0.0.1:${port}/json`)).json()).find(x => x.type === 'page'); } catch { }
  }
  if (!page) throw new Error('trinh duyet khong mo cong debug');
  ws = new WebSocket(page.webSocketDebuggerUrl);
  ws.onmessage = m => {
    const d = JSON.parse(m.data);
    if (d.method === 'Runtime.exceptionThrown') {
      const x = d.params.exceptionDetails;
      errors.push((x.exception?.description || x.text || '').split('\n')[0].slice(0, 200));
    }
    if (pend[d.id]) pend[d.id](d.result);
  };
  await new Promise(r => ws.onopen = r);
  await send('Runtime.enable');
  await send('Page.enable');
  let scriptId = null;
  for (const lang of runs) {
    const st = { ...store };
    if (lang !== null) {
      if (!LZ) throw new Error('khong thay lz-string.js de ghi ngon ngu');
      st['RPG File' + langKey] = LZ.compressToBase64(lang);
    }
    if (scriptId) await send('Page.removeScriptToEvaluateOnNewDocument', { identifier: scriptId });
    scriptId = (await send('Page.addScriptToEvaluateOnNewDocument', { source:
      `if(location.origin==${JSON.stringify(base.slice(0, -1))}){localStorage.clear();` +
      `for(const [k,v] of Object.entries(${JSON.stringify(st)}))localStorage.setItem(k,v);}` })).identifier;
    errors = [];
    await send('Page.navigate', { url: base + (www ? www + '/' : '') + 'index.html' });
    let s = {}, reached = false;
    for (let t = 0; t < secs; t++) {
      await sleep(1000);
      try { s = JSON.parse(await evalJs(probe) || '{}'); } catch { }
      if (s.err) break;
      if (/^Scene_(Title|Map)$/.test(s.scene || '')) { reached = true; await sleep(1500); s = JSON.parse(await evalJs(probe) || '{}'); break; }
    }
    const vietOk = s.vi >= 20 && s.cjk * 10 <= s.vi;
    const ok = reached && s.font && !s.err && vietOk;
    allOk &&= ok;
    const tag = lang === null ? 'ban luu hien tai' : `ngon ngu "${lang}"`;
    console.log(`${ok ? 'OK ' : 'LOI'} [${tag}] scene=${s.scene} font=${s.font} tieng_viet=${s.vi} chu_goc_CJK=${s.cjk}` +
      (s.err ? ` err=${s.err}` : '') + (reached ? '' : ' (khong toi Scene_Title)') + (vietOk ? '' : ' (KHONG PHAI TIENG VIET)'));
    for (const e of [...new Set(errors)].slice(0, 5)) console.log('    JS: ' + e);
  }
  if (measure || shotsDir) {
    const boxes = collectBoxes();
    const ready = await evalJs(`(()=>{try{${MEASURE_FN};return 'ok'}catch(x){return String(x)}})()`);
    if (ready !== 'ok') throw new Error('khong tao duoc khung do: ' + ready);
    let n = 0, bad = [], info = {};
    for (let k = 0; k < boxes.length; k += 1500) {
      const r = JSON.parse(await evalJs(`__vgtMeasure(${JSON.stringify(boxes.slice(k, k + 1500))})`) || '{}');
      n += r.n || 0; bad = bad.concat(r.bad || []); info = { avail: r.avail, rows: r.rows };
    }
    if (measure) {
      const ok = boxes.length > 0 && bad.length === 0;
      allOk &&= ok;
      console.log(`${ok ? 'OK ' : 'LOI'} [do khung] ${boxes.length} hop / ${n} dong, rong toi da ${info.avail}px, ` +
        `${info.rows} dong/hop: tran ${bad.filter(b => b.kind === 'tran').length}, qua dong ${bad.filter(b => b.kind === 'qua_dong').length}`);
      for (const b of bad.slice(0, 20)) console.log(`    ${b.grp}@${b.i} ${b.kind} ${b.px ?? b.n}/${b.max}: ${b.text.slice(0, 80)}`);
      if (reportFile) writeFileSync(reportFile, JSON.stringify({ hop: boxes.length, dong: n, ...info, loi: bad }, null, 1));
    }
    if (shotsDir) {
      mkdirSync(shotsDir, { recursive: true });
      const shot = async name => {
        const r = await send('Page.captureScreenshot', { format: 'png' });
        writeFileSync(join(shotsDir, name), Buffer.from(r.data, 'base64'));
      };
      await shot('00_tieu_de.png');
      // Mau: canh nguoi dung chon + hop co dong rong nhat (kha nang tran cao nhat)
      const widest = bad.filter(b => b.kind === 'tran').map(b => b.grp + '@' + b.i);
      const pickBoxes = [...boxes.filter(b => samples.includes(b.grp)).slice(0, 6),
        ...boxes.filter(b => widest.includes(b.grp + '@' + b.i)).slice(0, 4),
        ...[...boxes].sort((a, b) => Math.max(...b.lines.map(l => l.length)) - Math.max(...a.lines.map(l => l.length))).slice(0, 4)];
      const seen = new Set(); let k = 1; const index = [];
      for (const b of pickBoxes) {
        const key = b.grp + '@' + b.i; if (seen.has(key)) continue; seen.add(key);
        await evalJs(`(()=>{const W=window.__vgtWin;const MZ=Utils.RPGMAKER_NAME==='MZ';const h=W.w.fittingHeight?W.w.fittingHeight(W.rows):W.rows*36+36;
          if(window.__vgtShow)SceneManager._scene.removeChild(window.__vgtShow);
          const v=MZ?new Window_Base(new Rectangle(0,Graphics.boxHeight-h,Graphics.boxWidth,h)):new Window_Base(0,Graphics.boxHeight-h,W.w.width,h);
          const x=${JSON.stringify(b.face)}?W.faceW:0;const L=${JSON.stringify(b.lines)};
          const lh=v.lineHeight?v.lineHeight():36;L.forEach((l,i)=>v.drawTextEx(l,x,i*lh));
          window.__vgtShow=v;SceneManager._scene.addChild(v);return 1})()`);
        await sleep(400);
        const name = `${String(k++).padStart(2, '0')}_${key.replace(/[^\w@.-]+/g, '_')}.png`;
        await shot(name); index.push({ anh: name, hop: key, dong: b.lines });
      }
      writeFileSync(join(shotsDir, 'danh_sach.json'), JSON.stringify(index, null, 1));
      console.log(`Anh: ${index.length + 1} file trong ${shotsDir} (danh_sach.json: anh -> hop thoai)`);
    }
  }
} catch (e) { allOk = false; console.log('LOI: ' + (e.message || e)); }
try { execSync(`taskkill /PID ${proc.pid} /T /F`, { stdio: 'ignore' }); } catch { }
proc.kill();
server.close();
// Don dep: xoa ho so trinh duyet tam (moi lan ~ vai chuc MB).
await sleep(1000);
try { rmSync(profile, { recursive: true, force: true, maxRetries: 5, retryDelay: 500 }); } catch { }
console.log(allOk ? 'DAT' : 'KHONG DAT');
process.exit(allOk ? 0 : 1);
