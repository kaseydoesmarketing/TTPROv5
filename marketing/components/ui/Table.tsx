interface TableProps {
  children: React.ReactNode;
  className?: string;
}

interface TableHeaderProps {
  children: React.ReactNode;
}

interface TableBodyProps {
  children: React.ReactNode;
}

interface TableRowProps {
  children: React.ReactNode;
  className?: string;
}

interface TableCellProps {
  children: React.ReactNode;
  className?: string;
}

export function Table({ children, className = '' }: TableProps) {
  return (
    <div className={`overflow-x-auto ${className}`}>
      <table className="min-w-full">
        {children}
      </table>
    </div>
  );
}

export function TableHeader({ children }: TableHeaderProps) {
  return (
    <thead className="bg-slate-50">
      {children}
    </thead>
  );
}

export function TableBody({ children }: TableBodyProps) {
  return <tbody className="divide-y divide-slate-200">{children}</tbody>;
}

export function TableRow({ children, className = '' }: TableRowProps) {
  return <tr className={className}>{children}</tr>;
}

export function TableCell({ children, className = '' }: TableCellProps) {
  return (
    <td className={`px-6 py-4 text-sm text-slate-900 ${className}`}>
      {children}
    </td>
  );
}

export function TableHeaderCell({ children, className = '' }: TableCellProps) {
  return (
    <th className={`px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider ${className}`}>
      {children}
    </th>
  );
}