"use client";

import { useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { 
  ShieldCheck, 
  Sparkles, 
  MessageSquare, 
  Award, 
  Sliders, 
  Check, 
  X, 
  ArrowLeft, 
  Save, 
  RefreshCw, 
  AlertTriangle, 
  Eye, 
  Users, 
  Hash, 
  Bot, 
  Clock, 
  UserCheck, 
  Layers
} from "lucide-react";

export default function ServerDashboard() {
  const params = useParams();
  const guildId = params.guildId as string;

  // Navigation Tab State
  const [activeTab, setActiveTab] = useState<"overview" | "security" | "welcome" | "xp" | "autorole">("overview");

  // Interactive Form Controls State
  const [foxNoseEnabled, setFoxNoseEnabled] = useState(true);
  const [foxLogChannel, setFoxLogChannel] = useState("123456789012345678");
  const [autoQuarantineScore, setAutoQuarantineScore] = useState(70);

  const [welcomeEnabled, setWelcomeEnabled] = useState(true);
  const [welcomeChannel, setWelcomeChannel] = useState("987654321098765432");
  const [welcomeMessage, setWelcomeMessage] = useState("Welcome to the server, {user}! We are glad to have you here.");

  const [xpEnabled, setXpEnabled] = useState(true);
  const [xpMin, setXpMin] = useState(10);
  const [xpMax, setXpMax] = useState(20);
  const [xpCooldown, setXpCooldown] = useState(30);

  const [savedNotification, setSavedNotification] = useState(false);

  const handleSave = () => {
    setSavedNotification(true);
    setTimeout(() => setSavedNotification(false), 3000);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      
      {/* Top Header / Breadcrumb */}
      <div className="mb-8 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-purple-300 transition-colors mb-3"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            Back to Server Selector
          </Link>

          <div className="flex items-center gap-4">
            <img
              src="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=150&auto=format&fit=crop&q=80"
              alt="Server Avatar"
              className="w-14 h-14 rounded-2xl border-2 border-purple-500/40 shadow-lg"
            />
            <div>
              <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-3">
                Hu Immortal Blessed Land
              </h1>
              <div className="flex items-center gap-3 text-xs text-slate-400 mt-1">
                <span>Guild ID: <code className="text-slate-300 font-mono">{guildId}</code></span>
                <span>•</span>
                <span className="text-emerald-400 flex items-center gap-1 font-medium">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  Bot Connected
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Save Button & Feedback Toast */}
        <div className="flex items-center gap-3">
          {savedNotification && (
            <div className="px-3 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-medium flex items-center gap-2 animate-fade-in">
              <Check className="w-4 h-4" />
              Settings saved to database!
            </div>
          )}

          <button
            onClick={handleSave}
            className="px-6 py-2.5 rounded-xl text-sm font-semibold text-white bg-gradient-to-r from-purple-600 via-indigo-600 to-cyan-600 hover:from-purple-500 hover:to-cyan-500 transition-all shadow-lg shadow-purple-600/25 flex items-center gap-2"
          >
            <Save className="w-4 h-4" />
            Save Changes
          </button>
        </div>
      </div>

      {/* Control Panel Tab Navigation */}
      <div className="flex items-center gap-2 overflow-x-auto pb-3 mb-8 border-b border-slate-800/80">
        <button
          onClick={() => setActiveTab("overview")}
          className={`px-4 py-2.5 rounded-xl text-sm font-semibold transition-all flex items-center gap-2.5 whitespace-nowrap ${
            activeTab === "overview"
              ? "bg-purple-600/20 text-purple-300 border border-purple-500/40 shadow-lg shadow-purple-500/10"
              : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/60"
          }`}
        >
          <Sliders className="w-4 h-4" />
          Overview
        </button>

        <button
          onClick={() => setActiveTab("security")}
          className={`px-4 py-2.5 rounded-xl text-sm font-semibold transition-all flex items-center gap-2.5 whitespace-nowrap ${
            activeTab === "security"
              ? "bg-purple-600/20 text-purple-300 border border-purple-500/40 shadow-lg shadow-purple-500/10"
              : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/60"
          }`}
        >
          <ShieldCheck className="w-4 h-4" />
          Fox Nose Security
        </button>

        <button
          onClick={() => setActiveTab("welcome")}
          className={`px-4 py-2.5 rounded-xl text-sm font-semibold transition-all flex items-center gap-2.5 whitespace-nowrap ${
            activeTab === "welcome"
              ? "bg-purple-600/20 text-purple-300 border border-purple-500/40 shadow-lg shadow-purple-500/10"
              : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/60"
          }`}
        >
          <MessageSquare className="w-4 h-4" />
          Welcome System
        </button>

        <button
          onClick={() => setActiveTab("xp")}
          className={`px-4 py-2.5 rounded-xl text-sm font-semibold transition-all flex items-center gap-2.5 whitespace-nowrap ${
            activeTab === "xp"
              ? "bg-purple-600/20 text-purple-300 border border-purple-500/40 shadow-lg shadow-purple-500/10"
              : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/60"
          }`}
        >
          <Award className="w-4 h-4" />
          XP & Leveling
        </button>

        <button
          onClick={() => setActiveTab("autorole")}
          className={`px-4 py-2.5 rounded-xl text-sm font-semibold transition-all flex items-center gap-2.5 whitespace-nowrap ${
            activeTab === "autorole"
              ? "bg-purple-600/20 text-purple-300 border border-purple-500/40 shadow-lg shadow-purple-500/10"
              : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/60"
          }`}
        >
          <Layers className="w-4 h-4" />
          Reaction Roles
        </button>
      </div>

      {/* TAB CONTENT 1: OVERVIEW */}
      {activeTab === "overview" && (
        <div className="space-y-8">
          {/* Quick Metrics Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="glass-card p-6 rounded-2xl border border-slate-800/80">
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs font-semibold text-slate-400">Total Members</span>
                <Users className="w-5 h-5 text-purple-400" />
              </div>
              <span className="text-3xl font-extrabold text-white">1,420</span>
              <span className="text-xs text-emerald-400 block mt-2 font-medium">+14 this week</span>
            </div>

            <div className="glass-card p-6 rounded-2xl border border-slate-800/80">
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs font-semibold text-slate-400">Fox Nose Security</span>
                <ShieldCheck className="w-5 h-5 text-emerald-400" />
              </div>
              <span className="text-3xl font-extrabold text-white">Active</span>
              <span className="text-xs text-slate-400 block mt-2 font-medium">0 Raids active</span>
            </div>

            <div className="glass-card p-6 rounded-2xl border border-slate-800/80">
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs font-semibold text-slate-400">XP System</span>
                <Award className="w-5 h-5 text-pink-400" />
              </div>
              <span className="text-3xl font-extrabold text-white">Enabled</span>
              <span className="text-xs text-slate-400 block mt-2 font-medium">30s anti-spam cooldown</span>
            </div>

            <div className="glass-card p-6 rounded-2xl border border-slate-800/80">
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs font-semibold text-slate-400">Database Sync</span>
                <Sparkles className="w-5 h-5 text-cyan-400" />
              </div>
              <span className="text-3xl font-extrabold text-white">Synced</span>
              <span className="text-xs text-emerald-400 block mt-2 font-medium">PostgreSQL Live Storage</span>
            </div>
          </div>

          {/* Module Status Cards */}
          <div className="grid md:grid-cols-2 gap-6">
            
            <div className="glass-card p-6 rounded-2xl border border-slate-800/80">
              <h3 className="text-lg font-bold text-white mb-2 flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-purple-400" />
                Fox Nose Anti-Raid Status
              </h3>
              <p className="text-xs text-slate-400 mb-6">
                Analyzes joining user accounts and flags raid surges without taking destructive auto-actions.
              </p>
              <div className="flex items-center justify-between p-4 rounded-xl bg-slate-900/60 border border-slate-800">
                <span className="text-sm font-semibold text-slate-200">Security Monitoring</span>
                <button
                  onClick={() => setFoxNoseEnabled(!foxNoseEnabled)}
                  className={`w-12 h-6 rounded-full transition-colors relative p-1 ${
                    foxNoseEnabled ? "bg-purple-600" : "bg-slate-700"
                  }`}
                >
                  <div
                    className={`w-4 h-4 rounded-full bg-white transition-transform ${
                      foxNoseEnabled ? "translate-x-6" : "translate-x-0"
                    }`}
                  />
                </button>
              </div>
            </div>

            <div className="glass-card p-6 rounded-2xl border border-slate-800/80">
              <h3 className="text-lg font-bold text-white mb-2 flex items-center gap-2">
                <Award className="w-5 h-5 text-pink-400" />
                XP & Leveling System Status
              </h3>
              <p className="text-xs text-slate-400 mb-6">
                Awards chat experience points to active server members and tracks rankings.
              </p>
              <div className="flex items-center justify-between p-4 rounded-xl bg-slate-900/60 border border-slate-800">
                <span className="text-sm font-semibold text-slate-200">XP Distribution</span>
                <button
                  onClick={() => setXpEnabled(!xpEnabled)}
                  className={`w-12 h-6 rounded-full transition-colors relative p-1 ${
                    xpEnabled ? "bg-purple-600" : "bg-slate-700"
                  }`}
                >
                  <div
                    className={`w-4 h-4 rounded-full bg-white transition-transform ${
                      xpEnabled ? "translate-x-6" : "translate-x-0"
                    }`}
                  />
                </button>
              </div>
            </div>

          </div>
        </div>
      )}

      {/* TAB CONTENT 2: FOX NOSE SECURITY */}
      {activeTab === "security" && (
        <div className="space-y-8">
          
          <div className="glass-card p-8 rounded-2xl border border-slate-800/80">
            <h2 className="text-xl font-bold text-white mb-2 flex items-center gap-2">
              <ShieldCheck className="w-6 h-6 text-purple-400" />
              Fox Nose Security Settings
            </h2>
            <p className="text-xs text-slate-400 mb-8">
              Configure parameters for incoming account risk analysis and raid surge detection notifications.
            </p>

            <div className="space-y-6">
              {/* Module Toggle */}
              <div className="flex items-center justify-between pb-6 border-b border-slate-800/60">
                <div>
                  <label className="text-sm font-bold text-slate-200 block mb-1">
                    Enable Fox Nose Security Monitoring
                  </label>
                  <span className="text-xs text-slate-400">
                    When enabled, the bot sniffs incoming join accounts and alerts mods if risk score &ge; 30.
                  </span>
                </div>
                <button
                  onClick={() => setFoxNoseEnabled(!foxNoseEnabled)}
                  className={`w-14 h-7 rounded-full transition-colors relative p-1 ${
                    foxNoseEnabled ? "bg-purple-600" : "bg-slate-700"
                  }`}
                >
                  <div
                    className={`w-5 h-5 rounded-full bg-white transition-transform ${
                      foxNoseEnabled ? "translate-x-7" : "translate-x-0"
                    }`}
                  />
                </button>
              </div>

              {/* Channel Selector */}
              <div>
                <label className="text-sm font-bold text-slate-200 block mb-2">
                  Security Log Channel
                </label>
                <select
                  value={foxLogChannel}
                  onChange={(e) => setFoxLogChannel(e.target.value)}
                  className="w-full max-w-md px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-sm text-slate-200 focus:outline-none focus:border-purple-500/50"
                >
                  <option value="123456789012345678">#mod-security-alerts</option>
                  <option value="987654321098765432">#general</option>
                  <option value="">Default System Channel</option>
                </select>
              </div>
            </div>
          </div>

          {/* Recent Security Logs Table Preview */}
          <div className="glass-card p-8 rounded-2xl border border-slate-800/80">
            <h3 className="text-lg font-bold text-white mb-4">Recent Join Security Logs</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-300">
                <thead className="bg-slate-900/80 text-slate-400 font-semibold border-b border-slate-800">
                  <tr>
                    <th className="p-3">User</th>
                    <th className="p-3">Account Age</th>
                    <th className="p-3">Risk Score</th>
                    <th className="p-3">Risk Indicators</th>
                    <th className="p-3">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  <tr>
                    <td className="p-3 font-semibold text-slate-200 flex items-center gap-2">
                      <div className="w-6 h-6 rounded-full bg-slate-800 flex items-center justify-center font-bold text-[10px]">U1</div>
                      user_9921
                    </td>
                    <td className="p-3 text-slate-400">2 hours ago</td>
                    <td className="p-3 font-bold text-rose-400">85 / 100</td>
                    <td className="p-3 text-slate-400">Account &lt; 24h (+50), Default Avatar (+20), Pattern Match (+15)</td>
                    <td className="p-3">
                      <span className="px-2 py-0.5 rounded-md bg-rose-500/10 text-rose-400 font-semibold border border-rose-500/20">
                        High Suspicion
                      </span>
                    </td>
                  </tr>

                  <tr>
                    <td className="p-3 font-semibold text-slate-200 flex items-center gap-2">
                      <div className="w-6 h-6 rounded-full bg-slate-800 flex items-center justify-center font-bold text-[10px]">U2</div>
                      AlexG
                    </td>
                    <td className="p-3 text-slate-400">3 years ago</td>
                    <td className="p-3 font-bold text-emerald-400">0 / 100</td>
                    <td className="p-3 text-slate-400">None</td>
                    <td className="p-3">
                      <span className="px-2 py-0.5 rounded-md bg-emerald-500/10 text-emerald-400 font-semibold border border-emerald-500/20">
                        Clear
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

        </div>
      )}

      {/* TAB CONTENT 3: WELCOME SYSTEM */}
      {activeTab === "welcome" && (
        <div className="grid md:grid-cols-2 gap-8">
          
          {/* Settings Column */}
          <div className="glass-card p-8 rounded-2xl border border-slate-800/80">
            <h2 className="text-xl font-bold text-white mb-2 flex items-center gap-2">
              <MessageSquare className="w-6 h-6 text-purple-400" />
              Welcome System Settings
            </h2>
            <p className="text-xs text-slate-400 mb-8">
              Configure automated join greetings dispatched when new members enter the server.
            </p>

            <div className="space-y-6">
              <div>
                <label className="text-sm font-bold text-slate-200 block mb-2">
                  Destination Welcome Channel
                </label>
                <select
                  value={welcomeChannel}
                  onChange={(e) => setWelcomeChannel(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-sm text-slate-200 focus:outline-none focus:border-purple-500/50"
                >
                  <option value="987654321098765432">#welcome-and-rules</option>
                  <option value="123456789012345678">#general</option>
                </select>
              </div>

              <div>
                <label className="text-sm font-bold text-slate-200 block mb-2">
                  Welcome Message Template
                </label>
                <textarea
                  rows={4}
                  value={welcomeMessage}
                  onChange={(e) => setWelcomeMessage(e.target.value)}
                  className="w-full px-4 py-3 rounded-xl bg-slate-900 border border-slate-800 text-sm text-slate-200 focus:outline-none focus:border-purple-500/50"
                />
                <span className="text-[11px] text-slate-500 block mt-1">
                  Use <code className="text-purple-400">&#123;user&#125;</code> to mention the joining member.
                </span>
              </div>
            </div>
          </div>

          {/* Live Preview Column */}
          <div className="glass-card p-8 rounded-2xl border border-slate-800/80">
            <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-2">
              <Eye className="w-4 h-4 text-purple-400" />
              Live Message Preview
            </h3>
            
            {/* Discord Message Mockup */}
            <div className="bg-[#313338] p-4 rounded-xl border border-slate-700/60 font-sans">
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-full bg-purple-600 flex items-center justify-center font-bold text-white text-xs">
                  Bot
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-sm text-white">Hu Immortal Bot</span>
                    <span className="bg-[#5865F2] text-[10px] text-white px-1.5 py-0.2 rounded font-medium">BOT</span>
                    <span className="text-xs text-gray-400">Today at 4:30 PM</span>
                  </div>
                  <p className="text-sm text-gray-200 mt-1">
                    {welcomeMessage.replace("{user}", "@NewMember")}
                  </p>
                </div>
              </div>
            </div>
          </div>

        </div>
      )}

      {/* TAB CONTENT 4: XP & LEVELING */}
      {activeTab === "xp" && (
        <div className="space-y-8">
          
          <div className="glass-card p-8 rounded-2xl border border-slate-800/80">
            <h2 className="text-xl font-bold text-white mb-2 flex items-center gap-2">
              <Award className="w-6 h-6 text-pink-400" />
              XP & Leveling Settings
            </h2>
            <p className="text-xs text-slate-400 mb-8">
              Adjust experience point gain ranges and anti-spam cooldown parameters.
            </p>

            <div className="grid md:grid-cols-3 gap-6">
              <div>
                <label className="text-xs font-bold text-slate-300 block mb-2">Minimum XP per Message</label>
                <input
                  type="number"
                  value={xpMin}
                  onChange={(e) => setXpMin(Number(e.target.value))}
                  className="w-full px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-sm text-slate-200"
                />
              </div>

              <div>
                <label className="text-xs font-bold text-slate-300 block mb-2">Maximum XP per Message</label>
                <input
                  type="number"
                  value={xpMax}
                  onChange={(e) => setXpMax(Number(e.target.value))}
                  className="w-full px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-sm text-slate-200"
                />
              </div>

              <div>
                <label className="text-xs font-bold text-slate-300 block mb-2">Cooldown Timer (seconds)</label>
                <input
                  type="number"
                  value={xpCooldown}
                  onChange={(e) => setXpCooldown(Number(e.target.value))}
                  className="w-full px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-sm text-slate-200"
                />
              </div>
            </div>
          </div>

          {/* Server Leaderboard Preview */}
          <div className="glass-card p-8 rounded-2xl border border-slate-800/80">
            <h3 className="text-lg font-bold text-white mb-4">Top Server Members Leaderboard</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-4 rounded-xl bg-slate-900/60 border border-slate-800">
                <div className="flex items-center gap-4">
                  <span className="font-extrabold text-amber-400 text-lg w-6">#1</span>
                  <div className="w-8 h-8 rounded-full bg-purple-600 flex items-center justify-center font-bold text-xs">M1</div>
                  <div>
                    <span className="text-sm font-bold text-white block">Cultivator_Prime</span>
                    <span className="text-xs text-slate-400">1,420 Messages</span>
                  </div>
                </div>
                <div className="text-right">
                  <span className="text-sm font-bold text-purple-400 block">Level 14</span>
                  <span className="text-xs text-slate-400">18,450 XP</span>
                </div>
              </div>

              <div className="flex items-center justify-between p-4 rounded-xl bg-slate-900/60 border border-slate-800">
                <div className="flex items-center gap-4">
                  <span className="font-extrabold text-slate-300 text-lg w-6">#2</span>
                  <div className="w-8 h-8 rounded-full bg-cyan-600 flex items-center justify-center font-bold text-xs">M2</div>
                  <div>
                    <span className="text-sm font-bold text-white block">Shadow_Fox</span>
                    <span className="text-xs text-slate-400">980 Messages</span>
                  </div>
                </div>
                <div className="text-right">
                  <span className="text-sm font-bold text-purple-400 block">Level 11</span>
                  <span className="text-xs text-slate-400">12,100 XP</span>
                </div>
              </div>
            </div>
          </div>

        </div>
      )}

      {/* TAB CONTENT 5: REACTION ROLES */}
      {activeTab === "autorole" && (
        <div className="glass-card p-8 rounded-2xl border border-slate-800/80 text-center py-16">
          <Layers className="w-12 h-12 text-purple-400 mx-auto mb-4" />
          <h3 className="text-xl font-bold text-white mb-2">Reaction Role Builder</h3>
          <p className="text-sm text-slate-400 max-w-md mx-auto mb-6">
            Create visual reaction role messages with custom emoji mappings for server self-assignment.
          </p>
          <button className="px-6 py-3 rounded-xl text-sm font-semibold text-white bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 transition-all shadow-md shadow-purple-600/25">
            + Create New Reaction Role Message
          </button>
        </div>
      )}

    </div>
  );
}
