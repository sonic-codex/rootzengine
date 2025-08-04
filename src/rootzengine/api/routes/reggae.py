"""API routes for reggae pattern detection and analysis."""

from typing import Optional
from fastapi import APIRouter, Form, status
from fastapi.responses import JSONResponse

from rootzengine.audio.reggae_patterns import reggae_detector, ReggaeStyle

router = APIRouter()


@router.get("/styles")
async def get_all_styles() -> JSONResponse:
    """Get information about all available reggae styles."""
    try:
        styles = reggae_detector.get_all_styles()
        
        return JSONResponse(
            content={
                "styles": styles,
                "count": len(styles)
            },
            status_code=status.HTTP_200_OK,
        )
        
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.post("/detect")
async def detect_pattern(
    tempo: float = Form(...),
    audio_path: Optional[str] = Form(None)
) -> JSONResponse:
    """Detect reggae pattern based on tempo."""
    try:
        if tempo <= 0 or tempo > 300:
            return JSONResponse(
                content={"error": "Tempo must be between 0 and 300 BPM"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        
        # Detect pattern
        result = reggae_detector.detect_pattern_mock(tempo, audio_path)
        
        return JSONResponse(
            content=result,
            status_code=status.HTTP_200_OK,
        )
        
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.get("/styles/{style_name}")
async def get_style_info(style_name: str) -> JSONResponse:
    """Get detailed information about a specific reggae style."""
    try:
        # Validate style name
        try:
            style_enum = ReggaeStyle(style_name.lower())
        except ValueError:
            return JSONResponse(
                content={"error": f"Unknown reggae style: {style_name}"},
                status_code=status.HTTP_404_NOT_FOUND,
            )
        
        # Get pattern info
        pattern = reggae_detector.get_pattern_info(style_enum)
        
        if not pattern:
            return JSONResponse(
                content={"error": f"No pattern data for style: {style_name}"},
                status_code=status.HTTP_404_NOT_FOUND,
            )
        
        # Convert to serializable format
        pattern_info = {
            "name": pattern.name,
            "style": pattern.style.value,
            "tempo_range": pattern.tempo_range,
            "emphasis_pattern": pattern.emphasis_pattern,
            "rhythm_patterns": {
                "kick": pattern.kick_pattern,
                "snare": pattern.snare_pattern,
                "hi_hat": pattern.hi_hat_pattern,
                "skank": pattern.skank_pattern,
                "bass": pattern.bass_pattern
            },
            "confidence_factors": pattern.confidence_factors,
            "description": reggae_detector._get_style_description(style_enum)
        }
        
        return JSONResponse(
            content=pattern_info,
            status_code=status.HTTP_200_OK,
        )
        
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.post("/analyze-characteristics")
async def analyze_characteristics(
    tempo: float = Form(...),
    style: str = Form(...)
) -> JSONResponse:
    """Analyze rhythm characteristics for a detected style."""
    try:
        if tempo <= 0 or tempo > 300:
            return JSONResponse(
                content={"error": "Tempo must be between 0 and 300 BPM"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        
        # Validate style
        try:
            ReggaeStyle(style.lower())
        except ValueError:
            return JSONResponse(
                content={"error": f"Unknown reggae style: {style}"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        
        # Analyze characteristics
        characteristics = reggae_detector.analyze_rhythm_characteristics(tempo, style.lower())
        
        if "error" in characteristics:
            return JSONResponse(
                content=characteristics,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        
        return JSONResponse(
            content=characteristics,
            status_code=status.HTTP_200_OK,
        )
        
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.get("/tempo-to-style/{tempo}")
async def tempo_to_style(tempo: float) -> JSONResponse:
    """Get the most likely reggae style for a given tempo."""
    try:
        if tempo <= 0 or tempo > 300:
            return JSONResponse(
                content={"error": "Tempo must be between 0 and 300 BPM"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        
        # Get style suggestions based on tempo
        style_matches = []
        
        for style_enum, pattern in reggae_detector.patterns.items():
            tempo_min, tempo_max = pattern.tempo_range
            
            if tempo_min <= tempo <= tempo_max:
                match_strength = "perfect"
                score = 1.0
            else:
                # Calculate how close we are
                distance = min(abs(tempo - tempo_min), abs(tempo - tempo_max))
                if distance <= 20:
                    match_strength = "good"
                    score = 1.0 - (distance / 20.0)
                elif distance <= 40:
                    match_strength = "possible"
                    score = 1.0 - (distance / 40.0)
                else:
                    continue  # Too far away
            
            style_matches.append({
                "style": style_enum.value,
                "name": pattern.name,
                "tempo_range": pattern.tempo_range,
                "match_strength": match_strength,
                "score": score,
                "description": reggae_detector._get_style_description(style_enum)
            })
        
        # Sort by score
        style_matches.sort(key=lambda x: x["score"], reverse=True)
        
        return JSONResponse(
            content={
                "tempo": tempo,
                "matches": style_matches,
                "best_match": style_matches[0] if style_matches else None
            },
            status_code=status.HTTP_200_OK,
        )
        
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )