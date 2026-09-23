"use client";

import Link from "next/link";
import { 
  ShieldCheck, 
  Zap, 
  Sparkles, 
  Sliders, 
  Award, 
  Users, 
  ChevronRight, 
  ArrowRight, 
  Bell,
  CheckCircle2,
  Lock,
  Layers
} from "lucide-react";

export default function Home() {
  return (
    <div className="relative overflow-hidden min-h-[calc(100vh-4rem)]">
      
      {/* Glow Background Orbs */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-purple-600/15 rounded-full blur-[140px] pointer-events-none" />
      <div className="absolute top-1/3 left-1/3 w-[400px] h-[400px] bg-cyan-500/10 rounded-full blur-[120px] pointer-events-none" />

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-16 pb-20 text-center relative z-10">
        
        {/* Status Pill */}
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-panel text-xs font-semibold text-purple-300 border border-purple-500/30 mb-8 shadow-lg shadow-purple-500/10">
          <Sparkles className="w-4 h-4 text-purple-400" />
          <span>Next.js Web Dashboard v2.0 Live</span>
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse ml-1" />
        </div>

        {/* Main Hero Headline */}
        <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-white max-w-4xl mx-auto leading-[1.15]">
          Manage & Secure Your Discord Server with{" "}
          <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-cyan-400 bg-clip-text text-transparent">
            Precision
          </span>
        </h1>

        <p className="mt-6 text-lg sm:text-xl text-slate-400 max-w-2xl mx-auto font-normal leading-relaxed">
          Comprehensive Discord administration panel featuring Fox Nose Anti-Raid detection, live XP level leaderboards, customizable welcome cards, and persistent database storage.
        </p>

        {/* CTA Buttons */}
        <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link
            href="/dashboard"
            className="w-full sm:w-auto px-8 py-4 rounded-xl text-base font-semibold text-white bg-gradient-to-r from-purple-600 via-indigo-600 to-cyan-600 hover:from-purple-500 hover:to-cyan-500 transition-all shadow-xl shadow-purple-600/30 flex items-center justify-center gap-3 group"
          >
            <span>Open Control Panel</span>
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </Link>
          <a
            href="https://discord.com"
            target="_blank"
            rel="noreferrer"
            className="w-full sm:w-auto px-8 py-4 rounded-xl text-base font-semibold text-slate-200 glass-card hover:bg-slate-800/80 transition-all flex items-center justify-center gap-2 border border-slate-700/60"
          >
            <ShieldCheck className="w-5 h-5 text-purple-400" />
            <span>Invite to Server</span>
          </a>
        </div>

        {/* Live Bot Statistics */}
        <div className="mt-20 grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
          <div className="glass-card p-6 rounded-2xl text-left border border-slate-800/80">
            <div className="w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400 mb-3">
              <Users className="w-5 h-5" />
            </div>
            <span className="text-3xl font-extrabold text-white block">14,250+</span>
            <span className="text-xs text-slate-400 font-medium">Monitored Members</span>
          </div>

          <div className="glass-card p-6 rounded-2xl text-left border border-slate-800/80">
            <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400 mb-3">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <span className="text-3xl font-extrabold text-white block">99.8%</span>
            <span className="text-xs text-slate-400 font-medium">Raid Detection Rate</span>
          </div>

          <div className="glass-card p-6 rounded-2xl text-left border border-slate-800/80">
            <div className="w-10 h-10 rounded-xl bg-pink-500/10 border border-pink-500/20 flex items-center justify-center text-pink-400 mb-3">
              <Award className="w-5 h-5" />
            </div>
            <span className="text-3xl font-extrabold text-white block">1.2M+</span>
            <span className="text-xs text-slate-400 font-medium">XP Awarded</span>
          </div>

          <div className="glass-card p-6 rounded-2xl text-left border border-slate-800/80">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 mb-3">
              <Zap className="w-5 h-5" />
            </div>
            <span className="text-3xl font-extrabold text-white block">&lt; 15ms</span>
            <span className="text-xs text-slate-400 font-medium">Database Response</span>
          </div>
        </div>

      </section>

      {/* Feature Grid */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 border-t border-slate-800/60">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <span className="text-xs font-bold uppercase tracking-wider text-purple-400 block mb-2">
            Powerful Modules
          </span>
          <h2 className="text-3xl sm:text-4xl font-bold text-white tracking-tight">
            Everything you need to manage your community
          </h2>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          
          {/* Card 1: Fox Nose */}
          <div className="glass-card p-8 rounded-2xl relative group overflow-hidden">
            <div className="w-12 h-12 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400 mb-6 group-hover:scale-110 transition-transform">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-bold text-white mb-2">Fox Nose Anti-Raid Engine</h3>
            <p className="text-sm text-slate-400 leading-relaxed mb-4">
              Calculates account risk scores (0-100) based on age, avatars, and username heuristics. Detects join velocity surges without autonomous penalties.
            </p>
            <ul className="space-y-2 text-xs text-slate-300">
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                No destructive autonomous actions
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                Custom moderation alert channels
              </li>
            </ul>
          </div>

          {/* Card 2: Interactive Dashboard */}
          <div className="glass-card p-8 rounded-2xl relative group overflow-hidden">
            <div className="w-12 h-12 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400 mb-6 group-hover:scale-110 transition-transform">
              <Sliders className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-bold text-white mb-2">Web Control Panel</h3>
            <p className="text-sm text-slate-400 leading-relaxed mb-4">
              Configure every module from an intuitive browser interface. Real-time updates directly synced with PostgreSQL database storage.
            </p>
            <ul className="space-y-2 text-xs text-slate-300">
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                Discord OAuth2 Security
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                Persistent Database Sync
              </li>
            </ul>
          </div>

          {/* Card 3: XP & Leveling */}
          <div className="glass-card p-8 rounded-2xl relative group overflow-hidden">
            <div className="w-12 h-12 rounded-xl bg-pink-500/10 border border-pink-500/20 flex items-center justify-center text-pink-400 mb-6 group-hover:scale-110 transition-transform">
              <Award className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-bold text-white mb-2">XP & Leveling System</h3>
            <p className="text-sm text-slate-400 leading-relaxed mb-4">
              Reward active server members with chat experience points, level-up card displays, anti-spam cooldowns, and server leaderboards.
            </p>
            <ul className="space-y-2 text-xs text-slate-300">
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                Custom XP range & cooldowns
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                Slash commands (/rank, /leaderboard)
              </li>
            </ul>
          </div>

        </div>
      </section>

      {/* CTA Footer Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 text-center">
        <div className="glass-panel p-10 sm:p-16 rounded-3xl border border-purple-500/20 relative overflow-hidden">
          <div className="relative z-10 max-w-2xl mx-auto">
            <h2 className="text-3xl font-extrabold text-white mb-4">
              Ready to take control of your server?
            </h2>
            <p className="text-slate-400 text-sm mb-8">
              Access the Next.js Web Dashboard to customize your modules, review security logs, and manage community rankings.
            </p>
            <Link
              href="/dashboard"
              className="inline-flex items-center gap-3 px-8 py-4 rounded-xl text-base font-semibold text-white bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 transition-all shadow-lg shadow-purple-600/30"
            >
              <span>Launch Dashboard</span>
              <ChevronRight className="w-5 h-5" />
            </Link>
          </div>
        </div>
      </section>

    </div>
  );
}
