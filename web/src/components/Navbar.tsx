"use client";

import Link from "next/link";
import { Shield, LayoutDashboard, Server, User, LogOut } from "lucide-react";

export default function Navbar() {
  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-slate-800/80 bg-slate-950/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Logo & Brand */}
        <Link href="/" className="flex items-center gap-3 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-purple-600 via-indigo-500 to-cyan-400 p-0.5 shadow-lg shadow-purple-500/20 group-hover:scale-105 transition-transform">
            <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
              <Shield className="w-5 h-5 text-purple-400 group-hover:text-cyan-400 transition-colors" />
            </div>
          </div>
          <div>
            <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
              Hu Immortal
            </span>
            <span className="text-xs block text-purple-400 font-medium">Control Panel</span>
          </div>
        </Link>

        {/* Center Navigation */}
        <nav className="hidden md:flex items-center gap-1 bg-slate-900/60 p-1.5 rounded-xl border border-slate-800/60">
          <Link
            href="/"
            className="px-4 py-1.5 rounded-lg text-sm font-medium text-slate-300 hover:text-white hover:bg-slate-800/60 transition-all flex items-center gap-2"
          >
            Home
          </Link>
          <Link
            href="/dashboard"
            className="px-4 py-1.5 rounded-lg text-sm font-medium text-purple-300 bg-purple-500/10 border border-purple-500/20 hover:bg-purple-500/20 transition-all flex items-center gap-2"
          >
            <LayoutDashboard className="w-4 h-4" />
            Dashboard
          </Link>
          <a
            href="https://discord.com"
            target="_blank"
            rel="noreferrer"
            className="px-4 py-1.5 rounded-lg text-sm font-medium text-slate-300 hover:text-white hover:bg-slate-800/60 transition-all flex items-center gap-2"
          >
            <Server className="w-4 h-4" />
            Invite Bot
          </a>
        </nav>

        {/* Right User State / Discord Login */}
        <div className="flex items-center gap-3">
          <div className="hidden sm:flex items-center gap-3 bg-slate-900/80 px-3 py-1.5 rounded-xl border border-slate-800">
            <div className="w-7 h-7 rounded-full bg-purple-600/30 border border-purple-400/30 flex items-center justify-center text-purple-300 font-semibold text-xs">
              AD
            </div>
            <div className="text-left">
              <span className="text-xs font-semibold block text-slate-200">Server Administrator</span>
              <span className="text-[10px] text-emerald-400 flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                Connected
              </span>
            </div>
          </div>

          <Link
            href="/dashboard"
            className="px-4 py-2 rounded-xl text-sm font-semibold text-white bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 transition-all shadow-md shadow-purple-600/25 flex items-center gap-2"
          >
            <User className="w-4 h-4" />
            Login with Discord
          </Link>
        </div>

      </div>
    </header>
  );
}
