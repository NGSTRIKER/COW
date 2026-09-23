"use client";

import { useState } from "react";
import Link from "next/link";
import { Server, Settings, ShieldCheck, Search, PlusCircle, CheckCircle2, AlertCircle } from "lucide-react";

// Mock Discord Guild Data representing servers managed by the admin user
const MOCK_GUILDS = [
  {
    id: "1398024265655128194",
    name: "Hu Immortal Blessed Land",
    icon: "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=150&auto=format&fit=crop&q=80",
    members: 1420,
    hasBot: true,
    securityActive: true,
    xpActive: true,
    role: "Server Owner",
  },
  {
    id: "987654321098765432",
    name: "Gu Cultivation Alliance",
    icon: "https://images.unsplash.com/photo-1579783902614-a3fb3927b675?w=150&auto=format&fit=crop&q=80",
    members: 850,
    hasBot: true,
    securityActive: true,
    xpActive: false,
    role: "Administrator",
  },
  {
    id: "112233445566778899",
    name: "Dang Hun Mountain Peak",
    icon: "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=150&auto=format&fit=crop&q=80",
    members: 310,
    hasBot: false,
    securityActive: false,
    xpActive: false,
    role: "Administrator",
  }
];

export default function ServerSelector() {
  const [searchQuery, setSearchQuery] = useState("");

  const filteredGuilds = MOCK_GUILDS.filter((guild) =>
    guild.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      
      {/* Header Title */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-10 pb-6 border-b border-slate-800/80">
        <div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight flex items-center gap-3">
            <Server className="w-8 h-8 text-purple-400" />
            Select a Server
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Select a Discord server where you have Manage Server or Administrator permissions to configure settings.
          </p>
        </div>

        {/* Search Bar */}
        <div className="relative w-full md:w-72">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search servers..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-900/90 border border-slate-800 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-purple-500/50 transition-colors"
          />
        </div>
      </div>

      {/* Guild Grid */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredGuilds.map((guild) => (
          <div
            key={guild.id}
            className="glass-card p-6 rounded-2xl border border-slate-800/80 flex flex-col justify-between group"
          >
            <div>
              {/* Guild Header Avatar & Badges */}
              <div className="flex items-start justify-between gap-4 mb-5">
                <div className="relative">
                  <img
                    src={guild.icon}
                    alt={guild.name}
                    className="w-16 h-16 rounded-2xl object-cover border-2 border-slate-700/60 group-hover:border-purple-500/50 transition-colors shadow-lg"
                  />
                  {guild.hasBot && (
                    <span className="absolute -bottom-1 -right-1 w-5 h-5 rounded-full bg-emerald-500 border-2 border-slate-950 flex items-center justify-center text-[10px] text-slate-950 font-bold">
                      ✓
                    </span>
                  )}
                </div>

                {guild.hasBot ? (
                  <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    Bot Active
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
                    <AlertCircle className="w-3.5 h-3.5" />
                    Invite Required
                  </span>
                )}
              </div>

              {/* Server Name & Meta */}
              <h2 className="text-xl font-bold text-white mb-1 group-hover:text-purple-300 transition-colors">
                {guild.name}
              </h2>
              <div className="flex items-center gap-3 text-xs text-slate-400 mb-6">
                <span>{guild.members.toLocaleString()} Members</span>
                <span>•</span>
                <span className="text-purple-400 font-medium">{guild.role}</span>
              </div>

              {/* Status Modules */}
              {guild.hasBot && (
                <div className="grid grid-cols-2 gap-2 mb-6">
                  <div className="bg-slate-900/60 p-2.5 rounded-xl border border-slate-800/60 text-xs">
                    <span className="text-slate-500 block mb-0.5">Security</span>
                    <span className={`font-semibold ${guild.securityActive ? "text-emerald-400" : "text-slate-400"}`}>
                      {guild.securityActive ? "Fox Nose Active" : "Disabled"}
                    </span>
                  </div>

                  <div className="bg-slate-900/60 p-2.5 rounded-xl border border-slate-800/60 text-xs">
                    <span className="text-slate-500 block mb-0.5">Leveling</span>
                    <span className={`font-semibold ${guild.xpActive ? "text-purple-400" : "text-slate-400"}`}>
                      {guild.xpActive ? "XP Active" : "Disabled"}
                    </span>
                  </div>
                </div>
              )}
            </div>

            {/* Action Button */}
            <div>
              {guild.hasBot ? (
                <Link
                  href={`/dashboard/${guild.id}`}
                  className="w-full py-3 px-4 rounded-xl text-sm font-semibold text-white bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 transition-all shadow-md shadow-purple-600/20 flex items-center justify-center gap-2"
                >
                  <Settings className="w-4 h-4" />
                  <span>Configure Dashboard</span>
                </Link>
              ) : (
                <a
                  href="https://discord.com"
                  target="_blank"
                  rel="noreferrer"
                  className="w-full py-3 px-4 rounded-xl text-sm font-semibold text-slate-200 glass-card hover:bg-slate-800 transition-all border border-slate-700/60 flex items-center justify-center gap-2"
                >
                  <PlusCircle className="w-4 h-4 text-purple-400" />
                  <span>Invite Bot</span>
                </a>
              )}
            </div>

          </div>
        ))}
      </div>

    </div>
  );
}
