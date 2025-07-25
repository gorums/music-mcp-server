from typing import Dict, Any, List, Optional


def get_analyze_band_prompt(
    band_name: str = "", 
    albums: List[str] = None, 
    analyze_missing_albums: bool = False,
    analysis_scope: str = "full"
) -> Dict[str, Any]:
    """
    Generate a prompt template for analyzing bands with reviews, ratings, and similar bands.
    
    This prompt guides the AI to create comprehensive band analysis including:
    - Overall band review and rating
    - Album-specific reviews and ratings
    - Similar bands identification
    - Musical style and influence analysis
    
    Args:
        band_name: Name of the band to analyze (optional parameter for dynamic prompts)
        albums: List of albums to include in analysis (optional)
        analyze_missing_albums: If True, include analysis for missing albums too
        analysis_scope: Scope of analysis - "basic", "full", or "albums_only" (default: "full")
        
    Returns:
        Dict containing MCP prompt specification with messages for band analysis
    """
    albums = albums or []
    
    # Validate analysis scope
    valid_scopes = ["basic", "full", "albums_only"]
    if analysis_scope not in valid_scopes:
        analysis_scope = "full"
    
    # Build prompt content - if no band_name provided, create a general template
    if band_name:
        prompt_content = _build_specific_band_analysis_prompt(band_name, albums, analyze_missing_albums, analysis_scope)
    else:
        prompt_content = _build_general_analysis_template(analysis_scope)
    
    return {
        "name": "analyze_band",
        "description": "Create comprehensive analysis of a band including reviews, ratings, and similar bands",
        "arguments": [
            {
                "name": "band_name",
                "description": "Name of the band to analyze",
                "required": True
            },
            {
                "name": "albums", 
                "description": "List of albums to include in analysis (optional)",
                "required": False
            },
            {
                "name": "analyze_missing_albums",
                "description": "Whether to include analysis for missing albums (default: false)",
                "required": False
            },
            {
                "name": "analysis_scope",
                "description": "Scope of analysis: 'basic', 'full', or 'albums_only'",
                "required": False
            }
        ],
        "messages": [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": prompt_content
                }
            }
        ]
    }


def _build_general_analysis_template(analysis_scope: str) -> str:
    """Build a general analysis template for any band."""
    if analysis_scope == "basic":
        return _build_basic_analysis_template()
    elif analysis_scope == "albums_only":
        return _build_albums_analysis_template()
    else:  # full
        return _build_full_analysis_template()


def _build_full_analysis_template() -> str:
    """Build the comprehensive band analysis template."""
    return """You are tasked with creating a comprehensive analysis of a music band for a music collection database. Provide thoughtful reviews, accurate ratings, and identify similar artists.\n\n**INSTRUCTIONS:**\nWhen provided with a band name and their discography, create a detailed analysis including overall band assessment and individual album reviews.\n\n**ANALYSIS OBJECTIVES:**\n1. Evaluate the band's overall musical contribution and significance\n2. Provide detailed album-by-album analysis and ratings\n3. Identify similar bands and musical influences\n4. Assess musical style, evolution, and impact\n\n**ANALYSIS COMPONENTS:**\n\n**Overall Band Analysis:**\n- Comprehensive review covering musical style, innovation, influence, and legacy\n- Overall band rating (1-10 scale, where 1=poor, 10=masterpiece)\n- Historical context and significance in music\n- Musical evolution and consistency\n\n**Album-Specific Analysis:**\n- Individual review for each album covering style, standout tracks, production\n- Album rating (1-10 scale, independent of overall band rating)\n- Context within band's discography\n- Notable features, experiments, or departures\n\n**Similar Bands Identification (Separated by Collection Presence):**\n- List similar bands that exist in the user's collection (field: similar_bands)\n- List similar bands that do NOT exist in the user's collection (field: similar_bands_missing)\n- If you do not know which bands are present, provide all in similar_bands\n- Do NOT include the same band in both arrays\n\n**RATING GUIDELINES:**\n**Overall Band Rating (1-10):**\n- 1-2: Poor, limited musical value\n- 3-4: Below average, some redeeming qualities\n- 5-6: Average, solid but unremarkable\n- 7-8: Good to very good, notable contribution\n- 9-10: Excellent to masterpiece, significant impact\n\n**Album Rating (1-10):**\n- Consider: songwriting quality, production, innovation, cohesion\n- Rate within context of the band's catalog and genre\n- Independent assessment from overall band rating\n\n**ANALYSIS QUALITY GUIDELINES:**\n1. **Accuracy**: Base analysis on musical facts and widely accepted critical consensus\n2. **Depth**: Provide detailed, thoughtful commentary beyond surface-level observations\n3. **Context**: Consider historical period, genre conventions, and band's trajectory\n4. **Objectivity**: Balance personal taste with critical assessment\n5. **Completeness**: Cover all provided albums with sufficient detail\n\n**OUTPUT FORMAT:**\nReturn the analysis in JSON format matching this schema:\n\n```json\n{\n  \"review\": \"Comprehensive overall band analysis covering musical style, innovation, influence, and legacy...\",\n  \"rate\": 8,\n  \"albums\": [\n    {\n      \"album_name\": \"Album Title\",\n      \"review\": \"Detailed album analysis covering style, standout tracks, production, and significance within discography...\",\n      \"rate\": 9\n    }\n  ],\n  \"similar_bands\": [\"Similar Band 1\", \"Similar Band 2\"],\n  \"similar_bands_missing\": [\"Missing Band 1\", \"Missing Band 2\"]\n}\n```\n\n**ANALYSIS STRATEGY:**\n1. Research the band's history, style, and critical reception\n2. Analyze their musical evolution and key periods\n3. Evaluate each album within context of their career and genre\n4. Identify musical connections and influences\n5. Provide ratings that reflect both artistic merit and historical significance\n\n**VALIDATION RULES:**\n- Overall band rating must be 1-10 integer\n- Each album rating must be 1-10 integer  \n- Reviews should be substantial (minimum 50 words for band, 30 words per album)\n- Similar bands should be relevant and factually accurate\n- Include 3-8 similar bands for comprehensive comparison\n- If possible, always separate similar bands into those present in the user's collection (similar_bands) and those not present (similar_bands_missing)\n- Do not include the same band in both arrays\n\n**USAGE EXAMPLE:**\nWhen you receive a band like \"Pink Floyd\" with albums [\"The Dark Side of the Moon\", \"The Wall\"], provide comprehensive analysis including their progressive rock innovation, conceptual album mastery, and influence on modern music, with detailed album reviews and appropriate ratings.\n\n**IMPORTANT NOTES:**\n- Rate albums based on their individual merit, not just popularity\n- Consider both commercial and critical success in overall band assessment\n- Include lesser-known but critically acclaimed albums in analysis\n- Balance historical significance with actual musical quality"""


def _build_basic_analysis_template() -> str:
    """Build the basic analysis template focusing on essential elements."""
    return """You are tasked with creating a basic analysis of a music band for a music collection database. Focus on essential assessment elements.

**INSTRUCTIONS:**
When provided with a band name, create a concise but meaningful analysis covering the core elements.

**ANALYSIS COMPONENTS:**

**Essential Band Analysis:**
- Concise review covering musical style and significance (2-3 sentences)
- Overall band rating (1-10 scale)
- Brief assessment of their contribution to music

**Similar Bands:**
- 3-5 most relevant similar or influential bands
- Focus on direct stylistic connections

**RATING GUIDELINES:**
- 1-3: Limited appeal or poor quality
- 4-6: Average to good, solid contribution  
- 7-9: Very good to excellent, notable impact
- 10: Masterpiece level, transformative influence

**OUTPUT FORMAT:**
Return the analysis in JSON format:

```json
{
  "review": "Concise band analysis covering musical style and significance...",
  "rate": 8,
  "similar_bands": ["Similar Band 1", "Similar Band 2", "Influential Band"]
}
```

**ANALYSIS STRATEGY:**
1. Focus on the band's most significant contributions
2. Identify their primary musical style and innovation
3. Rate based on overall impact and quality
4. Select most relevant similar artists

**USAGE EXAMPLE:**
When you receive a band like "The Beatles", provide their essential contribution to pop/rock music, appropriate rating reflecting their massive influence, and most relevant similar artists."""


def _build_albums_analysis_template() -> str:
    """Build the albums-focused analysis template."""
    return """You are tasked with creating detailed album analysis for a music band's discography. Focus on individual album assessment and ratings.

**INSTRUCTIONS:**
When provided with a band name and their albums, create comprehensive album-by-album analysis with detailed reviews and ratings.

**ANALYSIS OBJECTIVES:**
1. Evaluate each album individually for musical merit
2. Provide detailed album reviews and accurate ratings
3. Consider each album within the band's discography context

**ALBUM ANALYSIS COMPONENTS:**
- Individual review for each album (minimum 40 words)
- Album rating (1-10 scale) based on musical quality
- Notable tracks, production quality, and innovations
- Position within band's evolution and discography

**RATING GUIDELINES FOR ALBUMS:**
- 1-2: Poor, weak songwriting or production
- 3-4: Below average, some good moments
- 5-6: Average, solid but unremarkable
- 7-8: Good to very good, strong collection
- 9-10: Excellent to masterpiece, essential listening

**ANALYSIS QUALITY GUIDELINES:**
1. **Individual Merit**: Rate each album on its own qualities
2. **Context**: Consider when it was released and band's trajectory  
3. **Completeness**: Cover songwriting, production, performance, innovation
4. **Specificity**: Mention standout tracks or notable elements

**OUTPUT FORMAT:**
Return the analysis in JSON format:

```json
{
  "albums": [
    {
      "album_name": "Album Title",
      "review": "Detailed album analysis covering style, standout tracks, production, and significance...",
      "rate": 9
    }
  ]
}
```

**ANALYSIS STRATEGY:**
1. Research each album's critical reception and significance
2. Consider the album's role in the band's development
3. Evaluate songwriting, production, and artistic cohesion
4. Rate based on lasting impact and musical quality

**USAGE EXAMPLE:**
When you receive albums like ["Sgt. Pepper's Lonely Hearts Club Band", "Revolver"] for The Beatles, provide detailed analysis of each album's innovation, standout tracks, and individual ratings reflecting their distinct contributions to music."""


def _build_specific_band_analysis_prompt(
    band_name: str, 
    albums: List[str], 
    analyze_missing_albums: bool,
    analysis_scope: str
) -> str:
    """Build an analysis prompt for a specific band."""
    albums_text = ""
    if albums:
        albums_list = "\n".join(f"- {album}" for album in albums)
        missing_note = ""
        if not analyze_missing_albums:
            missing_note = "\n\nNOTE: Only analyze albums that are available locally (not marked as missing)."
        elif analyze_missing_albums:
            missing_note = "\n\nNOTE: Include analysis for all albums, including those marked as missing."
            
        albums_text = f"""

**ALBUMS TO ANALYZE:**
{albums_list}{missing_note}

Focus your analysis on these specific albums when providing album-by-album reviews and ratings.
"""
    
    if analysis_scope == "basic":
        base_prompt = _build_basic_analysis_template()
    elif analysis_scope == "albums_only":
        base_prompt = _build_albums_analysis_template()
    else:  # full
        base_prompt = _build_full_analysis_template()
    
    # Replace the general instruction with specific band instruction
    specific_prompt = base_prompt.replace(
        "When provided with a band name",
        f"Analyze the band '{band_name}'"
    )
    
    # Add albums information if provided
    if albums_text:
        specific_prompt = specific_prompt.replace(
            "**ANALYSIS STRATEGY:**",
            f"{albums_text}\n\n**ANALYSIS STRATEGY:**"
        )
    
    return specific_prompt 