"""Pydantic models for structured Gemini responses."""

from pydantic import BaseModel, Field


class VideoReview(BaseModel):
    """Structured response model for video review analysis."""

    target_persona: str = Field(
        description="Which persona(s) does this content target and how well it speaks to their pain points"
    )

    # Individual scores
    hook_score: int = Field(
        ge=0, le=30,
        description="Hook & First Impression score"
    )
    pacing_score: int = Field(
        ge=0, le=15,
        description="Pacing & Energy score"
    )
    narrative_score: int = Field(
        ge=0, le=20,
        description="Problem-Solution Narrative score"
    )
    feature_demo_score: int = Field(
        ge=0, le=15,
        description="Feature Demonstration score"
    )
    technical_score: int = Field(
        ge=0, le=10,
        description="Technical Execution score"
    )
    trend_score: int = Field(
        ge=0, le=10,
        description="Trend & Platform Fit score"
    )
    shareability_score: int = Field(
        ge=0, le=5,
        description="Shareability & Virality Signals score"
    )
    caption_score: int | None = Field(
        default=None,
        ge=0, le=15,
        description="Caption Analysis score (only present when caption is provided)"
    )

    # Focus assessment
    features_shown: list[str] = Field(
        description="List of features demonstrated in the video"
    )
    focus_rating: str = Field(
        description="Focus assessment: FOCUSED, NATURAL_FLOW, SCATTERED, or INFOMERCIAL"
    )

    # Overall assessment
    overall_score: int = Field(
        ge=0, le=100,
        description="Overall score out of 100 (percentage)"
    )
    virality_tier: str = Field(
        description="Predicted virality tier: LOW, MEDIUM, HIGH, or VIRAL"
    )

    # Detailed feedback
    key_strengths: list[str] = Field(
        min_length=1, max_length=5,
        description="Key strengths of the video (1-5 items)"
    )
    areas_for_improvement: list[str] = Field(
        min_length=1, max_length=5,
        description="Areas that need improvement (1-5 items)"
    )
    recommendations: str = Field(
        description="Specific, actionable recommendations to improve the content"
    )
    caption_suggestions: list[str] = Field(
        default_factory=list,
        description="Caption ideas that would work well with this video"
    )
    alternative_hooks: list[str] = Field(
        min_length=2, max_length=3,
        description="2-3 alternative hooks/angles that could work better"
    )

    # Detailed analysis sections
    hook_analysis: str = Field(
        description="Analysis of the opening - scroll-stopping power, first frame quality"
    )
    pacing_analysis: str = Field(
        description="Analysis of pacing, cuts, energy level, attention retention"
    )
    narrative_analysis: str = Field(
        description="Analysis of the transformation story and authenticity"
    )
    feature_analysis: str = Field(
        description="Analysis of feature demonstration and focus"
    )
    technical_analysis: str = Field(
        description="Analysis of video/audio quality, text overlays, readability"
    )
    trend_analysis: str = Field(
        description="Analysis of trending sounds/formats usage, platform fit"
    )
    shareability_analysis: str = Field(
        description="Analysis of tag-worthiness, rewatchability, desire creation"
    )
    caption_analysis: str | None = Field(
        default=None,
        description="Analysis of the caption (only when caption provided)"
    )

    def to_slack_message(self) -> str:
        """Format the review as a Slack message."""
        sections = []

        # Determine max scores based on whether caption was provided
        has_caption = self.caption_score is not None
        if has_caption:
            hook_max, trend_max = 25, 10
        else:
            hook_max, trend_max = 30, 5

        # Target Persona
        sections.append(f"*TARGET PERSONA FIT*\n{self.target_persona}")

        # Hook Analysis
        sections.append(
            f"*HOOK & FIRST IMPRESSION ANALYSIS*\n{self.hook_analysis}\n"
            f"*Hook Score: {self.hook_score}/{hook_max}*"
        )

        # Pacing Analysis
        sections.append(
            f"*PACING & ENERGY ANALYSIS*\n{self.pacing_analysis}\n"
            f"*Pacing Score: {self.pacing_score}/15*"
        )

        # Narrative Analysis
        sections.append(
            f"*PROBLEM-SOLUTION NARRATIVE ANALYSIS*\n{self.narrative_analysis}\n"
            f"*Narrative Score: {self.narrative_score}/20*"
        )

        # Feature Analysis
        features_list = ", ".join(self.features_shown) if self.features_shown else "None identified"
        sections.append(
            f"*FEATURE DEMONSTRATION ANALYSIS*\n{self.feature_analysis}\n"
            f"*Features Shown:* {features_list}\n"
            f"*Focus Rating:* {self.focus_rating}\n"
            f"*Feature Demo Score: {self.feature_demo_score}/15*"
        )

        # Technical Analysis
        sections.append(
            f"*TECHNICAL EXECUTION ANALYSIS*\n{self.technical_analysis}\n"
            f"*Technical Score: {self.technical_score}/10*"
        )

        # Trend Analysis
        sections.append(
            f"*TREND & PLATFORM FIT ANALYSIS*\n{self.trend_analysis}\n"
            f"*Trend Score: {self.trend_score}/{trend_max}*"
        )

        # Shareability Analysis
        sections.append(
            f"*SHAREABILITY ANALYSIS*\n{self.shareability_analysis}\n"
            f"*Shareability Score: {self.shareability_score}/5*"
        )

        # Caption Analysis (if present)
        if self.caption_analysis and self.caption_score is not None:
            sections.append(
                f"*CAPTION ANALYSIS*\n{self.caption_analysis}\n"
                f"*Caption Score: {self.caption_score}/15*"
            )

        # Divider and Overall
        sections.append("─" * 30)
        sections.append(
            f"*OVERALL SCORE: {self.overall_score}/100*\n\n"
            f"*Predicted Virality Tier: {self.virality_tier}*"
        )

        # Key Strengths
        strengths = "\n".join(f"• {s}" for s in self.key_strengths)
        sections.append(f"*Key Strengths*\n{strengths}")

        # Areas for Improvement
        improvements = "\n".join(f"• {i}" for i in self.areas_for_improvement)
        sections.append(f"*Areas for Improvement*\n{improvements}")

        # Recommendations
        sections.append(f"*Recommendations*\n{self.recommendations}")

        # Caption Suggestions (if any)
        if self.caption_suggestions:
            captions = "\n".join(f"• {c}" for c in self.caption_suggestions)
            sections.append(f"*Caption Suggestions*\n{captions}")

        # Alternative Hooks
        hooks = "\n".join(f"• {h}" for h in self.alternative_hooks)
        sections.append(f"*Best Performing Angles for This Content*\n{hooks}")

        return "\n\n".join(sections)
