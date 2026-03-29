"use client";

import { useState, useCallback } from "react";
import { useQuery } from "@tanstack/react-query";
import { getParsingSession, getUploadPresignedUrl, type ParsingSession } from "@/lib/api";

interface UseUploadOptions {
  maxFiles?: number;
  maxSizeBytes?: number;
}

export function useUpload(options: UseUploadOptions = {}) {
  const { maxFiles = 10, maxSizeBytes = 50 * 1024 * 1024 } = options;

  const [files, setFiles] = useState<
    Array<{
      id: string;
      name: string;
      size: number;
      status: "pending" | "uploading" | "parsing" | "done" | "error";
      progress: number;
      error?: string;
    }>
  >([]);

  const addFiles = useCallback(
    (newFiles: File[]) => {
      if (files.length + newFiles.length > maxFiles) {
        throw new Error(`Maximum ${maxFiles} files allowed`);
      }
      const valid = newFiles.filter((f) => f.size <= maxSizeBytes);
      const added: typeof files[number][] = valid.map((file) => ({
        id: `${Date.now()}-${file.name}`,
        name: file.name,
        size: file.size,
        status: "pending",
        progress: 0,
      }));
      setFiles((prev) => [...prev, ...added]);
      return added;
    },
    [files.length, maxFiles, maxSizeBytes]
  );

  const removeFile = useCallback((id: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== id));
  }, []);

  const updateFileStatus = useCallback(
    (id: string, update: Partial<(typeof files)[number]>) => {
      setFiles((prev) => prev.map((f) => (f.id === id ? { ...f, ...update } : f)));
    },
    []
  );

  return { files, addFiles, removeFile, updateFileStatus };
}

export function useParsingSession(sessionId: string | null) {
  return useQuery<ParsingSession>({
    queryKey: ["parsing-session", sessionId],
    queryFn: () => getParsingSession(sessionId!),
    enabled: !!sessionId,
    refetchInterval: (query) =>
      query.state.data?.status === "processing" ||
      query.state.data?.status === "pending"
        ? 3000
        : false,
  });
}
