interface CardProps {
  children: React.ReactNode;
  className?: string;
}

export default function Card({ children, className = '' }: CardProps) {
  return (
    <div className={`bg-white rounded-2xl shadow-lg border border-slate-100 p-6 md:p-8 ${className}`}>
      {children}
    </div>
  );
}