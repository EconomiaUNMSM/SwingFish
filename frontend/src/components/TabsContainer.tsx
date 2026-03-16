"use client";

import { useState } from "react";

interface Tab {
  id: string;
  label: string;
  icon?: string;
  content: React.ReactNode;
}

interface TabsContainerProps {
  tabs: Tab[];
  defaultTab?: string;
}

export default function TabsContainer({ tabs, defaultTab }: TabsContainerProps) {
  const [activeTab, setActiveTab] = useState(defaultTab || tabs[0]?.id);

  if (tabs.length === 0) return null;

  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* Tab Navigation */}
      <div className="flex overflow-x-auto no-scrollbar border-b border-panel-light/20 bg-abyssal/30 shrink-0">
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-5 py-3 text-[10px] font-mono uppercase tracking-widest transition-all relative shrink-0 ${
                isActive 
                ? "text-accent bg-panel-light/20" 
                : "text-muted-text hover:text-primary-text hover:bg-panel-light/10"
              }`}
            >
              {tab.icon && <span className="text-sm opacity-80">{tab.icon}</span>}
              {tab.label}
              {isActive && (
                <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-accent shadow-[0_0_8px_rgba(0,194,255,0.6)]"></div>
              )}
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-y-auto p-4 custom-scrollbar">
        {tabs.find((tab) => tab.id === activeTab)?.content}
      </div>

      <style jsx>{`
        .no-scrollbar::-webkit-scrollbar {
          display: none;
        }
        .no-scrollbar {
          -ms-overflow-style: none;
          scrollbar-width: none;
        }
        .custom-scrollbar::-webkit-scrollbar {
          width: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(0,0,0,0);
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: #172A3A;
          border-radius: 10px;
        }
      `}</style>
    </div>
  );
}
