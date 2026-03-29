import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function centsToDollars(cents: number): string {
  return `S$${(cents / 100).toLocaleString("en-SG", { minimumFractionDigits: 2 })}`;
}

export function formatCents(cents: number): string {
  if (cents >= 100000000) {
    return `S$${(cents / 100000000).toFixed(1)}M`;
  }
  if (cents >= 100000) {
    return `S$${(cents / 100000).toFixed(0)}K`;
  }
  return `S$${(cents / 100).toLocaleString("en-SG")}`;
}
