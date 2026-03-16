import React from 'react';
import { Github, Linkedin, User } from 'lucide-react';

export default function AuthorSeal() {
  return (
    <div className="fixed bottom-4 right-4 z-[100] group">
      <div className="flex items-center gap-3">
        {/* Expanded Content on Hover */}
        <div className="flex items-center gap-2 bg-abyssal/90 backdrop-blur-md border border-panel-light/30 px-3 py-1.5 rounded-full shadow-2xl opacity-0 group-hover:opacity-100 transition-all duration-300 translate-x-10 group-hover:translate-x-0 pointer-events-none group-hover:pointer-events-auto">
          <span className="text-[10px] font-mono font-bold text-white whitespace-nowrap hidden sm:block">
            LUIS FABIO YOPLAC CORTEZ
          </span>
          <div className="h-3 w-[1px] bg-panel-light/50 hidden sm:block"></div>
          <a 
            href="https://github.com/EconomiaUNMSM" 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-muted-text hover:text-accent transition-colors"
            title="GitHub Profile"
          >
            <Github size={12} />
          </a>
          <a 
            href="https://www.linkedin.com/in/luis-yoplac-cortez-10397328b" 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-muted-text hover:text-accent transition-colors"
            title="LinkedIn Profile"
          >
            <Linkedin size={12} />
          </a>
        </div>

        {/* The Trigger Icon / Seal */}
        <div className="relative">
          <div className="absolute inset-0 bg-accent/20 rounded-full blur-md animate-pulse"></div>
          <div className="relative w-8 h-8 rounded-full bg-panel border border-accent/40 flex items-center justify-center text-accent hover:border-white hover:text-white transition-all duration-300 cursor-pointer shadow-[0_0_15px_rgba(0,194,255,0.2)]">
            <User size={14} className="group-hover:scale-110 transition-transform" />
            <div className="absolute -top-1 -right-1 w-2 h-2 bg-success rounded-full border border-abyssal"></div>
          </div>
        </div>
      </div>
    </div>
  );
}
