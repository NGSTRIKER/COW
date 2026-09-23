# 🦊 Little Hu Immortal - Discord Bot (Hu Immortal Blessed Land Theme)

A Discord Bot themed after **Little Hu Immortal (Land Spirit of Hu Immortal Blessed Land)** from *Reverend Insanity*.

## 🌸 Features

### 🦊 Fox Nose (Divine Sniffing Gu & Anti-Raid Protection)
- **Suspect / Fake Account Sniffing**: Calculates a **Suspect Score (0 - 100)** for joining users based on Account Age, Default Avatars, Suspicious Username Formats, and Raid Context.
- **Auto-Quarantine**: Automatically times out accounts with high suspect scores (>= 70).
- **Raid Surge Lockdown**: Detects join bursts and automatically enables **Raid Lockdown Mode** for 10 minutes, notifying moderators in the log channel.
- **Slash Commands**:
  - `/fox_nose status` - View anti-raid status and current settings.
  - `/fox_nose audit @user` - Manually trigger Fox Nose sniffing on a user.
  - `/fox_nose clear_lockdown` - Deactivate active raid lockdown mode.

---

### 🏔️ Hu Immortal Blessed Land Flavor & Moderation
- **Greetings**: `"🌸 Master, welcome to Hu Immortal Blessed Land! Little Hu Immortal greets {user}! 🦊✨"`
- **Offerings**: Offer or serve items such as `guts gu`, `fox tea`, `primeval stone`, `pink crane`, and `starlight firefly`.
- **Moderation**:
  - `seal @user for <seconds> because <reason>` - Suppress an intruder beneath Dang Hun Mountain (timeout).
  - `expel @user` / `banish @user` / `execute @user` - Expel an intruder from Hu Immortal Blessed Land (kick).
