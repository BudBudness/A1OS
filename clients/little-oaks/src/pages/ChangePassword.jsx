import React,{useState} from "react";
import {api} from "../api/client.js";

export default function ChangePassword(){
  const [currentPassword,setCurrentPassword]=useState("");
  const [newPassword,setNewPassword]=useState("");
  const [confirmation,setConfirmation]=useState("");
  const [message,setMessage]=useState("");
  const [error,setError]=useState("");
  const [busy,setBusy]=useState(false);

  async function submit(event){
    event.preventDefault();
    setError("");
    setMessage("");
    if(newPassword.length<8){
      setError("The new password must be at least 8 characters.");
      return;
    }
    if(newPassword!==confirmation){
      setError("The new passwords do not match.");
      return;
    }
    setBusy(true);
    try{
      await api.post("/auth/change-password",{
        current_password:currentPassword,
        new_password:newPassword,
      });
      setCurrentPassword("");
      setNewPassword("");
      setConfirmation("");
      setMessage("Password changed. Sign in again with your new password.");
    }catch(err){
      setError(err.message||"Password change failed.");
    }finally{
      setBusy(false);
    }
  }

  return <section>
    <h2>Change password</h2>
    <p>Change your own password. Passwords are never displayed or returned.</p>
    <form className="panel auth-card" onSubmit={submit}>
      <label>Current password
        <input type="password" value={currentPassword} onChange={e=>setCurrentPassword(e.target.value)} required autoComplete="current-password"/>
      </label>
      <label>New password
        <input type="password" value={newPassword} onChange={e=>setNewPassword(e.target.value)} minLength={8} required autoComplete="new-password"/>
      </label>
      <label>Confirm new password
        <input type="password" value={confirmation} onChange={e=>setConfirmation(e.target.value)} minLength={8} required autoComplete="new-password"/>
      </label>
      {error&&<p role="alert">{error}</p>}
      {message&&<p role="status">{message}</p>}
      <button disabled={busy}>{busy?"Changing…":"Change password"}</button>
    </form>
  </section>;
}
