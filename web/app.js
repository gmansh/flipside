// ---- Character code table ----
const CODES = {
  " ": 0,
  A:1,B:2,C:3,D:4,E:5,F:6,G:7,H:8,I:9,J:10,
  K:11,L:12,M:13,N:14,O:15,P:16,Q:17,R:18,S:19,T:20,
  U:21,V:22,W:23,X:24,Y:25,Z:26,
  "1":27,"2":28,"3":29,"4":30,"5":31,
  "6":32,"7":33,"8":34,"9":35,"0":36,
  "!":37,"@":38,"#":39,"$":40,"(":41,")":42,
  "-":43,"+":44,"&":45,"=":46,";":47,":":48,
  "'":49,'"':50,"%":51,",":52,".":53,"/":54,
  "?":55,"°":56
};
const CHARS_DISPLAY = {
  0:" ",1:"A",2:"B",3:"C",4:"D",5:"E",6:"F",7:"G",8:"H",9:"I",10:"J",
  11:"K",12:"L",13:"M",14:"N",15:"O",16:"P",17:"Q",18:"R",19:"S",20:"T",
  21:"U",22:"V",23:"W",24:"X",25:"Y",26:"Z",
  27:"1",28:"2",29:"3",30:"4",31:"5",32:"6",33:"7",34:"8",35:"9",36:"0",
  37:"!",38:"@",39:"#",40:"$",41:"(",42:")",43:"-",44:"+",45:"&",46:"=",
  47:";",48:":",49:"'",50:'"',51:"%",52:",",53:".",54:"/",55:"?",56:"°",
  63:"",64:"",65:"",66:"",67:"",68:"",69:"",70:""
};
const COLOR_CODES = [63,64,65,66,67,68,69,70];
const COLOR_NAMES = {63:"RED",64:"ORANGE",65:"YELLOW",66:"GREEN",67:"BLUE",68:"VIOLET",69:"WHITE",70:"BLACK"};
const COLOR_CSS = {63:"#be2828",64:"#d27828",65:"#dccc3c",66:"#32a032",67:"#3250c8",68:"#8232b4",69:"#f0f0f0",70:"#111"};

const ROWS = 6, COLS = 22;

// ---- State ----
let board = Array.from({length: ROWS}, () => new Array(COLS).fill(0));
let selectedCell = null;
let selectedCode = 0;
let isDragging = false;

// ---- DOM ----
const boardEl = document.getElementById("board");
const statusEl = document.getElementById("status");
const textInput = document.getElementById("text-input");
const valignSel = document.getElementById("valign");
const animSel = document.getElementById("anim-strategy");
const templateNameEl = document.getElementById("template-name");
const templateListEl = document.getElementById("template-list");
const pickerPanel = document.getElementById("picker-panel");
const charGrid = document.getElementById("char-grid");
const imageInput = document.getElementById("image-input");
const imagePreviewWrap = document.getElementById("image-preview-wrap");
const imagePreviewEl = document.getElementById("image-preview");

// ---- Board rendering ----
function buildGrid() {
  boardEl.innerHTML = "";
  for (let r = 0; r < ROWS; r++) {
    for (let c = 0; c < COLS; c++) {
      const cell = document.createElement("div");
      cell.className = "cell";
      cell.dataset.r = r;
      cell.dataset.c = c;
      cell.addEventListener("mousedown", onCellDown);
      cell.addEventListener("mouseenter", onCellEnter);
      boardEl.appendChild(cell);
    }
  }
  document.addEventListener("mouseup", () => isDragging = false);
}

function updateGrid() {
  const cells = boardEl.querySelectorAll(".cell");
  cells.forEach(cell => {
    const r = +cell.dataset.r, c = +cell.dataset.c;
    const code = board[r][c];
    cell.dataset.code = code;
    cell.textContent = CHARS_DISPLAY[code] ?? "";
    if (selectedCell && selectedCell[0] === r && selectedCell[1] === c) {
      cell.classList.add("selected");
    } else {
      cell.classList.remove("selected");
    }
  });
  updatePreview();
}

function onCellDown(e) {
  isDragging = true;
  const r = +this.dataset.r, c = +this.dataset.c;
  selectedCell = [r, c];
  board[r][c] = selectedCode;
  updateGrid();
}

function onCellEnter() {
  if (!isDragging) return;
  const r = +this.dataset.r, c = +this.dataset.c;
  board[r][c] = selectedCode;
  updateGrid();
}

// ---- Character picker ----
function buildPicker() {
  charGrid.innerHTML = "";

  // Blank
  const blankBtn = makePickBtn(0, "·");
  charGrid.appendChild(blankBtn);

  // Letters
  for (let i = 1; i <= 26; i++) {
    charGrid.appendChild(makePickBtn(i, CHARS_DISPLAY[i]));
  }
  // Digits
  for (const k of ["1","2","3","4","5","6","7","8","9","0"]) {
    charGrid.appendChild(makePickBtn(CODES[k], k));
  }
  // Symbols
  for (const [ch, code] of Object.entries(CODES)) {
    if (ch === " " || /[A-Z0-9]/i.test(ch)) continue;
    charGrid.appendChild(makePickBtn(code, ch));
  }
  // Colors
  COLOR_CODES.forEach(code => {
    const btn = makePickBtn(code, "");
    btn.classList.add("color-swatch");
    charGrid.appendChild(btn);
  });
}

function makePickBtn(code, label) {
  const btn = document.createElement("button");
  btn.className = "pick-btn";
  btn.dataset.code = code;
  btn.textContent = label;
  btn.title = COLOR_NAMES[code] ?? label;
  btn.addEventListener("click", () => {
    selectedCode = code;
    document.querySelectorAll(".pick-btn").forEach(b => b.classList.remove("selected"));
    btn.classList.add("selected");
  });
  return btn;
}

// ---- Text encoding ----
function encode(text) {
  return [...text.toUpperCase()].map(ch => CODES[ch] ?? 0);
}

function centerLine(text) {
  const codes = encode(text);
  const row = new Array(COLS).fill(0);
  const pad = Math.floor((COLS - Math.min(codes.length, COLS)) / 2);
  for (let i = 0; i < Math.min(codes.length, COLS); i++) {
    row[pad + i] = codes[i];
  }
  return row;
}

function makeBoard(lines, valign = "center") {
  const b = Array.from({length: ROWS}, () => new Array(COLS).fill(0));
  const n = Math.min(lines.length, ROWS);
  let start = 0;
  if (valign === "bottom") start = ROWS - n;
  else if (valign === "center") start = Math.floor((ROWS - n) / 2);
  for (let i = 0; i < n; i++) {
    b[start + i] = centerLine(lines[i]);
  }
  return b;
}

function applyTextPreview() {
  const text = textInput.value;
  const lines = text.split("\n");
  board = makeBoard(lines, valignSel.value);
  updateGrid();
}

// ---- Status & Toast ----
function showToast(msg, type = "") {
  const container = document.getElementById("toast-container");
  const toast = document.createElement("div");
  toast.className = "toast" + (type ? " " + type : "");
  toast.textContent = msg;
  container.appendChild(toast);
  setTimeout(() => {
    toast.classList.add("toast-fade-out");
    toast.addEventListener("animationend", () => toast.remove());
  }, 3000);
}

function setStatus(msg, type = "") {
  statusEl.textContent = msg;
  statusEl.className = type;
  if (type === "ok" || type === "err") showToast(msg, type);
}

// ---- API calls ----
async function sendBoard() {
  setStatus("Sending...");
  const strategy = animSel.value;
  try {
    let resp;
    if (strategy && strategy !== "none") {
      resp = await fetch("/api/message/animated", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({message: board, strategy})
      });
    } else {
      resp = await fetch("/api/message", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({message: board})
      });
    }
    if (resp.ok) setStatus("Sent!", "ok");
    else setStatus(`Error: ${resp.status}`, "err");
  } catch(e) {
    setStatus(`Error: ${e.message}`, "err");
  }
}

async function readBoard() {
  setStatus("Reading...");
  try {
    const resp = await fetch("/api/message");
    if (resp.ok) {
      const data = await resp.json();
      board = data.message;
      updateGrid();
      setStatus("Board loaded.", "ok");
    } else {
      setStatus(`Error: ${resp.status}`, "err");
    }
  } catch(e) {
    setStatus(`Error: ${e.message}`, "err");
  }
}

function clearBoard() {
  board = Array.from({length: ROWS}, () => new Array(COLS).fill(0));
  updateGrid();
  setStatus("Cleared.", "");
}

// ---- Templates ----
async function loadTemplates() {
  try {
    const resp = await fetch("/api/templates");
    if (!resp.ok) return;
    const data = await resp.json();
    templateListEl.innerHTML = "";
    if (data.templates.length === 0) {
      templateListEl.innerHTML = '<span style="color:#555;font-size:0.8rem">No saved templates</span>';
      return;
    }
    data.templates.forEach(t => {
      const item = document.createElement("div");
      item.className = "template-item";
      const span = document.createElement("span");
      span.title = t.name;
      span.textContent = t.name;
      const loadBtn = document.createElement("button");
      loadBtn.textContent = "Load";
      loadBtn.addEventListener("click", () => loadTemplate(t.name));
      const delBtn = document.createElement("button");
      delBtn.className = "danger";
      delBtn.textContent = "Del";
      delBtn.addEventListener("click", () => deleteTemplate(t.name));
      item.appendChild(span);
      item.appendChild(loadBtn);
      item.appendChild(delBtn);
      templateListEl.appendChild(item);
    });
  } catch(e) {}
}

function loadTemplate(name) {
  fetch("/api/templates").then(r => r.json()).then(data => {
    const t = data.templates.find(t => t.name === name);
    if (t) { board = t.message; updateGrid(); setStatus(`Loaded '${name}'`, "ok"); }
  });
}

async function saveTemplate() {
  const name = templateNameEl.value.trim();
  if (!name) { setStatus("Enter a template name.", "err"); return; }
  try {
    const resp = await fetch("/api/templates", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({name, message: board})
    });
    if (resp.ok) {
      setStatus(`Saved '${name}'`, "ok");
      loadTemplates();
    } else {
      setStatus(`Error: ${resp.status}`, "err");
    }
  } catch(e) {
    setStatus(`Error: ${e.message}`, "err");
  }
}

async function deleteTemplate(name) {
  try {
    const resp = await fetch(`/api/templates/${encodeURIComponent(name)}`, {method: "DELETE"});
    if (resp.ok) { setStatus(`Deleted '${name}'`, "ok"); loadTemplates(); }
    else setStatus(`Error: ${resp.status}`, "err");
  } catch(e) {
    setStatus(`Error: ${e.message}`, "err");
  }
}

// ---- Cron schedule helpers ----
const DAY_LABELS = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"];
const DAY_CRON   = ["1","2","3","4","5","6","0"];  // cron: 0=Sun, 1=Mon..6=Sat

function parseCron(expr) {
  const p = expr.split(/\s+/);
  const minute = parseInt(p[0]) || 0;
  const hourField = p[1] || "0";
  const dow = p[4] || "*";
  let freq = "daily";
  let hour = 0;
  let interval = 2;
  let days = [0,1,2,3,4,5,6];

  // Detect */N hour pattern (every N hours)
  const stepMatch = hourField.match(/^\*\/(\d+)$/);
  if (stepMatch) {
    freq = "interval";
    interval = parseInt(stepMatch[1]);
  } else {
    hour = parseInt(hourField) || 0;
    if (dow === "1-5" || dow === "MON-FRI") { freq = "weekdays"; days = [0,1,2,3,4]; }
    else if (dow === "0,6" || dow === "6,0" || dow === "SAT,SUN") { freq = "weekends"; days = [5,6]; }
    else if (dow !== "*") {
      freq = "custom";
      days = dow.split(",").map(d => {
        const n = parseInt(d);
        return n === 0 ? 6 : n - 1;
      });
    }
  }
  return { minute, hour, freq, days, interval };
}

function buildCron(minute, hour, freq, days, interval) {
  if (freq === "interval") {
    return `${minute} */${interval} * * *`;
  }
  let dow = "*";
  if (freq === "weekdays") dow = "1-5";
  else if (freq === "weekends") dow = "6,0";
  else if (freq === "custom" && days.length > 0 && days.length < 7) {
    dow = days.map(d => DAY_CRON[d]).join(",");
  }
  return `${minute} ${hour} * * ${dow}`;
}

function describeCron(expr) {
  const {minute, hour, freq, days, interval} = parseCron(expr);
  const minStr = String(minute).padStart(2, "0");
  if (freq === "interval") {
    return `Every ${interval} hour${interval > 1 ? "s" : ""} at :${minStr}`;
  }
  const h12 = hour % 12 || 12;
  const ampm = hour < 12 ? "AM" : "PM";
  const time = `${h12}:${minStr} ${ampm}`;
  if (freq === "daily") return `Daily at ${time}`;
  if (freq === "weekdays") return `Weekdays at ${time}`;
  if (freq === "weekends") return `Weekends at ${time}`;
  const dayStr = days.map(d => DAY_LABELS[d]).join(", ");
  return `${dayStr} at ${time}`;
}

// ---- Automations ----
// Tracks original values per automation for dirty detection
const autoOriginals = {};

async function loadAutomations() {
  const listEl = document.getElementById("automation-list");
  try {
    const resp = await fetch("/api/automations");
    if (!resp.ok) return;
    const data = await resp.json();
    listEl.innerHTML = "";
    if (data.automations.length === 0) {
      listEl.innerHTML = '<span style="color:#555;font-size:0.8rem">No automations</span>';
      return;
    }
    for (const a of data.automations) {
      await renderAutomationCard(listEl, a);
    }
  } catch(e) {}
}

async function renderAutomationCard(container, job) {
  const name = job.name;
  const card = document.createElement("div");
  card.className = "auto-card";
  card.id = `auto-card-${name}`;

  // Header: name + run button
  const header = document.createElement("div");
  header.className = "auto-header";
  const nameEl = document.createElement("span");
  nameEl.className = "auto-name";
  nameEl.textContent = name;
  header.appendChild(nameEl);
  const runBtn = document.createElement("button");
  runBtn.textContent = "Run Now";
  runBtn.addEventListener("click", () => triggerAutomation(name));
  header.appendChild(runBtn);
  card.appendChild(header);

  const next = job.next_run ? new Date(job.next_run).toLocaleString() : "—";
  const nextEl = document.createElement("div");
  nextEl.className = "auto-next";
  nextEl.textContent = "Next run: " + next;
  nextEl.id = `auto-next-${name}`;
  card.appendChild(nextEl);

  // Fetch settings
  try {
    const resp = await fetch(`/api/automations/${encodeURIComponent(name)}/settings`);
    if (!resp.ok) { container.appendChild(card); return; }
    const settings = await resp.json();

    // Store originals
    autoOriginals[name] = {};
    settings.schema.forEach(f => { autoOriginals[name][f.key] = String(f.value); });

    // Settings fields
    const fieldsEl = document.createElement("div");
    fieldsEl.className = "auto-settings";

    settings.schema.forEach(field => {
      if (field.type === "cron") {
        fieldsEl.appendChild(buildCronPicker(name, field.key, field.value));
      } else {
        const fieldEl = document.createElement("div");
        fieldEl.className = "auto-field";
        const label = document.createElement("label");
        label.textContent = field.label;
        const input = document.createElement("input");
        input.type = field.type === "number" ? "number" : "text";
        if (field.type === "number") input.step = "any";
        input.id = `auto-${name}-${field.key}`;
        input.dataset.key = field.key;
        input.dataset.automation = name;
        input.value = field.value;
        input.addEventListener("input", () => onAutoFieldChange(name));
        fieldEl.appendChild(label);
        fieldEl.appendChild(input);
        fieldsEl.appendChild(fieldEl);
      }
    });
    card.appendChild(fieldsEl);

    // Apply / Cancel buttons (hidden initially)
    const btnRow = document.createElement("div");
    btnRow.className = "auto-btn-row";
    btnRow.id = `auto-btns-${name}`;
    btnRow.style.display = "none";
    const applyBtn = document.createElement("button");
    applyBtn.className = "primary";
    applyBtn.textContent = "Apply";
    applyBtn.addEventListener("click", () => applyAutoSettings(name));
    const cancelBtn = document.createElement("button");
    cancelBtn.textContent = "Cancel";
    cancelBtn.addEventListener("click", () => cancelAutoSettings(name));
    btnRow.appendChild(applyBtn);
    btnRow.appendChild(cancelBtn);
    card.appendChild(btnRow);
  } catch(e) {}

  container.appendChild(card);
}

function buildCronPicker(name, key, cronValue) {
  const wrap = document.createElement("div");
  wrap.className = "cron-picker";
  wrap.dataset.automation = name;
  wrap.dataset.key = key;

  const parsed = parseCron(cronValue);

  // Hidden input holds the cron string for form collection
  const hidden = document.createElement("input");
  hidden.type = "hidden";
  hidden.id = `auto-${name}-${key}`;
  hidden.dataset.key = key;
  hidden.dataset.automation = name;
  hidden.value = cronValue;
  wrap.appendChild(hidden);

  // Summary line
  const summary = document.createElement("div");
  summary.className = "cron-summary";
  summary.id = `cron-summary-${name}`;
  summary.textContent = describeCron(cronValue);
  wrap.appendChild(summary);

  const isInterval = parsed.freq === "interval";

  // Frequency selector
  const freqRow = document.createElement("div");
  freqRow.className = "cron-row";
  const freqLabel = document.createElement("label");
  freqLabel.textContent = "Frequency";
  const freqSel = document.createElement("select");
  freqSel.id = `cron-freq-${name}`;
  [["interval","Every N hours"],["daily","Every day"],["weekdays","Weekdays (Mon\u2013Fri)"],["weekends","Weekends (Sat\u2013Sun)"],["custom","Custom days"]].forEach(([v,t]) => {
    const opt = document.createElement("option");
    opt.value = v;
    opt.textContent = t;
    if (v === parsed.freq) opt.selected = true;
    freqSel.appendChild(opt);
  });
  freqRow.appendChild(freqLabel);
  freqRow.appendChild(freqSel);
  wrap.appendChild(freqRow);

  // Interval selector (shown only for "Every N hours")
  const intervalRow = document.createElement("div");
  intervalRow.className = "cron-row";
  intervalRow.id = `cron-interval-row-${name}`;
  if (!isInterval) intervalRow.style.display = "none";
  const intervalLabel = document.createElement("label");
  intervalLabel.textContent = "Every";
  const intervalWrap = document.createElement("div");
  intervalWrap.className = "cron-time-wrap";
  const intervalSel = document.createElement("select");
  intervalSel.id = `cron-interval-${name}`;
  [1,2,3,4,6,8,12].forEach(n => {
    const opt = document.createElement("option");
    opt.value = n;
    opt.textContent = n;
    if (n === parsed.interval) opt.selected = true;
    intervalSel.appendChild(opt);
  });
  const hoursSpan = document.createElement("span");
  hoursSpan.textContent = "hour(s)";
  hoursSpan.style.cssText = "font-size:0.78rem;color:#ccc";
  intervalWrap.appendChild(intervalSel);
  intervalWrap.appendChild(hoursSpan);
  intervalRow.appendChild(intervalLabel);
  intervalRow.appendChild(intervalWrap);
  wrap.appendChild(intervalRow);

  // Day checkboxes (shown only for custom)
  const daysRow = document.createElement("div");
  daysRow.className = "cron-days";
  daysRow.id = `cron-days-${name}`;
  if (parsed.freq !== "custom") daysRow.style.display = "none";
  DAY_LABELS.forEach((label, i) => {
    const cb = document.createElement("input");
    cb.type = "checkbox";
    cb.id = `cron-day-${name}-${i}`;
    cb.dataset.dayIdx = i;
    cb.checked = parsed.days.includes(i);
    cb.addEventListener("change", () => syncCronPicker(name));
    const lbl = document.createElement("label");
    lbl.setAttribute("for", cb.id);
    lbl.textContent = label;
    lbl.className = "cron-day-label";
    daysRow.appendChild(cb);
    daysRow.appendChild(lbl);
  });
  wrap.appendChild(daysRow);

  // Time picker (hidden for interval mode; only minute shown for interval via offset row)
  const timeRow = document.createElement("div");
  timeRow.className = "cron-row";
  timeRow.id = `cron-time-row-${name}`;
  if (isInterval) timeRow.style.display = "none";
  const timeLabel = document.createElement("label");
  timeLabel.textContent = "Time";

  const timeWrap = document.createElement("div");
  timeWrap.className = "cron-time-wrap";

  // Hour (1-12)
  const hourSel = document.createElement("select");
  hourSel.id = `cron-hour-${name}`;
  for (let h = 1; h <= 12; h++) {
    const opt = document.createElement("option");
    opt.value = h;
    opt.textContent = h;
    const display12 = parsed.hour % 12 || 12;
    if (h === display12) opt.selected = true;
    hourSel.appendChild(opt);
  }

  // Minute
  const minSel = document.createElement("select");
  minSel.id = `cron-min-${name}`;
  for (let m = 0; m < 60; m += 5) {
    const opt = document.createElement("option");
    opt.value = m;
    opt.textContent = String(m).padStart(2, "0");
    if (m === Math.round(parsed.minute / 5) * 5 % 60) opt.selected = true;
    minSel.appendChild(opt);
  }

  // AM/PM
  const ampmSel = document.createElement("select");
  ampmSel.id = `cron-ampm-${name}`;
  ["AM","PM"].forEach(v => {
    const opt = document.createElement("option");
    opt.value = v;
    opt.textContent = v;
    if ((v === "AM" && parsed.hour < 12) || (v === "PM" && parsed.hour >= 12)) opt.selected = true;
    ampmSel.appendChild(opt);
  });

  timeWrap.appendChild(hourSel);
  const colon = document.createElement("span");
  colon.textContent = ":";
  colon.className = "cron-colon";
  timeWrap.appendChild(colon);
  timeWrap.appendChild(minSel);
  timeWrap.appendChild(ampmSel);

  timeRow.appendChild(timeLabel);
  timeRow.appendChild(timeWrap);
  wrap.appendChild(timeRow);

  // Minute offset for interval mode ("at :MM past the hour")
  const offsetRow = document.createElement("div");
  offsetRow.className = "cron-row";
  offsetRow.id = `cron-offset-row-${name}`;
  if (!isInterval) offsetRow.style.display = "none";
  const offsetLabel = document.createElement("label");
  offsetLabel.textContent = "At minute";
  const offsetWrap = document.createElement("div");
  offsetWrap.className = "cron-time-wrap";
  const offsetSel = document.createElement("select");
  offsetSel.id = `cron-offset-${name}`;
  for (let m = 0; m < 60; m += 5) {
    const opt = document.createElement("option");
    opt.value = m;
    opt.textContent = ":" + String(m).padStart(2, "0");
    if (m === Math.round(parsed.minute / 5) * 5 % 60) opt.selected = true;
    offsetSel.appendChild(opt);
  }
  offsetWrap.appendChild(offsetSel);
  const pastSpan = document.createElement("span");
  pastSpan.textContent = "past the hour";
  pastSpan.style.cssText = "font-size:0.78rem;color:#ccc";
  offsetWrap.appendChild(pastSpan);
  offsetRow.appendChild(offsetLabel);
  offsetRow.appendChild(offsetWrap);
  wrap.appendChild(offsetRow);

  // Wire up change events
  function onFreqChange() {
    const v = freqSel.value;
    daysRow.style.display = v === "custom" ? "flex" : "none";
    intervalRow.style.display = v === "interval" ? "" : "none";
    timeRow.style.display = v === "interval" ? "none" : "";
    offsetRow.style.display = v === "interval" ? "" : "none";
    syncCronPicker(name);
  }
  freqSel.addEventListener("change", onFreqChange);
  intervalSel.addEventListener("change", () => syncCronPicker(name));
  offsetSel.addEventListener("change", () => syncCronPicker(name));
  hourSel.addEventListener("change", () => syncCronPicker(name));
  minSel.addEventListener("change", () => syncCronPicker(name));
  ampmSel.addEventListener("change", () => syncCronPicker(name));

  return wrap;
}

function syncCronPicker(name) {
  const freq = document.getElementById(`cron-freq-${name}`).value;
  let minute, hour, days = [], interval = 2;

  if (freq === "interval") {
    interval = parseInt(document.getElementById(`cron-interval-${name}`).value);
    minute = parseInt(document.getElementById(`cron-offset-${name}`).value);
    hour = 0;
  } else {
    const h12 = parseInt(document.getElementById(`cron-hour-${name}`).value);
    minute = parseInt(document.getElementById(`cron-min-${name}`).value);
    const ampm = document.getElementById(`cron-ampm-${name}`).value;
    hour = h12 % 12 + (ampm === "PM" ? 12 : 0);
    if (freq === "custom") {
      DAY_LABELS.forEach((_, i) => {
        if (document.getElementById(`cron-day-${name}-${i}`).checked) days.push(i);
      });
      if (days.length === 0) days = [0];
    }
  }

  const cron = buildCron(minute, hour, freq, days, interval);
  const hidden = document.getElementById(`auto-${name}-schedule`);
  if (hidden) hidden.value = cron;

  const summary = document.getElementById(`cron-summary-${name}`);
  if (summary) summary.textContent = describeCron(cron);

  onAutoFieldChange(name);
}

function getAutoFieldValue(name, key) {
  const el = document.getElementById(`auto-${name}-${key}`);
  return el ? el.value : undefined;
}

function onAutoFieldChange(name) {
  const card = document.getElementById(`auto-card-${name}`);
  if (!card) return;
  const inputs = card.querySelectorAll("input[data-automation='" + name + "']");
  let dirty = false;
  inputs.forEach(input => {
    const orig = autoOriginals[name]?.[input.dataset.key];
    const changed = input.value !== orig;
    if (input.type !== "hidden" && input.type !== "checkbox") input.classList.toggle("modified", changed);
    if (changed) dirty = true;
  });
  const btns = document.getElementById(`auto-btns-${name}`);
  if (btns) btns.style.display = dirty ? "flex" : "none";
}

function cancelAutoSettings(name) {
  // Re-render is simplest to reset cron picker state
  loadAutomations();
}

async function applyAutoSettings(name) {
  const card = document.getElementById(`auto-card-${name}`);
  if (!card) return;
  const inputs = card.querySelectorAll("input[data-automation='" + name + "']");
  const params = {};
  inputs.forEach(input => {
    if (input.type !== "checkbox") params[input.dataset.key] = input.value;
  });

  try {
    const resp = await fetch(`/api/automations/${encodeURIComponent(name)}/settings`, {
      method: "PUT",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({params})
    });
    if (resp.ok) {
      showToast(`'${name}' settings updated`, "ok");
      loadAutomations();
    } else {
      const detail = await resp.text();
      showToast(`Error: ${detail}`, "err");
    }
  } catch(e) {
    showToast(`Error: ${e.message}`, "err");
  }
}

async function triggerAutomation(name) {
  showToast(`Running '${name}'...`);
  setStatus(`Running '${name}'...`);
  try {
    const resp = await fetch(`/api/automations/${encodeURIComponent(name)}/trigger`, {method: "POST"});
    if (resp.ok) {
      const data = await resp.json();
      board = data.board;
      updateGrid();
      setStatus(`'${name}' sent!`, "ok");
    } else {
      const detail = await resp.text();
      setStatus(`Error: ${resp.status} — ${detail}`, "err");
    }
  } catch(e) {
    setStatus(`Error: ${e.message}`, "err");
  }
}

// ---- Image import ----
function previewColorBoard(b) {
  imagePreviewEl.innerHTML = "";
  imagePreviewWrap.classList.add("show");
  for (let r = 0; r < ROWS; r++) {
    for (let c = 0; c < COLS; c++) {
      const cell = document.createElement("div");
      cell.className = "prev-cell";
      const code = b[r][c];
      cell.style.background = COLOR_CSS[code] ?? "#f0f0f0";
      imagePreviewEl.appendChild(cell);
    }
  }
}

async function handleImageUpload(e) {
  const file = e.target.files[0];
  if (!file) return;
  setStatus("Processing image...");
  const formData = new FormData();
  formData.append("file", file);
  try {
    const resp = await fetch("/api/message/image", {method: "POST", body: formData});
    if (resp.ok) {
      const data = await resp.json();
      board = data.board;
      updateGrid();
      previewColorBoard(board);
      setStatus("Image sent!", "ok");
    } else {
      setStatus(`Error: ${resp.status}`, "err");
    }
  } catch(e) {
    setStatus(`Error: ${e.message}`, "err");
  }
  imageInput.value = "";
}

// ---- Board preview (simulator) ----
function updatePreview() {
  const el = document.getElementById("live-preview");
  let html = '<div class="sim-board">';
  for (let r = 0; r < ROWS; r++) {
    for (let c = 0; c < COLS; c++) {
      const code = board[r][c];
      if (code === 0) {
        html += '<div class="sim-cell"></div>';
      } else if (COLOR_CSS[code]) {
        html += `<div class="sim-cell" style="background:${COLOR_CSS[code]}"></div>`;
      } else {
        const ch = CHARS_DISPLAY[code] ?? "";
        html += `<div class="sim-cell ch">${ch}</div>`;
      }
    }
  }
  html += "</div>";
  el.innerHTML = html;
}

async function refreshPreview() {
  try {
    const resp = await fetch("/api/message");
    if (resp.ok) {
      const data = await resp.json();
      board = data.message;
      updateGrid();
    } else {
      setStatus("Could not read board", "err");
    }
  } catch(e) {
    setStatus("Error: " + e.message, "err");
  }
}

// ---- Board status ----
let boardOnline = false;

async function checkBoardStatus() {
  const elOnline = document.getElementById("bs-online");
  const elIp = document.getElementById("bs-ip");
  const elPort = document.getElementById("bs-port");
  const elError = document.getElementById("bs-error");
  const errorRow = elError.closest(".status-row");
  try {
    const resp = await fetch("/api/status");
    if (!resp.ok) return;
    const s = await resp.json();
    const wasOffline = !boardOnline;
    boardOnline = s.online;
    elIp.textContent = s.ip;
    elPort.textContent = s.port;
    if (s.online) {
      elOnline.textContent = "Online";
      elOnline.className = "status-value status-online";
      errorRow.style.display = "none";
      if (wasOffline) {
        showToast("Board is back online", "ok");
        refreshPreview();
      }
    } else {
      elOnline.textContent = "Offline";
      elOnline.className = "status-value status-offline";
      errorRow.style.display = "";
      elError.textContent = s.error || "Unknown";
      elError.className = "status-value status-offline";
    }
  } catch(e) {
    elOnline.textContent = "Unknown";
    elOnline.className = "status-value";
  }
}

// ---- Init ----
buildGrid();
buildPicker();
updateGrid();
loadTemplates();
loadAutomations();
checkBoardStatus();
setInterval(checkBoardStatus, 15000);

textInput.addEventListener("input", applyTextPreview);
valignSel.addEventListener("change", applyTextPreview);

document.getElementById("btn-send").addEventListener("click", sendBoard);
document.getElementById("btn-read").addEventListener("click", readBoard);
document.getElementById("btn-clear").addEventListener("click", clearBoard);
document.getElementById("btn-save-template").addEventListener("click", saveTemplate);
document.getElementById("btn-toggle-picker").addEventListener("click", () => {
  pickerPanel.classList.toggle("open");
});
imageInput.addEventListener("change", handleImageUpload);
document.getElementById("btn-image-pick").addEventListener("click", () => imageInput.click());
document.getElementById("btn-refresh-preview").addEventListener("click", refreshPreview);
