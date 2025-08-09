interface ProgressProps {
  value: number;
  max?: number;
  className?: string;
}

export default function Progress({ value, max = 100, className = '' }: ProgressProps) {
  const percentage = Math.min((value / max) * 100, 100);

  return (
    <div className={`w-full bg-slate-200 rounded-full h-2 ${className}`}>
      <div 
        className="bg-gradient-to-r from-blue-500 to-fuchsia-500 h-2 rounded-full transition-all duration-300"
        style={{ width: `${percentage}%` }}
      />
    </div>
  );
}