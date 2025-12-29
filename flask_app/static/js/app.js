async function api(path, method='GET', body=null){
  const opts = {method, headers:{}}
  if(body){ opts.headers['Content-Type']='application/json'; opts.body = JSON.stringify(body) }
  const res = await fetch(path, opts)
  const text = await res.text()
  try{ return {ok: res.ok, status: res.status, json: JSON.parse(text)} }catch(e){ return {ok: res.ok, status: res.status, text} }
}

function $(id){ return document.getElementById(id) }
let booksCache = []

async function fetchReaders(){
  const res = await api('/readers')
  if(res.ok){ renderReaders(res.json) }
}

function renderReaders(list){
  const tbody = $('readersBody'); tbody.innerHTML=''
  list.forEach(r=>{
    const tr = document.createElement('tr')
    tr.innerHTML = `<td>${r.reader_id}</td><td>${r.name}</td><td>${r.organization||''}</td><td>${r.age||''}</td><td><button class='btn secondary' onclick='fillBorrowReader(${r.reader_id})'>选择</button></td>`
    tbody.appendChild(tr)
  })
  populateReaderSelect(list)
}

async function fetchBooks(){
  const res = await api('/books')
  if(res.ok){ renderBooks(res.json) }
}

function renderBooks(list){
  booksCache = list
  const tbody = $('booksBody'); tbody.innerHTML=''
  list.forEach(b=>{
    const tr = document.createElement('tr')
    tr.innerHTML = `<td>${b.book_id}</td><td>${b.title}</td><td>${b.author||''}</td><td>${b.available_copies}</td><td><button class='btn secondary' onclick='fillBorrowBook(${b.book_id})' ${b.available_copies<=0?"disabled":''}>选择</button></td>`
    tbody.appendChild(tr)
  })
  populateBookSelect(list)
}

async function fetchLoans(){
  const res = await api('/loans')
  if(res.ok){ renderLoans(res.json) }
}

function renderLoans(list){
  const tbody = $('loansBody'); tbody.innerHTML=''
  list.forEach(l=>{
    const tr = document.createElement('tr')
    tr.innerHTML = `<td>${l.loan_id}</td><td>${l.title}</td><td>${l.reader_name}</td><td>${l.status}</td><td>${l.borrow_date}</td><td>${l.due_date}</td><td>${l.return_date||''}</td><td>${l.fine||0}</td>`
    tbody.appendChild(tr)
  })
}

function populateReaderSelect(list){
  const sel = $('borrowReader'); sel.innerHTML=''
  list.forEach(r=>{ const o=document.createElement('option'); o.value=r.reader_id; o.textContent=`${r.reader_id} - ${r.name}`; sel.appendChild(o) })
}
function populateBookSelect(list){
  const sel = $('borrowBook'); sel.innerHTML=''
  list.forEach(b=>{ const o=document.createElement('option'); o.value=b.book_id; o.textContent=`${b.book_id} - ${b.title} (avail:${b.available_copies})`; o.disabled = b.available_copies<=0; sel.appendChild(o) })
}

function fillBorrowReader(id){ $('borrowReader').value = id }
function fillBorrowBook(id){ $('borrowBook').value = id }

function setInlineMsg(id, msg){ const el = $(id); if(!el) return; el.textContent = msg; }

async function addReader(e){
  e.preventDefault();
  const fd = Object.fromEntries(new FormData(e.target));
  if(!fd.name || fd.name.trim()===''){ setInlineMsg('readerMsg','姓名为必填'); return }
  const res = await api('/readers','POST',{name:fd.name, age: fd.age?parseInt(fd.age):null, organization:fd.organization});
  showMessage(res);
  setInlineMsg('readerMsg','');
  if(res.ok) fetchReaders()
}
async function addBook(e){
  e.preventDefault();
  const fd = Object.fromEntries(new FormData(e.target));
  if(!fd.title || fd.title.trim()===''){ setInlineMsg('bookMsg','书名为必填'); return }
  const total = parseInt(fd.total_copies)||1
  const avail = parseInt(fd.available_copies)||total
  if(total <= 0){ setInlineMsg('bookMsg','库存必须大于 0'); return }
  if(avail < 0 || avail > total){ setInlineMsg('bookMsg','可借数必须在 0 到 库存 之间'); return }
  const res = await api('/books','POST',{title:fd.title, author:fd.author, total_copies:total, available_copies:avail});
  showMessage(res);
  setInlineMsg('bookMsg','');
  if(res.ok) fetchBooks()
}

function validateBorrowForm(fd){
  if(!fd.reader_id) { setInlineMsg('borrowMsg','请选择读者'); return false }
  if(!fd.book_id) { setInlineMsg('borrowMsg','请选择图书'); return false }
  const book = booksCache.find(b => String(b.book_id) === String(fd.book_id))
  if(!book) { setInlineMsg('borrowMsg','图书不存在'); return false }
  if(book.available_copies <= 0){ setInlineMsg('borrowMsg','该图书当前不可借'); return false }
  if(!fd.due_date) { setInlineMsg('borrowMsg','请选择应还日期'); return false }
  setInlineMsg('borrowMsg','');
  return true
}

async function doBorrow(e){
  e.preventDefault();
  const fd = Object.fromEntries(new FormData(e.target));
  if(!validateBorrowForm(fd)) return;
  const res = await api('/borrow','POST',{reader_id:parseInt(fd.reader_id), book_id:parseInt(fd.book_id), due_date:fd.due_date});
  showMessage(res);
  if(res.ok){ fetchBooks(); fetchLoans(); }
}

function validateReturnForm(fd){
  if(!fd.loan_id || parseInt(fd.loan_id) <= 0){ setInlineMsg('returnMsg','请输入有效的 loan_id'); return false }
  if(!fd.return_date){ setInlineMsg('returnMsg','请选择归还日期'); return false }
  setInlineMsg('returnMsg','');
  return true
}

async function doReturn(e){
  e.preventDefault();
  const fd = Object.fromEntries(new FormData(e.target));
  if(!validateReturnForm(fd)) return;
  const res = await api('/return','POST',{loan_id:parseInt(fd.loan_id), return_date:fd.return_date});
  showMessage(res);
  if(res.ok){ fetchBooks(); fetchLoans(); }
}

function showMessage(res){ const box = $('message'); if(!box) return; box.style.display='block'; if(!res.ok){ box.className='message error'; box.textContent = res.json?.error || res.text || `Error ${res.status}` }else{ box.className='message success'; box.textContent = res.json?.msg || 'OK' } setTimeout(()=>box.textContent='',4000) }

window.addEventListener('DOMContentLoaded', ()=>{
  $('formAddReader').addEventListener('submit', addReader)
  $('formAddBook').addEventListener('submit', addBook)
  $('formBorrow').addEventListener('submit', doBorrow)
  $('formReturn').addEventListener('submit', doReturn)
  fetchReaders(); fetchBooks(); fetchLoans()
})