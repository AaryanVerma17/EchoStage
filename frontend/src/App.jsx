import { useEffect, useMemo, useState } from 'react';
import { Activity, AudioLines, CircleHelp, Clapperboard, Cloud, LoaderCircle, Play, Pause, RotateCcw, ShieldCheck, Sparkles, WandSparkles, Zap } from 'lucide-react';
import { api } from './api';

const INITIAL = {scene_id:'suspense',scene_phase:'rising_tension',narrative_progress:.42,stage_intensity:.58,simulated_engagement:.64,pacing_pressure:.48,current_lighting:'deep_blue',last_action:'HOLD',seconds_since_last_transition:30,transition_allowed:true};
const ACTIONS = ['HOLD','INTENSIFY','CONTRAST','SOFTEN','TRANSITION'];
const COPY = {HOLD:'Preserve the current atmosphere',INTENSIFY:'Build dramatic intensity',CONTRAST:'Shift the visual mood',SOFTEN:'Create breathing room',TRANSITION:'Advance the narrative phase'};
function Meter({label,value}) { return <div className="meter"><div className="meter-label"><span>{label}</span><strong>{Math.round(value*100)}%</strong></div><div className="track"><span style={{width:`${value*100}%`}}/></div></div>; }

export default function App() {
  const [state,setState] = useState(INITIAL), [playing,setPlaying] = useState(false), [busy,setBusy] = useState(false);
  const [decision,setDecision] = useState(null), [events,setEvents] = useState([]), [health,setHealth] = useState({api:false,decider:false});
  const [notice,setNotice] = useState(''), [theme,setTheme] = useState('A futuristic mystery that slowly becomes hopeful.');
  const [brief,setBrief] = useState(''), [briefBusy,setBriefBusy] = useState(false);
  const stageClass = useMemo(()=>`stage-${(state.current_lighting||'deep_blue').replaceAll('_','-')}`,[state.current_lighting]);

  async function refresh() {
    try { const [h,e] = await Promise.all([api.health(),api.events()]); setHealth({api:true,decider:Boolean(h.decider?.available),deciderMock:h.decider?.mode==='mock'}); setEvents(e.events||[]); }
    catch { setHealth({api:false,decider:false,deciderMock:false}); }
  }
  useEffect(()=>{refresh();},[]);
  async function decide() {
    if(busy)return; setBusy(true); setNotice('');
    try {
      const r=await api.decide(state); setDecision(r); setState(r.state_after);
      setNotice(r.source==='fallback'?`Fallback applied: ${r.fallback_reason||'policy safeguard'}`:'Live Decider 2B choice executed.');
      const e=await api.events(); setEvents(e.events||[]);
    } catch(err) { setNotice(err.message); }
    finally { setBusy(false); refresh(); }
  }
  async function reset(){setState(INITIAL);setDecision(null);setPlaying(false);setNotice('Scene reset.');try{await api.reset();}catch{}}
  async function generateBrief(){setBriefBusy(true);setNotice('');try{const r=await api.brief(theme,'cinematic theatre');setBrief(r.brief);}catch(e){setNotice(`Bedrock: ${e.message}`);}finally{setBriefBusy(false);}}
  useEffect(()=>{if(!playing||busy)return;const t=window.setTimeout(()=>decide(),5000);return()=>window.clearTimeout(t);},[playing,busy,state]);

  return <main className="shell">
    <header className="topbar"><div className="brand"><span className="brand-icon"><AudioLines/></span><div><b>echo<span>stage</span></b><small>ADAPTIVE PERFORMANCE SYSTEM</small></div></div><div className="statuses"><span className={health.api?'online':''}>● API {health.api?'CONNECTED':'OFFLINE'}</span><span className={health.decider?'online':''}>● {health.deciderMock?'MOCK POLICY':`DECIDER ${health.decider?'READY':'UNAVAILABLE'}`}</span></div></header>
    <section className="hero"><div className="eyebrow">— INTELLIGENT STAGE DIRECTION <span>BETA / 01</span></div><h1>A stage that <em>feels</em><br/>the moment.</h1><p>One performance. A thousand possible cues. EchoStage adapts the visual atmosphere through bounded decisions, not scripted guesses.</p></section>
    <section className="workspace">
      <div className="left">
        <div className={`stage ${stageClass}`} style={{'--intensity':state.stage_intensity}}>
          <div className="stage-top"><span>● VIRTUAL STAGE / 001</span><span>SIMULATED SIGNALS</span></div><div className="glow g1"/><div className="glow g2"/><div className="gridfx"/><div className="beam b1"/><div className="beam b2"/><div className="horizon"/><div className="floor"/>
          <div className="figure"><div className="head"/><div className="body"/><div className="leg l1"/><div className="leg l2"/></div>
          <div className="caption"><small>CURRENT SCENE</small><strong>{state.scene_phase.replaceAll('_',' ')}</strong><span>{state.current_lighting.replaceAll('_',' ')} · {Math.round(state.stage_intensity*100)}% intensity</span></div><div className="stage-progress"><span style={{width:`${state.narrative_progress*100}%`}}/></div>
        </div>
        <div className="panel controls"><div><small>DIRECTOR CONTROLS</small><b>{playing?'Autopilot is active':'Ready for direction'}</b><p>{playing?'Requesting decisions every few seconds.':'Request a decision or run the adaptive sequence.'}</p></div><div className="buttons"><button className="primary" onClick={()=>setPlaying(!playing)}>{playing?<Pause size={15}/>:<Play size={15}/>} {playing?'Pause':'Autopilot'}</button><button onClick={decide} disabled={busy}>{busy?<LoaderCircle className="spin" size={15}/>:<Zap size={15}/>} Decide</button><button className="icon-btn" onClick={reset} title="Reset"><RotateCcw size={15}/></button></div></div>
        <div className="metrics"><div className="panel metric-panel"><div className="panel-title"><Activity size={16}/> SCENE TELEMETRY</div><Meter label="Simulated engagement" value={state.simulated_engagement}/><Meter label="Stage intensity" value={state.stage_intensity}/><Meter label="Pacing pressure" value={state.pacing_pressure}/></div><div className="panel metric-panel"><div className="panel-title"><Clapperboard size={16}/> NARRATIVE POSITION</div><div className="big-number">{Math.round(state.narrative_progress*100)}<small>%</small></div><div className="track"><span style={{width:`${state.narrative_progress*100}%`}}/></div><div className="phases">{['opening','rising tension','climax','resolution'].map(x=><span key={x}>{x}</span>)}</div></div></div>
      </div>
      <aside className="right">
        <div className="panel inspector"><div className="panel-title"><ShieldCheck size={16}/> DECISION INSPECTOR <span className="live">LIVE</span></div>
          {decision?<div className="result"><div className="result-top"><small>EXECUTED CUE</small><span className={decision.source==='fallback'?'fallback':''}>{decision.source==='fallback'?'FALLBACK':'DECIDER 2B'}</span></div><h2>{decision.executed_action}</h2><p>{COPY[decision.executed_action]}</p><div className="confidence"><span>Model confidence</span><b>{decision.confidence==null?'Not returned':`${Math.round(decision.confidence*100)}%`}</b></div>{decision.confidence!=null&&<div className="track"><span style={{width:`${decision.confidence*100}%`}}/></div>}<div className="details"><span>Latency</span><b>{decision.latency_ms} ms</b><span>Requested</span><b>{decision.requested_action}</b></div>{decision.fallback_reason&&<div className="warning"><ShieldCheck size={14}/>{decision.fallback_reason.replaceAll('_',' ')}</div>}</div>:<div className="empty"><div className="empty-icon"><CircleHelp/></div><b>Awaiting first decision</b><p>Decider 2B will choose the next cue from the current scene state.</p><button className="primary" onClick={decide} disabled={busy}>{busy?<LoaderCircle className="spin" size={15}/>:<Zap size={15}/>} Make first decision</button></div>}
          {notice&&<div className="notice">{notice}</div>}<div className="legend"><small>AVAILABLE ACTIONS</small>{ACTIONS.map(a=><div key={a}><i className={`dot ${a.toLowerCase()}`}/><b>{a}</b><span>{COPY[a]}</span></div>)}</div>
        </div>
        <div className="panel brief-panel"><div className="panel-title"><Sparkles size={16}/> BEDROCK SCENE BRIEF</div><label htmlFor="theme">Creative direction</label><textarea id="theme" value={theme} onChange={e=>setTheme(e.target.value)} rows="2"/><button className="outline" onClick={generateBrief} disabled={briefBusy}>{briefBusy?<LoaderCircle className="spin" size={15}/>:<WandSparkles size={15}/>} Generate with Bedrock</button>{brief&&<div className="brief-output">{brief}</div>}<small className="bedrock-caption"><Cloud size={13}/> GENERATIVE TASK · SERVER-SIDE</small></div>
      </aside>
    </section>
    <section className="panel history"><div className="history-title"><div><small>TRACEABILITY</small><h2>Decision history</h2></div><span>{events.length} EVENTS</span></div>{events.length?<div className="table-wrap"><table><thead><tr><th>EVENT</th><th>REQUESTED</th><th>EXECUTED</th><th>CONFIDENCE</th><th>LATENCY</th><th>STATUS</th></tr></thead><tbody>{events.slice(0,8).map(e=><tr key={e.event_id}><td><code>{e.event_id?.slice(0,8)}</code></td><td>{e.requested_action}</td><td><b>{e.executed_action}</b></td><td>{e.confidence==null?'—':`${Math.round(e.confidence*100)}%`}</td><td>{e.latency_ms} ms</td><td className={e.source==='fallback'?'warn':''}>{e.source==='fallback'?'Fallback':'Executed'}</td></tr>)}</tbody></table></div>:<div className="no-events"><Activity size={17}/> No decisions logged yet. Make the first decision to create a trace.</div>}</section>
    <footer><b><AudioLines size={15}/> ECHOSTAGE</b><span>STRANDS DECIDER 2B + AMAZON BEDROCK</span><span>SIMULATED SIGNALS · PROTOTYPE</span></footer>
  </main>;
}
