"use client";

import { useState } from "react";
import { Shield, FileText, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Modal, ModalContent, ModalHeader, ModalTitle, ModalDescription, ModalFooter } from "@/components/ui/Modal";

interface ConsentBannerProps {
  onAccept: () => void;
  onViewPolicy: () => void;
}

export function ConsentBanner({ onAccept, onViewPolicy }: ConsentBannerProps) {
  const [agreedUpload, setAgreedUpload] = useState(false);
  const [agreedAnalysis, setAgreedAnalysis] = useState(false);
  const [showPrivacyModal, setShowPrivacyModal] = useState(false);

  const canAccept = agreedUpload && agreedAnalysis;

  return (
    <>
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
        <div className="w-full max-w-lg rounded-xl bg-white shadow-xl">
          <div className="p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10">
                <Shield className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">Before you upload your policies</h2>
                <p className="text-sm text-muted-foreground">Your consent is required under Singapore PDPA</p>
              </div>
            </div>

            <div className="mb-4 max-h-60 overflow-y-auto rounded-lg border bg-slate-50 p-4 text-sm text-muted-foreground">
              <p className="mb-3">
                <strong className="text-foreground">What we collect:</strong> We process your
                insurance policy PDF documents to extract structured data (benefits, exclusions,
                riders, coverage amounts).
              </p>
              <p className="mb-3">
                <strong className="text-foreground">PDF handling:</strong> Your original PDFs
                are deleted immediately after parsing unless you opt into the secure vault.
                Only structured data is retained.
              </p>
              <p className="mb-3">
                <strong className="text-foreground">What we do not do:</strong> We do not
                provide financial advice, sell your data, or share your information with
                insurers or third parties.
              </p>
              <p>
                <strong className="text-foreground">Your rights:</strong> You may export or
                delete all your data at any time via Settings.
              </p>
            </div>

            <div className="space-y-3 mb-4">
              <label className="flex items-start gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={agreedUpload}
                  onChange={(e) => setAgreedUpload(e.target.checked)}
                  className="mt-0.5 h-4 w-4 rounded border-gray-400"
                />
                <span className="text-sm">
                  I consent to uploading my insurance policy documents for analysis. My PDFs
                  will be deleted immediately after parsing unless I opt into the secure vault.
                </span>
              </label>
              <label className="flex items-start gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={agreedAnalysis}
                  onChange={(e) => setAgreedAnalysis(e.target.checked)}
                  className="mt-0.5 h-4 w-4 rounded border-gray-400"
                />
                <span className="text-sm">
                  I understand this is an informational service only, not financial advice, and
                  I should consult a licensed adviser before making insurance decisions.
                </span>
              </label>
            </div>

            <div className="flex gap-3">
              <Button variant="outline" size="sm" onClick={onViewPolicy} className="gap-2">
                <FileText className="h-4 w-4" />
                Read Full Privacy Policy
              </Button>
              <Button onClick={onAccept} disabled={!canAccept} className="flex-1">
                I Agree, Continue to Upload
              </Button>
            </div>

            <p className="mt-3 text-xs text-muted-foreground">
              Your consent is recorded with a timestamp and version of this policy. You may
              withdraw consent and request data deletion at any time via Settings.
            </p>
          </div>
        </div>
      </div>

      <Modal open={showPrivacyModal} onOpenChange={setShowPrivacyModal}>
        <ModalContent>
          <ModalHeader>
            <ModalTitle>Privacy Policy</ModalTitle>
            <ModalDescription>Full privacy policy under Singapore PDPA</ModalDescription>
          </ModalHeader>
          <div className="max-h-96 overflow-y-auto text-sm text-muted-foreground space-y-3">
            <p>
              Insert full privacy policy text here. See <code>docs/privacy-policy.md</code>.
            </p>
          </div>
          <ModalFooter>
            <Button variant="outline" onClick={() => setShowPrivacyModal(false)}>
              Close
            </Button>
            <Button onClick={() => { setShowPrivacyModal(false); onAccept(); }} disabled={!canAccept}>
              I Agree
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  );
}
