import { useState } from "react";
import UploadStep    from "./components/UploadStep";
import AnalyzeStep   from "./components/AnalyzeStep";
import Dashboard     from "./components/Dashboard";
import History       from "./components/History";
import "./styles/globals.css";

export default function App() {
  const [step,    setStep]    = useState("upload");   // upload | analyze | dashboard | history
  const [session, setSession] = useState(null);
  const [resume,  setResume]  = useState(null);

  return (
    <div className="app">
      <header className="header">
        <div className="header-inner">
          <span className="logo">⚡ Resume Tailor</span>
          <nav className="nav">
            <button className={step === "upload"  ? "active" : ""} onClick={() => setStep("upload")}>New</button>
            <button className={step === "history" ? "active" : ""} onClick={() => setStep("history")}>History</button>
          </nav>
        </div>
      </header>

      <main className="main">
        {step === "upload" && (
          <UploadStep onComplete={(resumeData) => {
            setResume(resumeData);
            setStep("analyze");
          }} />
        )}
        {step === "analyze" && (
          <AnalyzeStep resume={resume} onComplete={(sessionData) => {
            setSession(sessionData);
            setStep("dashboard");
          }} />
        )}
        {step === "dashboard" && (
          <Dashboard session={session} resume={resume} />
        )}
        {step === "history" && (
          <History onSelect={(s) => { setSession(s); setStep("dashboard"); }} />
        )}
      </main>
    </div>
  );
}
