# Quick Start: Using Agent.md

**Created:** 2026-01-31  
**Purpose:** Fast guide to using the new Agent.md file

---

## For AI DJs: How to Use Agent.md

### 1. At Session Start

When initializing your AI DJ (Claude, GPT-4, Gemini, etc.), feed it this exact text:

```
Please read and internalize the following instruction file for your role as Backlink Broadcast DJ:

[PASTE ENTIRE CONTENTS OF Agent.md HERE]

This is your personality, voice, and operational guide. Follow it precisely.
```

### 2. During Broadcast

**Before each show segment:**
- Check listener locations and time zones
- Review last 10 songs played (avoid repeats)
- Load appropriate persona (Morning/Afternoon/Evening)
- Queue 2-3 tracks following Variety Engine rules

**Every hour:**
- Run anti-repetition self-check
- Verify you're following the 4th wall rules
- Confirm talk segments under 60 seconds

### 3. Quick Reference

| Time | Persona | Vibe | Music Style |
|------|---------|------|-------------|
| 6AM-12PM | Morning | Energetic, optimistic | Upbeat, driving |
| 12PM-6PM | Afternoon | Steady, focused | Focus flow, anthems |
| 6PM-6AM | Evening | Chill, introspective | Lo-fi, jazz, downtempo |

**"Update on the 8s" Protocol:**
- XX:08 → Local lock (listener location)
- XX:38 → Station ID

**Golden Rule:** When in doubt, play the music.

---

## For Developers: Implementation

### Option 1: Direct Prompt Injection
```python
with open('Agent.md', 'r') as f:
    agent_instructions = f.read()

response = llm.chat([
    {"role": "system", "content": agent_instructions},
    {"role": "user", "content": "Start the morning show"}
])
```

### Option 2: Context Caching (Recommended)
```python
# Using Anthropic Claude with prompt caching
import anthropic

client = anthropic.Anthropic()

with open('Agent.md', 'r') as f:
    agent_instructions = f.read()

message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    system=[
        {
            "type": "text",
            "text": agent_instructions,
            "cache_control": {"type": "ephemeral"}
        }
    ],
    messages=[
        {"role": "user", "content": "Start the evening show"}
    ]
)
```

### Option 3: With Memory (LangChain)
```python
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

with open('Agent.md', 'r') as f:
    agent_instructions = f.read()

memory = ConversationBufferMemory()
chain = ConversationChain(
    llm=your_llm,
    memory=memory,
    system_message=agent_instructions
)
```

---

## For Station Operators: Customization

### 1. Brand Your Station
Edit these sections in Agent.md:
- Line 4: Update VERSION
- Lines 13-16: Update station name, frequency, URLs
- Lines 283-290: Customize station IDs
- Lines 320-330: Update documentation references

### 2. Adjust Voice
Edit these sections:
- Lines 50-88: Time-based persona characteristics
- Lines 90-120: Language and style rules
- Lines 122-138: Anti-repetition protocol (add your own forbidden phrases)

### 3. Music Policy
Edit these sections:
- Lines 142-180: Variety Engine rules
- Lines 182-194: Budget management strategy
- Lines 196-208: Contextual play guidelines

### 4. Interaction Rules
Edit these sections:
- Lines 244-262: Listener interaction responses
- Lines 264-270: Safety and moderation

---

## Next Steps

1. **Immediate:**
   - [ ] Read Agent.md in full
   - [ ] Feed to your AI DJ system
   - [ ] Test with sample broadcast

2. **This Week:**
   - [ ] Implement memory system (Redis/Mem0/LangChain)
   - [ ] Study Deej-AI repository
   - [ ] Customize Agent.md for your brand

3. **This Month:**
   - [ ] Study Rasa for personality development
   - [ ] Integrate weather/news APIs
   - [ ] Build listener history tracking
   - [ ] Deploy intelligence bees (optional)

---

## Troubleshooting

**Problem:** DJ sounds robotic
**Solution:** Re-emphasize section "The 4th Wall is Absolute" (lines 28-37)

**Problem:** Repetitive phrases
**Solution:** Check Anti-Repetition Protocol (lines 122-138), add specific phrases

**Problem:** Too much talking
**Solution:** Remind about 60-second max talk window (line 23)

**Problem:** Music selection feels random
**Solution:** Review The Variety Engine (lines 144-161) and Contextual Play (lines 196-208)

**Problem:** Lost context between sessions
**Solution:** Implement memory system (see AGENT_RECOMMENDATIONS.md)

---

## Support Resources

- **Full Evaluation:** See `AGENT_RECOMMENDATIONS.md`
- **Training Repos:** See Agent.md lines 312-379
- **Hive Architecture:** See `hive/SWARM_ROLES.md`
- **Station Manifesto:** See `docs/lore/STATION_MANIFESTO.md`

---

## Quick Links

| Resource | Purpose |
|----------|---------|
| [Agent.md](./Agent.md) | Main instruction file |
| [AGENT_RECOMMENDATIONS.md](./AGENT_RECOMMENDATIONS.md) | Evaluation & recommendations |
| [Deej-AI](https://github.com/teticio/Deej-AI) | Music curation learning |
| [Rasa](https://github.com/RasaHQ/rasa) | Personality development |
| [Awesome-Agent-Memory](https://github.com/TeleAI-UAGI/Awesome-Agent-Memory) | Memory systems |

---

**Status:** Production Ready ✅  
**Last Updated:** 2026-01-31
