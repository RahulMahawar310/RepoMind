export default function SourceCard({ s }) {
  return <span className="source">{s.file}:{s.start}-{s.end}</span>;
}
