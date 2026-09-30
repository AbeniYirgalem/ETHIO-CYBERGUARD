import React, { useState } from 'react';
import { CheckSquare, ShieldCheck, AlertTriangle, Check, X, Lock, CheckCircle } from 'lucide-react';
import type { ResponseAction } from '../types';

interface ResponseViewProps {
  actions: ResponseAction[];
  onApproveAction: (id: string) => void;
  onRejectAction: (id: string, reason?: string) => void;
}

export const ResponseView: React.FC<ResponseViewProps> = ({
  actions,
  onApproveAction,
  onRejectAction
}) => {
  const [selectedActionForModal, setSelectedActionForModal] = useState<ResponseAction | null>(null);
  const [modalMode, setModalMode] = useState<'approve' | 'reject'>('approve');
  const [rejectReason, setRejectReason] = useState('');

  const pending = actions.filter(a => a.status === 'PENDING_APPROVAL');
  const history = actions.filter(a => a.status !== 'PENDING_APPROVAL');

  const handleOpenDecision = (act: ResponseAction, mode: 'approve' | 'reject') => {
    setSelectedActionForModal(act);
    setModalMode(mode);
    setRejectReason('');
  };

  const handleConfirmDecision = () => {
    if (!selectedActionForModal) return;
    if (modalMode === 'approve') {
      onApproveAction(selectedActionForModal.id);
    } else {
      onRejectAction(selectedActionForModal.id, rejectReason || 'Rejected by Tier-2 Security Analyst');
    }
    setSelectedActionForModal(null);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center pb-2 border-b border-[#1E2A38]">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center space-x-2">
            <CheckSquare className="w-5 h-5 text-[#00D9FF]" />
            <span>Response Center & Human Approval Gateway</span>
          </h1>
          <p className="text-xs text-[#7D8A99]">Safety-guaranteed human authorization queue for containment and remediation commands</p>
        </div>

        <div className="flex items-center space-x-2 text-xs font-mono bg-[#0D131C] px-3 py-1.5 rounded-lg border border-[#1E2A38] mt-3 sm:mt-0">
          <Lock className="w-3.5 h-3.5 text-[#22C55E]" />
          <span className="text-white">Zero Autonomous Destructive Execution Policy</span>
        </div>
      </div>

      {/* Safety Notice Banner */}
      <div className="p-4 bg-[#111923] border border-[#00D9FF]/30 rounded-xl flex items-start space-x-3">
        <ShieldCheck className="w-5 h-5 text-[#00D9FF] shrink-0 mt-0.5" />
        <div className="text-xs">
          <p className="font-bold text-white">Strict Human-in-the-Loop Safeguard</p>
          <p className="text-[#7D8A99] mt-0.5">
            Per ETHIO-CYBERGUARD security specifications, AI agents generate, justify, and rank response actions. However, <strong>no firewall modification, process kill, or host network isolation is ever executed without an authorized analyst's explicit verification</strong>.
          </p>
        </div>
      </div>

      {/* Pending Actions Queue */}
      <div className="bg-[#111923] border border-[#1E2A38] rounded-xl overflow-hidden">
        <div className="p-4 border-b border-[#1E2A38] flex justify-between items-center">
          <div>
            <h2 className="text-sm font-bold text-white">Pending Containment Actions ({pending.length})</h2>
            <p className="text-xs text-[#7D8A99]">Review evidence rationale and execute authorized containment</p>
          </div>
        </div>

        {pending.length === 0 ? (
          <div className="p-8 text-center text-xs text-[#22C55E]">
            <CheckCircle className="w-8 h-8 mx-auto mb-2 text-[#22C55E]" />
            <p className="font-bold">No actions currently pending approval.</p>
            <p className="text-[#7D8A99]">All active threat recommendations have been reviewed.</p>
          </div>
        ) : (
          <div className="divide-y divide-[#1E2A38]">
            {pending.map((act) => (
              <div key={act.id} className="p-5 flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4 hover:bg-[#0D131C]/40 transition">
                <div className="space-y-1.5 max-w-2xl">
                  <div className="flex items-center space-x-2">
                    <span className="px-2 py-0.5 rounded text-[11px] font-mono font-bold bg-[#FF1744]/15 text-[#FF1744] border border-[#FF1744]/30">
                      {act.action_type}
                    </span>
                    <span className="text-xs font-mono text-[#00D9FF] font-semibold">{act.incident_number}</span>
                    <span className="text-[10px] text-[#7D8A99] font-mono">Recommended by: {act.recommended_by}</span>
                  </div>

                  <p className="text-sm font-bold text-white">{act.target_entity}</p>
                  <p className="text-xs text-[#E6EDF3] leading-relaxed">{act.reasoning}</p>

                  <div className="flex items-center space-x-4 text-[11px] text-[#7D8A99] pt-1">
                    <span>Confidence: <strong className="text-[#22C55E]">{act.confidence}%</strong></span>
                    <span>Queued: <strong className="text-white">{act.created_at}</strong></span>
                  </div>
                </div>

                <div className="flex items-center space-x-3 w-full sm:w-auto">
                  <button
                    onClick={() => handleOpenDecision(act, 'approve')}
                    className="flex-1 sm:flex-none px-4 py-2 rounded-lg bg-[#22C55E] hover:bg-[#22C55E]/80 text-black font-bold text-xs flex items-center justify-center space-x-1.5 transition shadow-lg shadow-[#22C55E]/20"
                  >
                    <Check className="w-4 h-4" />
                    <span>Approve & Execute</span>
                  </button>
                  <button
                    onClick={() => handleOpenDecision(act, 'reject')}
                    className="flex-1 sm:flex-none px-4 py-2 rounded-lg bg-[#111923] border border-[#FF1744]/40 hover:bg-[#FF1744]/20 text-[#FF1744] font-bold text-xs flex items-center justify-center space-x-1.5 transition"
                  >
                    <X className="w-4 h-4" />
                    <span>Reject</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Historical Response Log */}
      <div className="bg-[#111923] border border-[#1E2A38] rounded-xl overflow-hidden">
        <div className="p-4 border-b border-[#1E2A38]">
          <h2 className="text-sm font-bold text-white">Remediation Execution History</h2>
          <p className="text-xs text-[#7D8A99]">Verified actions executed by perimeter orchestrator or host agents</p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-[#0D131C] text-[#7D8A99] uppercase text-[10px] border-b border-[#1E2A38]">
              <tr>
                <th className="py-2.5 px-4">Action ID</th>
                <th className="py-2.5 px-4">Incident</th>
                <th className="py-2.5 px-4">Action Type</th>
                <th className="py-2.5 px-4">Target Entity</th>
                <th className="py-2.5 px-4">Decision</th>
                <th className="py-2.5 px-4">Reviewer</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1E2A38] text-[11px]">
              {history.map(act => (
                <tr key={act.id} className="hover:bg-[#0D131C]/60 transition">
                  <td className="py-3 px-4 font-bold text-white">{act.id}</td>
                  <td className="py-3 px-4 text-[#00D9FF]">{act.incident_number}</td>
                  <td className="py-3 px-4 text-white">{act.action_type}</td>
                  <td className="py-3 px-4 text-[#7D8A99]">{act.target_entity}</td>
                  <td className="py-3 px-4">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      act.status === 'APPROVED' ? 'bg-[#22C55E]/15 text-[#22C55E] border border-[#22C55E]/30' : 'bg-[#FF1744]/15 text-[#FF1744]'
                    }`}>
                      {act.status}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-[#7D8A99] font-sans">Dawit Mengistu</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Decision Modal */}
      {selectedActionForModal && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50">
          <div className="bg-[#111923] border border-[#1E2A38] rounded-xl max-w-lg w-full p-6 space-y-4 shadow-2xl">
            <div className="flex justify-between items-center border-b border-[#1E2A38] pb-3">
              <h3 className="text-base font-bold text-white flex items-center space-x-2">
                {modalMode === 'approve' ? (
                  <>
                    <CheckCircle className="w-5 h-5 text-[#22C55E]" />
                    <span>Authorize Response Action</span>
                  </>
                ) : (
                  <>
                    <AlertTriangle className="w-5 h-5 text-[#FF1744]" />
                    <span>Reject Response Action</span>
                  </>
                )}
              </h3>
              <button 
                onClick={() => setSelectedActionForModal(null)}
                className="text-[#7D8A99] hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-2 text-xs">
              <p className="text-[#7D8A99]">Action: <strong className="text-white font-mono">{selectedActionForModal.action_type}</strong></p>
              <p className="text-[#7D8A99]">Target: <strong className="text-[#00D9FF] font-mono">{selectedActionForModal.target_entity}</strong></p>
              <p className="text-[#7D8A99]">Incident: <strong className="text-white font-mono">{selectedActionForModal.incident_number}</strong></p>
              
              <div className="p-3 bg-[#070B12] rounded-lg border border-[#1E2A38] mt-2">
                <span className="text-[10px] text-[#7D8A99] uppercase font-mono block">AI Justification:</span>
                <p className="text-white mt-1 leading-relaxed">{selectedActionForModal.reasoning}</p>
              </div>

              {modalMode === 'reject' && (
                <div className="mt-3">
                  <label className="text-[11px] text-[#7D8A99] block mb-1">State Reason for Rejection:</label>
                  <textarea 
                    value={rejectReason}
                    onChange={(e) => setRejectReason(e.target.value)}
                    placeholder="e.g. Asset is critical SWIFT gateway; scheduled downtime required..."
                    className="w-full bg-[#070B12] border border-[#1E2A38] rounded-lg p-2 text-xs text-white placeholder-[#7D8A99] focus:outline-none focus:border-[#FF1744]"
                    rows={3}
                  />
                </div>
              )}
            </div>

            <div className="flex items-center space-x-3 pt-3 border-t border-[#1E2A38]">
              <button
                onClick={handleConfirmDecision}
                className={`flex-1 py-2 rounded-lg font-bold text-xs transition ${
                  modalMode === 'approve'
                    ? 'bg-[#22C55E] hover:bg-[#22C55E]/80 text-black'
                    : 'bg-[#FF1744] hover:bg-[#FF1744]/80 text-white'
                }`}
              >
                {modalMode === 'approve' ? 'Confirm & Execute Now' : 'Confirm Rejection'}
              </button>
              <button
                onClick={() => setSelectedActionForModal(null)}
                className="py-2 px-4 rounded-lg bg-[#0D131C] border border-[#1E2A38] text-xs text-[#7D8A99] hover:text-white"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
