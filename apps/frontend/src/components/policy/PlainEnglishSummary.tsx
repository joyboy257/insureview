interface PlainEnglishSummaryProps {
  text: string;
}

export function PlainEnglishSummary({ text }: PlainEnglishSummaryProps) {
  return (
    <div className="text-sm leading-relaxed">
      <p>{text}</p>
    </div>
  );
}
