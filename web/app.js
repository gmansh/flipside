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

// ---- Automations ----
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
    data.automations.forEach(a => {
      const item = document.createElement("div");
      item.className = "template-item";
      const next = a.next_run ? new Date(a.next_run).toLocaleString() : "—";
      const span = document.createElement("span");
      span.title = "Next: " + next;
      span.textContent = a.name;
      const btn = document.createElement("button");
      btn.textContent = "Run";
      btn.addEventListener("click", () => triggerAutomation(a.name));
      item.appendChild(span);
      item.appendChild(btn);
      listEl.appendChild(item);
    });
  } catch(e) {}
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

// ---- Init ----
buildGrid();
buildPicker();
updateGrid();
loadTemplates();
loadAutomations();

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
