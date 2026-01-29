"""Engagement comment generation prompt templates for Clarity app."""


def get_comment_generation_prompt(
    video_summary: str,
    platform: str,
    post_url: str,
    caption: str | None = None,
) -> str:
    """
    Generate a prompt for creating engagement comments.

    Args:
        video_summary: Summary of the video content
        platform: Target platform (instagram or tiktok)
        post_url: URL to the post
        caption: Optional caption from the post

    Returns:
        The formatted prompt for Gemini
    """
    platform_guidelines = _get_platform_guidelines(platform)

    caption_section = ""
    if caption:
        caption_section = f"""
## Post Caption
```
{caption}
```

"""

    return f"""You are a social media engagement specialist for **Clarity**, an AI-powered study app. Generate authentic comments that feel like they're from real students/professionals who discovered the app.

## About Clarity
AI-powered study companion that helps with:
- Lecture transcription & AI summaries
- Chat with documents/videos
- Adaptive quizzes & flashcards
- AI Personal Tutor with study plans
- Gamification (streaks, XP)

## Target Personas (Write Comments From Their Perspective)

1. **The Overwhelmed Undergrad** (18-22)
   - Speaks like: "omg where was this during midterms 😭", "I literally have 5 lectures to catch up on"
   - Pain: Can't keep up with lectures, messy notes, cramming

2. **The Burnt-Out Grad Student** (22-28)
   - Speaks like: "dissertation is killing me rn", "spent 6 hours reading and retained nothing"
   - Pain: Research overload, reading hundreds of papers

3. **The Working Professional** (24-35)
   - Speaks like: "studying for the CPA while working full-time is brutal", "no energy after work"
   - Pain: No time, certification exam stress

4. **The Pre-Med/Pre-Law Gunner** (19-25)
   - Speaks like: "MCAT prep is ruining my life", "need that 520+"
   - Pain: Competitive pressure, massive content volume

5. **The ADHD/Neurodivergent Learner** (18-29)
   - Speaks like: "my ADHD brain could never with traditional studying", "I zone out 5 min into any lecture"
   - Pain: Can't focus, traditional methods don't work

## Video Summary
{video_summary}
{caption_section}
## Post URL
{post_url}

## Platform
{platform.upper()}

## Platform-Specific Guidelines
{platform_guidelines}

## Comment Rules

**LENGTH IS CRITICAL:**
- TikTok: 1 sentence MAX (under 15 words)
- Instagram: 1-2 sentences MAX (under 25 words)
- Comments that are too long look fake and get ignored

**DO:**
- Sound like a real person's gut reaction
- Use lowercase, casual punctuation
- Reference specific struggles briefly

**DON'T:**
- Write paragraphs
- Sound like a brand or bot
- Use generic praise ("Great video!")
- Over-explain

## Task
Generate 5 short comments. For EACH comment, also provide 2 quick reply options the creator can use when people respond.

### Comment 1 - The Overwhelmed Student
**Comment:** [1-2 sentences max - an undergrad who relates to the struggle]
**Reply Options:**
- [Short reply if someone agrees/relates]
- [Short reply if someone asks a question]

### Comment 2 - The Curious Skeptic
**Comment:** [1 sentence - genuine question about how it works]
**Reply Options:**
- [Reply explaining briefly]
- [Reply redirecting to try it]

### Comment 3 - The Testimony
**Comment:** [1-2 sentences - brief personal win, be specific]
**Reply Options:**
- [Reply if someone asks for more details]
- [Reply if someone is skeptical]

### Comment 4 - The "Where Was This" Reactor
**Comment:** [1 sentence - regret they didn't have this sooner]
**Reply Options:**
- [Reply agreeing/relating]
- [Reply encouraging them]

### Comment 5 - The Niche Persona
**Comment:** [1-2 sentences - from grad student, working professional, pre-med, or ADHD learner perspective]
**Reply Options:**
- [Reply if someone from same niche responds]
- [Reply if someone asks about their situation]

---

**Best Posting Times:** [Brief note on optimal timing for student content]
"""


def _get_platform_guidelines(platform: str) -> str:
    """Get platform-specific guidelines for comments."""
    guidelines = {
        "instagram": """
**Length:** MAX 1-2 short sentences (under 25 words total)

**Tone by Persona:**
- Overwhelmed Undergrad: "omg where was this during midterms 😭", "I literally have 5 lectures to catch up on"
- Burnt-Out Grad Student: "dissertation is killing me rn", "spent 6 hours reading and retained nothing"
- Working Professional: "studying for the CPA while working full-time is brutal"
- Pre-Med/Pre-Law: "MCAT prep is ruining my life", "need that 520+"
- ADHD Learner: "my ADHD brain could never with traditional studying"

**Emojis:** 😭🙏💀✨📚🧠😩

**Good examples:**
- "me during finals week omg 😭"
- "wait does this work for med school lectures?"
- "this wouldve saved me last semester fr"
""",
        "tiktok": """
**Length:** MAX 1 sentence (under 15 words) - shorter is better

**Tone by Persona:**
- Overwhelmed Undergrad: "no bc why is this exactly what i needed 😭"
- Burnt-Out Grad Student: "me pretending my thesis doesnt exist while watching this"
- Working Professional: "crying in corporate rn"
- Pre-Med/Pre-Law: "WHERE WAS THIS FOR MCAT PREP"
- ADHD Learner: "the way my adhd brain just understood this immediately"

**Style:** All lowercase, casual, meme-y, all caps for emphasis

**Good examples:**
- "WHERE WAS THIS DURING FINALS 😭"
- "the way i SPRINTED to download this"
- "not me watching this at 2am instead of studying 💀"
- "this is the sign i needed to get my life together"
""",
    }

    return guidelines.get(platform.lower(), guidelines["instagram"])
