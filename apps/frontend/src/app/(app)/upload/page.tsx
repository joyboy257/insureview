"use client";

import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { FileText, X, CheckCircle, AlertCircle, Loader2, Upload } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Card, CardContent } from "@/components/ui/Card";
import { Progress } from "@/components/ui/Progress";
import { ConsentBanner } from "@/components/pdpa/ConsentBanner";
import { DisclaimerBanner } from "@/components/ui/DisclaimerBanner";
import { getUploadPresignedUrl, completeUpload, type ParsingSession } from "@/lib/api";
import { useParsingSession } from "@/hooks/useUpload";

interface FileState {
  id: string;
  file: File;
  sessionId: string | null;
  status: "pending" | "uploading" | "parsing" | "done" | "error";
  progress: number;
  error?: string;
}

function FileItem({ file, onRemove }: { file: FileState; onRemove: () => void }) {
  const session = useParsingSession(file.sessionId);

  const progress =
    file.status === "uploading"
      ? file.progress
      : file.status === "parsing"
      ? session.data?.status === "completed"
        ? 100
        : session.data?.status === "failed"
        ? 0
        : 60
      : file.status === "done"
      ? 100
      : 0;

  return (
    <Card>
      <CardContent className="flex items-center gap-4 py-3">
        <FileText className="h-5 w-5 flex-shrink-0 text-muted-foreground" />
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium truncate">{file.file.name}</p>
          <div className="flex items-center gap-2 mt-1">
            <Progress value={progress} className="h-1.5 flex-1" />
            <span className="text-xs text-muted-foreground w-10 text-right">
              {progress}%
            </span>
          </div>
          {file.error && (
            <p className="text-xs text-destructive mt-1">{file.error}</p>
          )}
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          {file.status === "uploading" && (
            <Loader2 className="h-4 w-4 animate-spin text-primary" />
          )}
          {file.status === "parsing" && (
            <Loader2 className="h-4 w-4 animate-spin text-primary" />
          )}
          {file.status === "done" && (
            <CheckCircle className="h-4 w-4 text-green-600" />
          )}
          {file.status === "error" && (
            <AlertCircle className="h-4 w-4 text-destructive" />
          )}
          <span className="text-xs text-muted-foreground capitalize">
            {file.status === "parsing"
              ? session.data?.status === "completed"
                ? "done"
                : "reading..."
              : file.status === "error"
              ? "failed"
              : file.status}
          </span>
          <button
            onClick={onRemove}
            className="text-muted-foreground hover:text-destructive ml-1"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      </CardContent>
    </Card>
  );
}

export default function UploadPage() {
  const [files, setFiles] = useState<FileState[]>([]);
  const [showConsent, setShowConsent] = useState(true);
  const [consentGiven, setConsentGiven] = useState(false);

  async function processFile(fs: FileState) {
    updateFile(fs.id, { status: "uploading", progress: 5 });

    try {
      // Step 1: Get presigned URL
      const { uploadUrl, s3Key } = await getUploadPresignedUrl({
        filename: fs.file.name,
        fileSizeBytes: fs.file.size,
      });
      updateFile(fs.id, { progress: 20 });

      // Step 2: Upload PDF directly to S3
      await fetch(uploadUrl, {
        method: "PUT",
        body: fs.file,
        headers: { "Content-Type": "application/pdf" },
      });
      updateFile(fs.id, { progress: 50 });

      // Step 3: Notify backend to trigger parsing
      // Extract session ID from s3Key: "uploads/{user_id}/{session_id}/filename.pdf"
      const parts = s3Key.split("/");
      const sessionId = parts[2];
      if (!sessionId) throw new Error("Invalid s3Key: could not extract session ID");
      await completeUpload(sessionId);
      updateFile(fs.id, { sessionId, status: "parsing", progress: 60 });
    } catch (err) {
      updateFile(fs.id, {
        status: "error",
        error: err instanceof Error ? err.message : "Upload failed",
      });
    }
  }

  const updateFile = useCallback(
    (id: string, update: Partial<FileState>) => {
      setFiles((prev) => prev.map((f) => (f.id === id ? { ...f, ...update } : f)));
    },
    []
  );

  const onDrop = useCallback(
    (accepted: File[]) => {
      const newFiles: FileState[] = accepted.map(
        (file) =>
          ({
            id: `${Date.now()}-${file.name}`,
            file,
            sessionId: null,
            status: "pending",
            progress: 0,
          }) as FileState
      );
      setFiles((prev) => [...prev, ...newFiles]);
      newFiles.forEach((nf) => processFile(nf));
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    []
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"] },
    maxSize: 50 * 1024 * 1024,
    maxFiles: 10,
    disabled: !consentGiven,
  });

  const removeFile = (id: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== id));
  };

  const completedCount = files.filter((f) => f.status === "done").length;

  if (showConsent && !consentGiven) {
    return (
      <ConsentBanner
        onAccept={() => {
          setConsentGiven(true);
          setShowConsent(false);
        }}
        onViewPolicy={() => (window.location.href = "/privacy")}
      />
    );
  }

  return (
    <div className="container py-10 max-w-3xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Upload Your Policies</h1>
        <p className="text-muted-foreground">
          Upload up to 10 Singapore insurance policy PDFs. We support AIA, Great
          Eastern, Prudential, NTUC Income, and other major insurers.
        </p>
      </div>

      <div
        {...getRootProps()}
        className={`border-2 rounded-xl p-10 text-center cursor-pointer transition-all ${
          isDragActive
            ? "border-primary bg-primary/5 scale-[1.01]"
            : "border-primary/30 hover:border-primary/60 bg-white"
        } ${!consentGiven ? "opacity-50 pointer-events-none" : ""}`}
      >
        <input {...getInputProps()} />
        <div className="flex flex-col items-center gap-3">
          <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
            <Upload className="h-6 w-6 text-primary" />
          </div>
          <div>
            <p className="text-base font-medium">
              {isDragActive ? "Drop your PDFs here" : "Drag & drop your policy PDFs"}
            </p>
            <p className="text-sm text-muted-foreground mt-1">
              or{" "}
              <span className="text-primary font-medium underline underline-offset-2 cursor-pointer">
                click to browse
              </span>{" "}
              &mdash; PDF only, up to 50 MB each, max 10 files
            </p>
          </div>
        </div>
      </div>

      {files.length > 0 && (
        <div className="mt-6 space-y-3">
          {files.map((f) => (
            <FileItem
              key={f.id}
              file={f}
              onRemove={() => removeFile(f.id)}
            />
          ))}
        </div>
      )}

      {completedCount > 0 && completedCount < files.length && (
        <div className="mt-6 flex justify-center">
          <Button variant="outline" disabled>
            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            Processing {files.length - completedCount} more...
          </Button>
        </div>
      )}

      {completedCount === files.length && files.length > 0 && (
        <div className="mt-6 flex justify-center">
          <Button
            onClick={() => (window.location.href = "/dashboard")}
            size="lg"
          >
            View My Portfolio ({completedCount} policies)
          </Button>
        </div>
      )}

      <DisclaimerBanner />

      <div className="mt-6 p-4 bg-slate-50 rounded-lg text-sm text-muted-foreground">
        <p>
          <strong>Privacy:</strong> Your PDFs are deleted immediately after parsing.
          Only structured policy data is retained. We do not share your information
          with insurers or third parties.
        </p>
      </div>
    </div>
  );
}
