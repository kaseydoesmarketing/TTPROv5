interface KpiCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: React.ReactNode;
}

export default function KpiCard({ title, value, subtitle, icon }: KpiCardProps) {
  return (
    <div className="bg-white rounded-2xl shadow-lg border border-slate-100 p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-slate-500 mb-1">{title}</p>
          <p className="text-2xl font-bold text-slate-900">{value}</p>
          {subtitle && <p className="text-sm text-slate-400 mt-1">{subtitle}</p>}
        </div>
        {icon && (
          <div className="p-3 bg-gradient-to-r from-blue-50 to-fuchsia-50 rounded-xl">
            {icon}
          </div>
        )}
      </div>
    </div>
  );
}