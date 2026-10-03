import React from 'react';

interface FeatureCardProps {
  to: string;
  icon: React.ReactNode;
  title: string;
  subtitle?: string;
  description: string;
  badge?: string;
}

const FeatureCard: React.FC<FeatureCardProps> = ({ to, icon, title, subtitle, description, badge }) => {
  return (
    <a
      href={to}
      className="group bg-white rounded-2xl p-6 sm:p-8 border border-slate-200 shadow-sm hover:shadow-lg hover:border-primary-200 transition-all duration-300"
    >
      <div className="w-14 h-14 rounded-xl bg-primary-50 group-hover:bg-primary-100 flex items-center justify-center mb-4 transition-colors">
        {icon}
      </div>
      {badge && (
        <span className="inline-block px-2 py-1 text-xs font-medium text-primary-600 bg-primary-50 rounded-full mb-3">
          {badge}
        </span>
      )}
      <h3 className="text-xl font-bold text-slate-900 mb-2 group-hover:text-primary-600 transition-colors">{title}</h3>
      {subtitle && <p className="text-sm text-slate-500 mb-2">{subtitle}</p>}
      <p className="text-slate-600 leading-relaxed">{description}</p>
    </a>
  );
};

export default FeatureCard;