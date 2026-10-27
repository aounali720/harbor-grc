"use strict";
(() => {
  const $ = (id) => document.getElementById(id);
  const state = {user:null, csrf:"", workspace:{}, schemas:{}, data:{}, metrics:{}, view:"dashboard", editing:null, toastTimer:null, frameworks:{catalog:null,mappings:null,coverage:null,errors:[]}};
  let frameworkRequest=0;
  const kinds = ["risks","controls","vendors","assets","evidence","findings"];
  const meta = {
    risks:{name:"Risk register",singular:"risk",eyebrow:"Governance",description:"Record what could go wrong, who owns the risk, and how you plan to respond.",help:"Scores use a 1–5 ordinal scale. Residual scores require rationale and a review date. A second person must accept a risk."},
    controls:{name:"Control library",singular:"control",eyebrow:"Governance",description:"Keep each control’s owner, test procedure, and evidence in one place.",help:"Create a control as planned or implemented. Effective status requires a test procedure and current evidence approved by another user."},
    vendors:{name:"Vendor risk",singular:"vendor",eyebrow:"Third-party assurance",description:"Review vendors based on the service they provide, the data they handle, and the access they have.",help:"Tier is derived from inherent exposure. Approval or conditional approval requires assurance notes and a next review date. Questionnaire scores do not automatically reduce risk."},
    assets:{name:"Cloud & assets",singular:"asset",eyebrow:"Cloud assurance",description:"Track the cloud resources and SaaS services included in your assessment.",help:"Use sanitized resource identifiers in this portfolio. This inventory does not connect to or scan your cloud accounts."},
    evidence:{name:"Evidence",singular:"evidence record",eyebrow:"Assurance",description:"Record where evidence came from, when it expires, and who reviewed it.",help:"Only metadata is stored. Keep the artifact in your approved repository and supply its HTTPS reference and SHA-256 hash. Create as pending; a different user can approve it with review notes."},
    findings:{name:"Findings",singular:"finding",eyebrow:"Remediation",description:"Assign gaps to an owner and track the work needed to close them.",help:"Closure requires remediation notes and current approved evidence. Risk acceptance must reference a currently accepted risk. Cloud imports never make an assurance decision for you."}
  };
  const hiddenFields = new Set(["residual_reviewed_by","reviewed_by","acceptance_approver","submitted_by","source_updated_at"]);
  const longFields = new Set(["description","test_procedure","assurance_notes","review_notes","acceptance_rationale","residual_rationale","remediation"]);
  const refKinds = {control_id:"controls",control_ids:"controls",risk_id:"risks",vendor_id:"vendors",asset_id:"assets",evidence_id:"evidence"};
  const hints = {
    likelihood:"1 rare · 2 unlikely · 3 possible · 4 likely · 5 almost certain",
    impact:"1 negligible · 2 minor · 3 material · 4 major · 5 severe",
    residual_likelihood:"Leave both residual scores blank until a documented review.",
    residual_impact:"A reviewed estimate, never an automatic control discount.",
    residual_review_date:"Date the residual risk judgment was made.",
    acceptance_expires:"Must be in the future. Expired acceptance returns to the oversight queue.",
    framework_refs:"One identifier per line. Browse selected suggestions below or enter a custom reference. Mappings are illustrative.",
    uri:"Stable HTTPS reference, without credentials or query parameters. The server does not fetch it.",
    sha256:"Exactly 64 lowercase hexadecimal characters, calculated from the original artifact.",
    expires_on:"Evidence supports assurance only while current and independently approved.",
    frequency_days:"Control test cadence in days. Choose a schedule justified by risk.",
    review_date:"Next vendor reassessment date.",
    source_key:"Optional external identifier. Cloud imports use it to recognize repeat findings.",
    questionnaire_score:"0–100. A triage input; it is not a compliance or assurance rating.",
    control_ids:"Select all applicable controls. Hold Ctrl or Command to select multiple."
  };
  function el(tag, cls, text) { const n = document.createElement(tag); if(cls) n.className=cls; if(text !== undefined) n.textContent=text; return n; }
  function add(parent, ...children) { children.flat().forEach(c=>{if(c!==null && c!==undefined) parent.append(c);}); return parent; }
  function textLabel(value) { return String(value??"").replaceAll("_"," ").replace(/^\w/,c=>c.toUpperCase()); }
  function announce(text) { $("live-status").textContent=text; }
  function toast(message,error=false) {clearTimeout(state.toastTimer); $("toast").textContent=message; $("toast").classList.toggle("error",error); $("toast").hidden=false; announce(message); state.toastTimer=setTimeout(()=>$("toast").hidden=true,error?10000:5000);}
  function errorMessage(detail) {
    if(Array.isArray(detail)) return detail.map(item=>((item.loc||[]).filter(x=>x!=="body").join(" · ")+(item.loc?.length?": ":"")+(item.msg||"Invalid value"))).join("\n");
    return typeof detail==="string" ? detail : "The request could not be completed.";
  }
  async function api(path, options={}) {
    const headers = new Headers(options.headers||{});
    if(options.body !== undefined) headers.set("Content-Type","application/json");
    if(options.method && !["GET","HEAD"].includes(options.method)) headers.set("X-CSRF-Token",state.csrf);
    let response;
    try { response=await fetch(path,{credentials:"same-origin",...options,headers}); }
    catch { throw new Error("Cannot reach the server. Check the connection and try again."); }
    let body = null; const type=response.headers.get("content-type")||"";
    if(type.includes("json")) {try {body=await response.json();} catch {}}
    if(!response.ok) {
      if(response.status===401 && path!=="/api/auth/login" && state.user) {showLogin(); toast("Your session has ended. Please sign in again.",true);}
      const error=new Error(errorMessage(body?.detail||body?.message||"Request failed ("+response.status+")."));
      error.status=response.status; throw error;
    }
    return body;
  }
  function writeAllowed() { return state.user?.role==="admin" || state.user?.role==="analyst"; }
  function showLogin() {frameworkRequest++;state.user=null;state.csrf="";state.data={};state.frameworks={catalog:null,mappings:null,coverage:null,errors:[]};$("workspace").hidden=true;$("login-view").hidden=false;$("password").value="";document.title="Sign in · Harbor GRC";$("username").focus();}
  async function enterWorkspace(session) {
    state.user=session.user; state.csrf=session.csrf_token; state.workspace=session.workspace||{};
    $("user-name").textContent=state.user.username; $("user-role").textContent=state.user.role;
    $("user-avatar").textContent=state.user.username.slice(0,1).toUpperCase();
    $("workspace-name").textContent=state.workspace.name||"Assurance workspace";
    $("demo-badge").hidden=!state.workspace.demo;
    $("login-view").hidden=true;$("workspace").hidden=false;
    $("content").replaceChildren(el("p","loading","Opening your workspace…"));
    await loadData(); await renderView();
  }
  async function loadData() {
    const user=state.user;
    const results=await Promise.all([api("/api/schema"),api("/api/dashboard"),...kinds.map(k=>api("/api/"+k))]);
    if(state.user!==user)return;
    state.schemas=results[0].kinds; state.metrics=results[1];
    kinds.forEach((kind,i)=>state.data[kind]=results[i+2].items||[]);
    document.querySelectorAll("[data-count]").forEach(n=>n.textContent=state.data[n.dataset.count].length);
    await loadFrameworkData();
  }
  function viewFromHash() { const v=location.hash.slice(1);return kinds.includes(v)||v==="audit"||v==="frameworks"?v:"dashboard"; }
  function pageHeading(title,description,eyebrow,actions) {
    const heading=el("div","page-heading"); const copy=el("div");
    add(copy,el("p","eyebrow",eyebrow),el("h1","",title),el("p","",description));heading.append(copy);
    if(actions) heading.append(actions); return heading;
  }
  function button(text,cls,handler) {const b=el("button","button "+cls,text);b.type="button";if(handler)b.addEventListener("click",handler);return b;}
  function makeLink(text,view,cls="panel-link") {const a=el("a",cls,text);a.href="#"+view;return a;}
  function dateText(value,includeTime=false) {
    if(!value)return "Not set";
    const d=new Date(value.length===10 ? value+"T00:00:00Z" : value);
    if(Number.isNaN(d.getTime()))return value;
    return new Intl.DateTimeFormat(undefined,{day:"numeric",month:"short",year:"numeric",...(includeTime?{hour:"2-digit",minute:"2-digit"}:{}),timeZone:"UTC"}).format(d)+(includeTime?" UTC":"");
  }
  function today(){return new Date().toISOString().slice(0,10);}
  function isOverdue(date){return Boolean(date&&date<today());}
  function badge(value) {
    const good=["effective","approved","closed"]; const bad=["critical","ineffective","rejected","expired"];
    const warn=["high","conditional","in_treatment","in_progress","pending","risk_accepted","accepted"];
    const cls=good.includes(value)?"good":bad.includes(value)?"bad":warn.includes(value)?"warn":["implemented","due_diligence","screening"].includes(value)?"info":"neutral";
    return el("span","pill "+cls,textLabel(value||"Not set"));
  }
  function riskBand(score){return score>=20?"critical":score>=12?"high":score>=6?"moderate":"low";}
  function scoreNode(score){const n=el("span","score-box "+riskBand(score),String(score));n.title="Ordinal likelihood × impact score";return n;}
  function vendorTier(v){return v.criticality==="critical"||v.data_sensitivity==="restricted"||v.access_level==="privileged"?"tier_1":v.criticality==="high"||v.data_sensitivity==="confidential"?"tier_2":"tier_3";}
  function panelHeader(title,description,link) {const h=el("div","panel-header");const c=el("div");add(c,el("h2","",title),description?el("p","",description):null);add(h,c,link);return h;}
  function metric(label,value,note,icon,cls="") {const box=el("article","metric-card "+cls);add(box,add(el("div","metric-top"),el("span","",label),el("span","metric-icon",icon)),el("div","metric-value",String(value)),el("div","metric-footer",note));return box;}

  function renderDashboard() {
    const d=state.metrics;const content=$("content");const actions=el("div","date-label","As of "+dateText(d.as_of||new Date().toISOString()));
    content.append(pageHeading("Assurance, at a glance.","Your shared view of exposure, evidence, and the work that needs attention.","Workspace overview",actions));
    const scope=el("div","scope-banner");const scopeLabel=el("div","scope-label");add(scopeLabel,el("span","","↗"),el("strong","","Three domains. One risk picture."));
    const domains=el("div","scope-domains");[["01","SaaS governance"],["02","Cloud assurance"],["03","Vendor risk"]].forEach(([num,name])=>add(domains,add(el("div","scope-domain"),el("b","",num),el("span","",name))));
    add(scope,scopeLabel,el("span","scope-subtext",state.workspace.demo?"Northstar Metrics · fictional scenario":"Connected through shared controls and evidence"),domains);content.append(scope);
    const metricGrid=el("div","metric-grid");
    const openRisks=d.open_risks??state.data.risks.filter(r=>r.status!=="closed").length;
    const applicable=d.applicable_controls??state.data.controls.filter(c=>c.status!=="not_applicable").length;
    const effective=d.evidence_backed_effective_controls??0;
    const tier1=d.vendor_tiers?.tier_1??state.data.vendors.filter(v=>vendorTier(v)==="tier_1").length;
    add(metricGrid,metric("Open risks",openRisks,(d.high_inherent_risks??0)+" rated high or critical","◇","warning"),metric("Evidence-backed controls",effective+" / "+applicable,"Current evidence · applicable controls","▣","accent"),metric("Tier 1 vendors",tier1,"Critical, restricted-data, or privileged","▱"),metric("Overdue findings",d.overdue_findings??0,(d.open_findings??0)+" findings remain open","⚑",(d.overdue_findings??0)>0?"warning":""));content.append(metricGrid);
    const grid=el("div","dashboard-grid");const heat=el("section","panel");
    add(heat,panelHeader("Inherent risk distribution","Before considering the effect of controls.",el("span","small-tag","5 × 5 assessment")));
    const layout=el("div","heatmap-layout"), plot=el("div","heatmap-plot");plot.setAttribute("role","img");plot.setAttribute("aria-label","Risk heatmap. Likelihood runs from 1 at the bottom to 5 at the top, impact from 1 to 5 from left to right.");
    for(let l=5;l>=1;l--) {
      plot.append(el("span","heatmap-axis",String(l)));
      for(let i=1;i<=5;i++) {
        const count=d.inherent_heatmap?.[l-1]?.[i-1]??state.data.risks.filter(r=>r.likelihood===l&&r.impact===i&&r.status!=="closed").length;
        const cell=el("div","heatmap-cell "+riskBand(l*i)+(count?" has-risk":""),count?String(count):"");
        cell.title="Likelihood "+l+", impact "+i+": "+count+" risk"+(count===1?"":"s");plot.append(cell);
      }
    }
    plot.append(el("span"));for(let i=1;i<=5;i++)plot.append(el("span","heatmap-axis",String(i)));
    add(layout,el("div","heatmap-y-label","Likelihood"),plot);heat.append(layout,el("div","heatmap-x-label","Business impact"));
    const legend=el("div","heatmap-legend");[["low","Low 1–5"],["moderate","Medium 6–11"],["high","High 12–19"],["critical","Critical 20–25"]].forEach(([cls,name])=>add(legend,add(el("span"),el("i","legend-"+cls),document.createTextNode(name))));heat.append(legend);
    const assurance=el("section","panel");assurance.append(panelHeader("Attention & follow-through","A practical queue for the next assurance review.",makeLink("Open findings ↗","findings")));
    const items=el("div","assurance-list");
    [["▤","Evidence awaiting review","Independent review before assurance credit",d.pending_evidence??0],["◷","Expired evidence","Refresh the artifact and repeat the test",d.expired_evidence??0],["▱","Vendor reviews overdue","Revisit assurance and service dependency",d.overdue_vendor_reviews??0],["◇","Residual risk not reviewed","Document the judgment behind the score",d.unreviewed_residual_risks??0]].forEach(([icon,title,desc,n])=>{
      add(items,add(el("div","assurance-row"),el("span","assurance-icon",icon),add(el("div","assurance-copy"),el("strong","",title),el("p","",desc)),el("span","assurance-number",String(n))));
    });
    add(assurance,items,el("div","assurance-bottom",(d.stale_effective_control_ids?.length??0)+" effective controls and "+(d.stale_closed_finding_ids?.length??0)+" closed findings have stale supporting evidence."));add(grid,heat,assurance);content.append(grid);
    const priority=[...state.data.risks].filter(r=>r.status!=="closed").sort((a,b)=>(b.likelihood*b.impact)-(a.likelihood*a.impact)).slice(0,5);
    const riskPanel=el("section","panel");riskPanel.append(panelHeader("Risks worth a closer look","Highest inherent exposure among open records.",makeLink("View risk register ↗","risks")),makeTable("risks",priority,true));
    const foot=el("div","table-foot");add(foot,el("span","",priority.length+" of "+openRisks+" open risk records"),el("span","","Residual scores reflect an explicit review."));riskPanel.append(foot);content.append(riskPanel);
    const strip=el("div","insight-strip");add(strip,el("span","","i"),el("p","",state.workspace.demo?"You are viewing synthetic sample data for Northstar Metrics. Evidence references are fictional; the sample illustrates decisions and gaps, not a completed audit.":"Control coverage reflects this register and current approved evidence. It does not establish control effectiveness across an entire organization."));content.append(strip);
  }
  function ownerNode(value){return add(el("span","owner-cell"),el("span","owner-initial",String(value||"?").split(" ").map(s=>s[0]).slice(0,2).join("").toUpperCase()),el("span","",value||"Unassigned"));}
  function dateNode(value,checkOverdue=true){const n=el("span",checkOverdue&&isOverdue(value)?"overdue":"",dateText(value));if(checkOverdue&&isOverdue(value))n.title="Overdue";return n;}
  function titleCell(kind,record) {
    const b=el("button","record-link");b.type="button";b.setAttribute("aria-label",(writeAllowed()?"Edit ":"View ")+record.title);
    add(b,el("span","record-title",record.title),el("span","record-id",record.id));b.addEventListener("click",()=>openRecord(kind,record));return b;
  }
  function referenceTitle(kind,id){return state.data[kind]?.find(r=>r.id===id)?.title||id||"Not linked";}
  function tableColumns(kind,compact=false) {
    const base=[{name:kind==="risks"?"Risk":kind==="evidence"?"Artifact":"Record",render:r=>titleCell(kind,r)}];
    const owner={name:"Owner",render:r=>ownerNode(r.owner)},status={name:"Status",render:r=>badge(r.status)};
    if(kind==="risks") return [...base,{name:"Category",render:r=>textLabel(r.category)},{name:"Inherent → residual",render:r=>{const pair=el("div","score-pair");add(pair,scoreNode(r.likelihood*r.impact),el("span","","→"),r.residual_likelihood===null||r.residual_likelihood===undefined?el("span","","Unreviewed"):scoreNode(r.residual_likelihood*r.residual_impact));return pair;}},owner,...(compact?[]:[{name:"Review / due",render:r=>dateNode(r.due_date)}]),status];
    if(kind==="controls")return [...base,{name:"Domain",render:r=>textLabel(r.domain)},{name:"Framework references",render:r=>r.framework_refs.join(" · ")||"Unmapped"},owner,status];
    if(kind==="vendors")return [...base,{name:"Service",render:r=>r.service},{name:"Inherent tier",render:r=>badge(vendorTier(r))},{name:"Next review",render:r=>dateNode(r.review_date)},owner,status];
    if(kind==="assets")return [...base,{name:"Provider",render:r=>r.provider},{name:"Environment",render:r=>textLabel(r.environment)},{name:"Data classification",render:r=>badge(r.data_classification)},{name:"Criticality",render:r=>badge(r.criticality)},owner];
    if(kind==="evidence")return [...base,{name:"Control",render:r=>referenceTitle("controls",r.control_id)},{name:"Expires",render:r=>dateNode(r.expires_on)},{name:"Reviewer",render:r=>r.reviewed_by||"Awaiting review"},owner,status];
    return [...base,{name:"Severity",render:r=>badge(r.severity)},{name:"Due date",render:r=>dateNode(r.due_date)},{name:"Linked risk",render:r=>referenceTitle("risks",r.risk_id)},owner,status];
  }
  function makeTable(kind,records,compact=false) {
    if(records.length===0){const empty=el("div","empty-state");add(empty,el("h3","","No records to show"),el("p","","Create a record or adjust the current filter."));return empty;}
    const wrap=el("div","table-scroll"),table=el("table");table.setAttribute("aria-label",meta[kind].name);const columns=tableColumns(kind,compact);const thead=el("thead"),tr=el("tr");
    columns.forEach(c=>{const th=el("th","",c.name);th.scope="col";tr.append(th);});thead.append(tr);table.append(thead);
    const tbody=el("tbody");records.forEach(record=>{const row=el("tr");columns.forEach(col=>{const td=el("td");const value=col.render(record);td.append(value instanceof Node?value:document.createTextNode(String(value??"")));row.append(td);});tbody.append(row);});table.append(tbody);wrap.append(table);return wrap;
  }
  function renderRegister(kind) {
    const content=$("content"),m=meta[kind],actions=el("div","heading-actions");
    if((kind==="assets"||kind==="findings")&&writeAllowed())actions.append(button("↑ Import cloud JSON","button-secondary",()=>{$("import-error").hidden=true;$("import-dialog").showModal();}));
    if(writeAllowed())actions.append(button("+ Add "+m.singular,"button-primary",()=>openRecord(kind)));
    content.append(pageHeading(m.name,m.description,m.eyebrow,actions));
    const panel=el("section","panel"),toolbar=el("div","table-toolbar"),search=el("div","search-box"),input=el("input");
    input.type="search";input.placeholder="Search "+m.name.toLowerCase()+"…";input.setAttribute("aria-label","Search "+m.name.toLowerCase());add(search,el("span","","⌕"),input);
    const controls=el("div","toolbar-controls"),statusFilter=el("select","filter-select");statusFilter.setAttribute("aria-label","Filter by status");const all=el("option","","All statuses");all.value="";statusFilter.append(all);
    const values=[...new Set(state.data[kind].map(r=>r.status).filter(Boolean))].sort();
    values.forEach(s=>{const o=el("option","",textLabel(s));o.value=s;statusFilter.append(o);});
    const count=el("span","table-meta");if(values.length)controls.append(statusFilter);controls.append(count);add(toolbar,search,controls);panel.append(toolbar);
    const holder=el("div");panel.append(holder);const foot=el("div","table-foot");add(foot,el("span","",writeAllowed()?"Select a record to review or edit its details.":"Auditor access · records are read-only."),el("span","","All dates use UTC."));panel.append(foot);content.append(panel);
    const redraw=()=>{const query=input.value.trim().toLowerCase();const records=state.data[kind].filter(r=>(!statusFilter.value||r.status===statusFilter.value)&&(!query||[r.title,r.id,r.owner,r.description,r.domain,r.category,r.service,r.provider].some(v=>String(v||"").toLowerCase().includes(query))));holder.replaceChildren(makeTable(kind,records));count.textContent=records.length+" records";};
    input.addEventListener("input",redraw);statusFilter.addEventListener("change",redraw);redraw();
    content.append(el("p","detail-note"));content.lastChild.textContent=m.help;
  }
  async function renderAudit(){
    const content=$("content");content.append(pageHeading("Activity & audit","Inspect who changed a record and verify the continuity of the audit chain.","Oversight",add(el("div","heading-actions"),button("↻ Refresh","button-secondary",()=>renderView()))));
    const data=await api("/api/audit"),v=data.verification||{};if(state.view!=="audit")return;const summary=el("div","audit-summary"+(v.valid?"":" bad"));
    add(summary,el("span","",v.valid?"✓":"!"),el("div","",(v.valid?"Audit chain verified":"Audit chain verification failed")+" · "+(v.count??data.items.length)+" events. "+(v.valid?"Keep an external trusted checkpoint to detect truncation or a complete rewrite.":"Investigate the database and compare against a trusted checkpoint.")));content.append(summary);
    const panel=el("section","panel");panel.append(panelHeader("Recent activity","Records are shown newest first. Audit details deliberately exclude record contents.",el("span","small-tag","SHA-256 chain")));
    if(!data.items.length)panel.append(el("div","empty-state","No audit events yet."));
    else {const wrap=el("div","table-scroll"),table=el("table"),head=el("thead"),row=el("tr");["Sequence","Time (UTC)","Actor","Action","Target","Details"].forEach(t=>{const th=el("th","",t);th.scope="col";row.append(th);});head.append(row);table.append(head);const body=el("tbody");
      data.items.forEach(item=>{const tr=el("tr");[item.seq,dateText(item.timestamp,true),item.actor,textLabel(item.action),item.target,JSON.stringify(item.details)].forEach((value,i)=>{const td=el("td",i===5?"audit-details":"",String(value??""));if(i===5)td.title=String(value);tr.append(td);});body.append(tr);});table.append(body);wrap.append(table);panel.append(wrap);}
    panel.append(el("div","table-foot","Head checkpoint: "+(v.head_hash||"Unavailable")));content.append(panel);
  }
  async function renderView() {
    if(!state.user)return;state.view=viewFromHash();const content=$("content");content.replaceChildren();content.setAttribute("aria-busy","true");
    document.querySelectorAll("#main-nav [data-view]").forEach(a=>{const active=a.dataset.view===state.view;a.classList.toggle("active",active);if(active)a.setAttribute("aria-current","page");else a.removeAttribute("aria-current");});
    const title=state.view==="dashboard"?"Overview":state.view==="audit"?"Activity & audit":state.view==="frameworks"?"Frameworks":meta[state.view].name;$("breadcrumb-title").textContent=title;document.title=title+" · Harbor GRC";
    try {if(state.view==="dashboard")renderDashboard();else if(state.view==="audit")await renderAudit();else if(state.view==="frameworks")renderFrameworks();else renderRegister(state.view);}
    catch(error){const empty=el("div","empty-state");add(empty,el("h2","","This view could not be loaded"),el("p","",error.message),button("Try again","button-secondary",()=>renderView()));content.replaceChildren(empty);}
    finally{content.setAttribute("aria-busy","false");announce(title+" loaded");}
  }

  function frameworkText(value) {
    if(Array.isArray(value))return value.map(frameworkText).join(" · ");
    if(value && typeof value==="object")return Object.entries(value).map(([key,text])=>textLabel(key)+": "+frameworkText(text)).join(" · ");
    return String(value??"");
  }
  function officialLink(url,label="Official publication ↗",context="") {
    try {
      const parsed=new URL(url);
      if(parsed.protocol!=="https:"||parsed.username||parsed.password)return el("span","muted","Official source unavailable");
      const a=el("a","framework-source",label);a.href=parsed.href;a.target="_blank";a.rel="noopener noreferrer";a.setAttribute("aria-label",(context?context+": ":"")+label.replace(" ↗","")+" (opens in a new tab)");return a;
    } catch {return el("span","muted","Official source unavailable");}
  }
  async function loadFrameworkData() {
    const user=state.user,requestId=++frameworkRequest;
    const paths=["/api/frameworks","/api/frameworks/mappings","/api/frameworks/coverage"];
    const results=await Promise.allSettled(paths.map(path=>api(path)));
    const empty={catalog:null,mappings:null,coverage:null,errors:[]};
    ["catalog","mappings","coverage"].forEach((key,i)=>{
      if(results[i].status==="fulfilled" && results[i].value && Array.isArray(results[i].value.items))empty[key]=results[i].value;
      else empty.errors.push(key==="catalog"?"Publication catalog could not be loaded.":key==="mappings"?"Topic mappings are temporarily unavailable.":"Local coverage counts are temporarily unavailable.");
    });
    if(requestId===frameworkRequest&&state.user===user)state.frameworks=empty;
  }
  function referencePicker(input) {
    const details=el("details","reference-picker"),summary=el("summary","","Browse reference suggestions");details.append(summary);
    const body=el("div","reference-picker-body");body.append(el("p","muted","Selected topic examples only. Add a reference below or enter your own identifier in the field above."));
    const mappingRows=state.frameworks?.mappings?.items||[];
    const catalog=state.frameworks?.catalog?.items||[];
    const seen=new Set(),links=[];
    mappingRows.forEach(row=>(row.links||[]).forEach(link=>{
      if(link.reference&&!seen.has(link.reference)){seen.add(link.reference);links.push(link);}
    }));
    if(!links.length){body.append(el("p","muted","Suggestions are unavailable. Custom references can still be entered and saved."));details.append(body);return details;}
    const select=el("select");select.setAttribute("aria-label","Suggested framework reference");
    const blank=el("option","","Choose a reference…");blank.value="";select.append(blank);
    catalog.forEach(framework=>{
      const group=el("optgroup");group.label=framework.name;
      links.filter(link=>link.framework_id===framework.id).forEach(link=>{const option=el("option","",link.reference+" · "+link.topic);option.value=link.reference;group.append(option);});
      if(group.children.length)select.append(group);
    });
    links.filter(link=>!catalog.some(item=>item.id===link.framework_id)).forEach(link=>{const option=el("option","",link.reference+" · "+link.topic);option.value=link.reference;select.append(option);});
    const description=el("p","reference-description","Select an identifier to inspect the mapping rationale.");
    const source=el("div","reference-source");
    const appendButton=button("Add reference","button-secondary",()=>{
      if(!select.value)return;
      const values=input.value.split(/\r?\n/).map(value=>value.trim()).filter(Boolean);
      if(!values.includes(select.value)){values.push(select.value);input.value=values.join("\n");input.dispatchEvent(new Event("input",{bubbles:true}));announce("Reference added to the control form.");}
      else announce("That reference is already listed.");
    });
    appendButton.disabled=true;
    select.addEventListener("change",()=>{
      const link=links.find(item=>item.reference===select.value);appendButton.disabled=!link;
      description.textContent=link?link.topic+" · "+link.relationship+". "+link.rationale:"Select an identifier to inspect the mapping rationale.";
      source.replaceChildren();if(link)source.append(officialLink(link.source_url,"Reference source ↗",link.reference));
    });
    const row=add(el("div","reference-picker-row"),select,appendButton);add(body,row,description,source);details.append(body);return details;
  }
  function renderFrameworks() {
    const content=$("content"),library=state.frameworks||{},catalog=library.catalog?.items||[],mappings=library.mappings?.items||[],coverage=library.coverage;
    const refresh=button("↻ Refresh library","button-secondary",async()=>{
      refresh.disabled=true;
      try {await loadData();if(state.view==="frameworks")await renderView();}
      catch(error){toast(error.message,true);}
      finally {refresh.disabled=false;}
    });
    const actions=add(el("div","heading-actions"),refresh);
    content.append(pageHeading("Frameworks","Find a publication, review its scope, and see the local controls linked to it.","Reference library",actions));
    const intro=el("div","framework-intro");
    const introCopy=add(el("div"),el("strong","","A reference library, with a defined scope."),el("p","","CSF outcomes, NIST risk-management publications, and ISO/IEC standards serve different purposes. The crosswalk below covers selected topics; it is not an equivalence determination or a complete assessment."));
    add(intro,introCopy,el("span","small-tag",catalog.length+" publications"));content.append(intro);
    if(library.errors?.length){
      const notice=el("div","framework-notice");notice.setAttribute("role","status");notice.textContent=library.errors.join(" ")+" Other registries remain available.";content.append(notice);
    }
    if(!catalog.length){
      const empty=el("section","panel empty-state");add(empty,el("h2","","No publication records available"),el("p","","Refresh the library to try again. Risk and control records remain available from the sidebar."));content.append(empty);return;
    }
    const panel=el("section","panel framework-library"),toolbar=el("div","table-toolbar"),search=el("div","search-box"),query=el("input");
    query.type="search";query.placeholder="Search frameworks, editions, or purpose…";query.setAttribute("aria-label","Search frameworks");
    add(search,el("span","","⌕"),query);
    const publisher=el("select","filter-select");publisher.setAttribute("aria-label","Filter frameworks by publisher");const all=el("option","","All publishers");all.value="";publisher.append(all);
    [...new Set(catalog.map(item=>item.publisher))].sort().forEach(name=>{const option=el("option","",name);option.value=name;publisher.append(option);});
    const count=el("span","table-meta");count.setAttribute("role","status");count.setAttribute("aria-live","polite");const tools=add(el("div","toolbar-controls"),publisher,count);add(toolbar,search,tools);panel.append(toolbar);
    if(coverage?.scope){const scope=el("details","framework-count-scope");add(scope,el("summary","","How local counts are calculated"),el("p","",coverage.scope));panel.append(scope);}
    const grid=el("div","framework-grid");panel.append(grid);
    const checked=library.catalog.checked_on?dateText(library.catalog.checked_on):"Not recorded";
    const catalogFoot=el("div","table-foot");add(catalogFoot,el("span","","Catalog "+(library.catalog.catalog_version||"unversioned")+" · checked "+checked),el("span","",coverage?"Local mapping snapshot: "+dateText(coverage.as_of):"Local mapping counts unavailable"));panel.append(catalogFoot);content.append(panel);
    const crosswalk=el("section","panel framework-crosswalk");
    crosswalk.append(panelHeader("Illustrative control-topic crosswalk","Explore a selected library topic. Local associations below require an exact stored reference match.",el("span","small-tag","Partial mapping")));
    const controls=el("div","framework-crosswalk-tools"),topicField=el("div","field"),frameworkField=el("div","field");
    const topicLabel=el("label","","Library control topic");topicLabel.htmlFor="framework-topic";const topicSelect=el("select");topicSelect.id="framework-topic";
    mappings.forEach((row,i)=>{const option=el("option","",row.title+" · "+row.control_key);option.value=String(i);topicSelect.append(option);});
    topicSelect.disabled=!mappings.length;
    const scopeLabel=el("label","","Limit links to a publication");scopeLabel.htmlFor="framework-scope";const scopeSelect=el("select");scopeSelect.id="framework-scope";
    const any=el("option","","All publications");any.value="";scopeSelect.append(any);catalog.forEach(item=>{const option=el("option","",item.name);option.value=item.id;scopeSelect.append(option);});
    add(topicField,topicLabel,topicSelect);add(frameworkField,scopeLabel,scopeSelect);add(controls,topicField,frameworkField);crosswalk.append(controls);
    const linkHolder=el("div","framework-mapping-list"),localHolder=el("div","framework-local-list"),mappingStatus=el("p","sr-only");
    mappingStatus.setAttribute("role","status");mappingStatus.setAttribute("aria-live","polite");add(crosswalk,mappingStatus,linkHolder,localHolder);content.append(crosswalk);
    const limitations=frameworkText(library.catalog.limitations);
    const note=el("div","insight-strip");add(note,el("span","","i"),el("p","",limitations||"These links support local assessment planning. ISO/IEC normative content is not reproduced here. Use the relevant official publication and licensed standards when determining requirements."));content.append(note);
    if(coverage?.unknown_references?.length){
      const unknown=el("details","framework-unrecognized");unknown.append(el("summary","",coverage.unknown_references.length+" stored references are outside this catalog"));
      unknown.append(el("p","muted","Custom references remain valid entries in the local register. They are excluded from this catalog’s mapping counts until a supported reference is selected."));
      const list=el("ul");coverage.unknown_references.forEach(item=>{const li=el("li");add(li,el("code","",item.reference),document.createTextNode(" · "+item.control_id));list.append(li);});unknown.append(list);content.append(unknown);
    }
    const cardNodes=[];
    function drawCards(){
      const terms=query.value.trim().toLowerCase().split(/\s+/).filter(Boolean);
      const records=catalog.filter(item=>{
        const searchable=[item.id,item.name,item.edition,item.publisher,item.summary,item.applicability,item.type,item.scope].map(frameworkText).join(" ").toLowerCase();
        return (!publisher.value||item.publisher===publisher.value)&&terms.every(term=>searchable.includes(term));
      });
      grid.replaceChildren();cardNodes.length=0;count.textContent=records.length+" publications";
      if(!records.length){grid.append(add(el("div","empty-state framework-empty"),el("h3","","No matching publications"),el("p","","Try a broader phrase or another publisher.")));return;}
      records.forEach(item=>{
        const card=el("article","framework-card"+(scopeSelect.value===item.id?" selected":""));cardNodes.push({id:item.id,node:card});
        const top=add(el("div","framework-card-top"),el("span","framework-publisher",item.publisher),el("span","framework-edition",item.edition));
        const title=el("h2","",item.name),purpose=el("p","framework-summary",item.summary);
        const detail=el("details","framework-applicability");detail.append(el("summary","",textLabel(item.type||"Publication")+" · when to use it"),el("p","",frameworkText(item.applicability)));
        if(item.scope)detail.append(el("p","muted","Catalog scope: "+frameworkText(item.scope)));
        if(item.related_sources?.length){
          const related=el("div","framework-related-sources");
          related.append(el("strong","","Related official sources"));
          item.related_sources.forEach((url,i)=>related.append(officialLink(url,"Related source "+(i+1)+" ↗",item.name+" "+item.edition)));
          detail.append(related);
        }
        const counts=coverage?.items?.find(row=>row.framework_id===item.id);
        const mapped=counts?.mapped_controls,backed=counts?.evidence_backed_controls;
        const numbers=el("div","framework-counts");
        function value(n){return typeof n==="number"?String(n):Array.isArray(n)?String(n.length):"—";}
        const mappedBox=add(el("div"),el("strong","",value(mapped)),el("span","","Local controls mapped"));
        const backedBox=add(el("div"),el("strong","",value(backed)),el("span","","Effective + current evidence"));add(numbers,mappedBox,backedBox);
        const note=el("p","framework-count-note","Selected references in this register · no full-framework coverage implied.");
        const hasLinks=mappings.some(row=>(row.links||[]).some(link=>link.framework_id===item.id));
        const footer=add(el("div","framework-card-footer"),officialLink(item.source_url,"Official publication ↗",item.name+" "+item.edition),button(hasLinks?"Explore links →":"View scope →","framework-explore",()=>{
          scopeSelect.value=item.id;
          const match=mappings.findIndex(row=>(row.links||[]).some(link=>link.framework_id===item.id));if(match>=0)topicSelect.value=String(match);
          updateCrosswalk();crosswalk.scrollIntoView({block:"start",behavior:"auto"});(hasLinks?topicSelect:scopeSelect).focus({preventScroll:true});
        }));
        add(card,top,title,purpose,detail,numbers,note,footer);grid.append(card);
      });
    }
    function updateCrosswalk(){
      cardNodes.forEach(({id,node})=>node.classList.toggle("selected",scopeSelect.value===id));
      linkHolder.replaceChildren();localHolder.replaceChildren();
      const referenceOnly=scopeSelect.value&&library.mappings&&!mappings.some(topic=>(topic.links||[]).some(link=>link.framework_id===scopeSelect.value));
      if(referenceOnly){const message="This publication is reference-only in the curated pack. No topic mappings or local mapping coverage are supplied for it.";linkHolder.append(el("p","empty-state",message));mappingStatus.textContent=message;return;}
      const row=mappings[Number(topicSelect.value)];
      if(!row){const message="Topic mappings are unavailable. Publication sources and local controls can still be reviewed.";linkHolder.append(el("p","empty-state",message));mappingStatus.textContent=message;return;}
      const links=(row.links||[]).filter(link=>!scopeSelect.value||link.framework_id===scopeSelect.value);
      if(!links.length)linkHolder.append(el("p","empty-state","This selected topic has no mapping to that publication in the partial crosswalk. Choose another topic or publication."));
      links.forEach(link=>{
        const framework=catalog.find(item=>item.id===link.framework_id),entry=el("article","framework-mapping");
        const head=add(el("div","framework-mapping-header"),el("code","",link.reference),el("span","small-tag",textLabel(link.relationship)));
        add(entry,head,el("h3","",link.topic),el("p","",link.rationale),add(el("div","framework-mapping-footer"),el("span","",framework?.name||link.framework_id),officialLink(link.source_url,"Reference source ↗",link.reference)));linkHolder.append(entry);
      });
      const exactRefs=new Set(links.map(link=>link.reference));
      const local=(state.data.controls||[]).filter(control=>(control.framework_refs||[]).some(reference=>exactRefs.has(reference)));
      mappingStatus.textContent=links.length+" partial reference links; "+local.length+" local controls contain the selected exact references.";
      add(localHolder,el("h3","","Local controls with these exact references"),el("p","muted","This association uses stored identifiers only. The library topic title does not establish that a live control implements a framework outcome."));
      if(!local.length)localHolder.append(el("p","framework-local-empty","No local controls contain these exact selected references."));
      local.forEach(control=>{
        const recordButton=el("button","framework-local-control");recordButton.type="button";recordButton.setAttribute("aria-label",(writeAllowed()?"Edit ":"View ")+control.title);
        add(recordButton,add(el("span"),el("strong","",control.title),el("span","record-id",control.id)),badge(control.status),el("span","framework-local-arrow","↗"));recordButton.addEventListener("click",()=>openRecord("controls",control));localHolder.append(recordButton);
      });
    }
    query.addEventListener("input",drawCards);publisher.addEventListener("change",drawCards);topicSelect.addEventListener("change",updateCrosswalk);scopeSelect.addEventListener("change",updateCrosswalk);drawCards();updateCrosswalk();
  }


  function resolveSchema(property){return property.anyOf?.find(s=>s.type!=="null")||property;}
  function openRecord(kind,record=null){
    state.editing={kind,record};const schema=state.schemas[kind];if(!schema){toast("The record schema could not be loaded.",true);return;}
    const readOnly=!writeAllowed();$("record-dialog-eyebrow").textContent=record?(readOnly?"Record details":"Edit record"):"New record";
    $("record-dialog-title").textContent=(record?(readOnly?"View ":"Edit "):"Create ")+meta[kind].singular;
    $("record-form-help").textContent=meta[kind].help;$("record-error").hidden=true;$("record-fields").replaceChildren();
    const required=new Set(schema.required||[]);
    for(const [key,property] of Object.entries(schema.properties||{})) {
      if(hiddenFields.has(key))continue;
      const p=resolveSchema(property),field=el("div","field"+(longFields.has(key)||key==="title"||key==="uri"||key==="framework_refs"||key==="control_ids"?" full-width":""));
      const label=el("label","",key==="uri"?"Artifact URL":key==="sha256"?"SHA-256":textLabel(key));label.htmlFor="field-"+key;
      if(required.has(key))label.append(el("span","required-star","*"));else label.append(el("span","optional","optional"));
      let input;const ref=refKinds[key],isArray=p.type==="array";
      if(ref){input=el("select");if(isArray)input.multiple=true;else{const blank=el("option","","Select a record…");blank.value="";input.append(blank);}
        state.data[ref].forEach(r=>{const option=el("option","",r.title+" · "+r.id);option.value=r.id;input.append(option);});}
      else if(p.enum){input=el("select");p.enum.forEach(value=>{const o=el("option","",textLabel(value));o.value=value;input.append(o);});}
      else if(longFields.has(key)||isArray) {input=el("textarea");input.rows=3;}
      else {input=el("input");input.type=p.type==="integer"||p.type==="number"?"number":p.format==="date"?"date":p.format==="uri"?"url":"text";if(p.minimum!==undefined)input.min=p.minimum;if(p.maximum!==undefined)input.max=p.maximum;if(p.type==="integer")input.step="1";}
      input.id="field-"+key;input.name=key;input.dataset.valueType=p.type||"string";input.dataset.nullable=String(Boolean(property.anyOf?.some(s=>s.type==="null")));input.required=required.has(key);
      if(p.maxLength)input.maxLength=p.maxLength;if(p.minLength)input.minLength=p.minLength;if(p.pattern&&input.tagName==="INPUT")input.pattern=p.pattern;
      const value=record?record[key]:(property.default!==undefined?property.default:p.default);
      if(isArray&&ref){const selected=new Set(value||[]);Array.from(input.options).forEach(o=>o.selected=selected.has(o.value));}
      else if(isArray)input.value=(value||[]).join("\n");
      else if(value!==null&&value!==undefined)input.value=String(value);
      else if(input.tagName!=="SELECT")input.value="";
      if(readOnly){if(input.tagName==="SELECT")input.disabled=true;else input.readOnly=true;}
      add(field,label,input);if(hints[key]){const hint=el("small","",hints[key]);hint.id="hint-"+key;input.setAttribute("aria-describedby",hint.id);field.append(hint);}if(key==="framework_refs"&&!readOnly)field.append(referencePicker(input));$("record-fields").append(field);
    }
    if(record){
      const extra=el("div","field full-width");add(extra,el("small","","Record "+record.id+" · created by "+record.created_by+" · "+dateText(record.created_at,true)));
      if(kind==="evidence"&&record.reviewed_by)extra.append(el("small","","Reviewed by "+record.reviewed_by));
      if(kind==="risks"&&record.residual_reviewed_by)extra.append(el("small","","Residual risk reviewed by "+record.residual_reviewed_by));
      if(kind==="risks"&&record.acceptance_approver)extra.append(el("small","","Acceptance approved by "+record.acceptance_approver));
      if(kind==="vendors")extra.append(el("small","","Derived inherent tier: "+textLabel(vendorTier(record))));
      $("record-fields").append(extra);
    }
    $("record-version").textContent=record?"Version "+record.version+" · optimistic locking":"Required fields are marked *";$("save-record").hidden=readOnly;$("cancel-record-dialog").textContent=readOnly?"Close":"Cancel";
    $("record-dialog").showModal();
  }
  async function saveRecord(event) {
    event.preventDefault();if(!writeAllowed())return;
    const {kind,record}=state.editing,schema=state.schemas[kind],data={};
    for(const [key,property] of Object.entries(schema.properties||{})) {
      if(hiddenFields.has(key))continue;const input=$("field-"+key);if(!input)continue;const p=resolveSchema(property);
      if(p.type==="array")data[key]=input.tagName==="SELECT"?Array.from(input.selectedOptions).map(o=>o.value):input.value.split(/\r?\n/).map(v=>v.trim()).filter(Boolean);
      else if(p.type==="integer"||p.type==="number")data[key]=input.value===""?null:Number(input.value);
      else data[key]=input.value===""&&input.dataset.nullable==="true"?null:input.value;
    }
    $("save-record").disabled=true;$("record-error").hidden=true;
    try {
      await api("/api/"+kind+(record?"/"+encodeURIComponent(record.id):""),{method:record?"PUT":"POST",body:JSON.stringify(record?{version:record.version,data}:data)});
      $("record-dialog").close();await loadData();await renderView();toast(textLabel(meta[kind].singular)+(record?" updated.":" created."));
    }catch(error){$("record-error").textContent=error.message+(error.status===409?" Close this dialog and reopen the record to load the latest version.":"");$("record-error").hidden=false;$("record-error").scrollIntoView({block:"nearest"});if(error.status===409){try{await loadData();await renderView();}catch{}}}
    finally{$("save-record").disabled=false;}
  }
  async function exportReport(){
    $("export-button").disabled=true;
    try {const report=await api("/api/report");const blob=new Blob([JSON.stringify(report,null,2)],{type:"application/json"});const url=URL.createObjectURL(blob),a=el("a");a.href=url;a.download="harbor-grc-report-"+today()+".json";a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);toast("Report exported. Treat the file according to your data classification.");}
    catch(error){toast(error.message,true);}finally{$("export-button").disabled=false;}
  }
  $("login-form").addEventListener("submit",async event=>{
    event.preventDefault();const b=event.currentTarget.querySelector("button");b.disabled=true;$("login-error").hidden=true;
    try{const session=await api("/api/auth/login",{method:"POST",body:JSON.stringify({username:$("username").value,password:$("password").value})});$("password").value="";await enterWorkspace(session);}
    catch(error){if(state.user){$("content").replaceChildren(add(el("div","empty-state"),el("h2","","Workspace could not be loaded"),el("p","",error.message),button("Try again","button-secondary",()=>location.reload())));}else{$("login-error").textContent=error.message;$("login-error").hidden=false;}}finally{b.disabled=false;}
  });
  $("logout-button").addEventListener("click",async()=>{try{await api("/api/auth/logout",{method:"POST",body:"{}"});showLogin();}catch(error){toast(error.message,true);}});
  $("export-button").addEventListener("click",exportReport);
  $("record-form").addEventListener("submit",saveRecord);
  ["close-record-dialog","cancel-record-dialog"].forEach(id=>$(id).addEventListener("click",()=>$("record-dialog").close()));
  ["close-import-dialog","cancel-import-dialog"].forEach(id=>$(id).addEventListener("click",()=>$("import-dialog").close()));
  $("import-form").addEventListener("submit",async event=>{
    event.preventDefault();$("import-error").hidden=true;let body;
    try{body=JSON.parse($("cloud-json").value);}catch{$("import-error").textContent="Enter valid JSON before importing.";$("import-error").hidden=false;return;}
    $("submit-import").disabled=true;
    try{const result=await api("/api/import/cloud",{method:"POST",body:JSON.stringify(body)});$("import-dialog").close();$("cloud-json").value="";await loadData();location.hash="findings";await renderView();toast((result.created??0)+" created · "+(result.updated??0)+" updated · "+(result.skipped??0)+" skipped.");}
    catch(error){$("import-error").textContent=error.message;$("import-error").hidden=false;}finally{$("submit-import").disabled=false;}
  });
  window.addEventListener("hashchange",()=>{if(state.user)renderView();});
  window.addEventListener("pageshow",event=>{if(event.persisted)location.reload();});
  api("/api/auth/me").then(enterWorkspace).catch(error=>{if(state.user){$("content").replaceChildren(add(el("div","empty-state"),el("h2","","Workspace could not be loaded"),el("p","",error.message),button("Try again","button-secondary",()=>location.reload())));}else showLogin();});
})();



