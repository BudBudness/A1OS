import React,{useState} from "react";
import {login} from "../core/auth.js";

export default function Login({onAuthenticated}){
  const [email,setEmail]=useState("");
  const [password,setPassword]=useState("");
  const [error,setError]=useState("");
  const [busy,setBusy]=useState(false);

  async function submit(e){
    e.preventDefault();
    setError(""); setBusy(true);
    try {
      await login(email,password);
      onAuthenticated();
    } catch(err) {
      setError(err.message || "Authentication failed");
    } finally { setBusy(false); }
  }

  return <section className="auth-page">
    <form className="panel auth-card" onSubmit={submit}>
      <span className="eyebrow">LITTLE OAKS</span>
      <h2>Sign in</h2>
      <p>Secure school portal</p>
      <label>Email<input type="email" value={email} onChange={e=>setEmail(e.target.value)} required autoComplete="username"/></label>
      <label>Password<input type="password" value={password} onChange={e=>setPassword(e.target.value)} required autoComplete="current-password"/></label>
      {error&&<p role="alert">{error}</p>}
      <button disabled={busy}>{busy?"Signing in…":"Sign in"}</button>
    </form>
  </section>;
}
