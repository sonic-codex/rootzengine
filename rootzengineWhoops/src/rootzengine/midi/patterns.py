"""Authentic reggae MIDI pattern library."""

import numpy as np
from typing import Dict, List, Tuple, Optional
from enum import Enum
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


class RiddimType(Enum):
    """Reggae riddim types."""
    ONE_DROP = "one_drop"
    STEPPERS = "steppers" 
    ROCKERS = "rockers"
    DIGITAL = "digital"
    RUBADUB = "rubadub"
    DANCEHALL = "dancehall"


@dataclass
class MIDINote:
    """MIDI note with timing and velocity."""
    note: int
    velocity: int
    start_beat: float
    duration: float
    channel: int = 9  # Drum channel by default


@dataclass
class MIDIPattern:
    """MIDI pattern for a specific instrument."""
    name: str
    notes: List[MIDINote]
    length_beats: float
    tempo_range: Tuple[int, int]
    description: str


class ReggaePatternLibrary:
    """Library of authentic reggae MIDI patterns."""
    
    def __init__(self):
        self.patterns = self._create_pattern_library()
        
    def _create_pattern_library(self) -> Dict[RiddimType, Dict[str, MIDIPattern]]:
        """Create the complete reggae pattern library."""
        return {
            RiddimType.ONE_DROP: self._create_one_drop_patterns(),
            RiddimType.STEPPERS: self._create_steppers_patterns(),
            RiddimType.ROCKERS: self._create_rockers_patterns(),
            RiddimType.DIGITAL: self._create_digital_patterns(),
            RiddimType.RUBADUB: self._create_rubadub_patterns(),
            RiddimType.DANCEHALL: self._create_dancehall_patterns(),
        }
    
    def _create_one_drop_patterns(self) -> Dict[str, MIDIPattern]:
        """Create One Drop riddim patterns - the classic reggae sound."""
        patterns = {}
        
        # One Drop Drums - Kick on beat 3, snare on 2 & 4
        patterns["drums"] = MIDIPattern(
            name="One Drop Drums",
            notes=[
                # Beat 1: Hi-hat only
                MIDINote(42, 60, 0.0, 0.25, 9),    # Closed hi-hat
                
                # Beat 2: Snare + hi-hat
                MIDINote(38, 100, 1.0, 0.25, 9),   # Snare
                MIDINote(42, 65, 1.0, 0.25, 9),    # Closed hi-hat
                
                # Beat 3: KICK + hi-hat (the "drop")
                MIDINote(36, 120, 2.0, 0.5, 9),    # Kick drum (strong)
                MIDINote(42, 70, 2.0, 0.25, 9),    # Closed hi-hat
                
                # Beat 4: Snare + hi-hat
                MIDINote(38, 95, 3.0, 0.25, 9),    # Snare
                MIDINote(42, 65, 3.0, 0.25, 9),    # Closed hi-hat
                
                # Off-beat hi-hats
                MIDINote(42, 45, 0.5, 0.25, 9),    # &1
                MIDINote(42, 50, 1.5, 0.25, 9),    # &2
                MIDINote(42, 50, 2.5, 0.25, 9),    # &3
                MIDINote(42, 45, 3.5, 0.25, 9),    # &4
            ],
            length_beats=4.0,
            tempo_range=(70, 90),
            description="Classic One Drop drum pattern with emphasis on beat 3"
        )
        
        # One Drop Bass - Walking pattern with root emphasis
        patterns["bass"] = MIDIPattern(
            name="One Drop Bass",
            notes=[
                # Beat 1: Root note (medium)
                MIDINote(40, 80, 0.0, 0.75, 1),    # E2
                
                # Beat 1.5: Walk up
                MIDINote(42, 60, 0.75, 0.25, 1),   # F#2
                
                # Beat 2: Fifth
                MIDINote(47, 85, 1.0, 0.5, 1),     # B2
                
                # Beat 2.5: Walk down  
                MIDINote(45, 65, 1.5, 0.25, 1),    # A2
                
                # Beat 3: ROOT (strong - matches kick)
                MIDINote(40, 110, 2.0, 1.0, 1),    # E2 (strong)
                
                # Beat 4: Third
                MIDINote(44, 75, 3.0, 0.75, 1),    # G#2
                
                # Beat 4.75: Walk back to root
                MIDINote(42, 60, 3.75, 0.25, 1),   # F#2
            ],
            length_beats=4.0,
            tempo_range=(70, 90),
            description="One Drop bass with walking notes and root emphasis on beat 3"
        )
        
        # One Drop Organ Skank - Off-beat chops
        patterns["organ"] = MIDIPattern(
            name="One Drop Organ Skank",
            notes=[
                # Skank on off-beats (2 & 4 primarily)
                # Beat 2 skank - stronger
                MIDINote(64, 85, 1.75, 0.125, 2),  # E4
                MIDINote(67, 85, 1.75, 0.125, 2),  # G4  
                MIDINote(71, 85, 1.75, 0.125, 2),  # B4
                
                # Beat 4 skank - stronger  
                MIDINote(64, 90, 3.75, 0.125, 2),  # E4
                MIDINote(67, 90, 3.75, 0.125, 2),  # G4
                MIDINote(71, 90, 3.75, 0.125, 2),  # B4
                
                # Subtle skanks on other off-beats
                MIDINote(64, 60, 0.75, 0.125, 2),  # &1
                MIDINote(67, 60, 0.75, 0.125, 2),
                
                MIDINote(64, 65, 2.75, 0.125, 2),  # &3
                MIDINote(67, 65, 2.75, 0.125, 2),
            ],
            length_beats=4.0,
            tempo_range=(70, 90),
            description="Classic organ skank emphasizing off-beats 2 & 4"
        )
        
        # One Drop Guitar - Sparse chord stabs
        patterns["guitar"] = MIDIPattern(
            name="One Drop Guitar",
            notes=[
                # Chord stabs on select beats
                # Beat 2.5 - upstroke chord
                MIDINote(52, 75, 1.5, 0.25, 3),   # E3
                MIDINote(56, 75, 1.5, 0.25, 3),   # G#3
                MIDINote(59, 75, 1.5, 0.25, 3),   # B3
                
                # Beat 4.5 - upstroke chord  
                MIDINote(52, 80, 3.5, 0.25, 3),   # E3
                MIDINote(56, 80, 3.5, 0.25, 3),   # G#3
                MIDINote(59, 80, 3.5, 0.25, 3),   # B3
            ],
            length_beats=4.0,
            tempo_range=(70, 90),
            description="Sparse guitar chord stabs on off-beats"
        )
        
        return patterns
    
    def _create_steppers_patterns(self) -> Dict[str, MIDIPattern]:
        """Create Steppers riddim patterns - four-on-the-floor variation."""
        patterns = {}
        
        # Steppers Drums - Kick on 1 & 3, snare on 2 & 4
        patterns["drums"] = MIDIPattern(
            name="Steppers Drums",
            notes=[
                # Beat 1: Kick + hi-hat
                MIDINote(36, 110, 0.0, 0.5, 9),    # Kick
                MIDINote(42, 70, 0.0, 0.25, 9),    # Hi-hat
                
                # Beat 2: Snare + hi-hat
                MIDINote(38, 100, 1.0, 0.25, 9),   # Snare
                MIDINote(42, 65, 1.0, 0.25, 9),    # Hi-hat
                
                # Beat 3: Kick + hi-hat
                MIDINote(36, 105, 2.0, 0.5, 9),    # Kick
                MIDINote(42, 70, 2.0, 0.25, 9),    # Hi-hat
                
                # Beat 4: Snare + hi-hat
                MIDINote(38, 95, 3.0, 0.25, 9),    # Snare
                MIDINote(42, 65, 3.0, 0.25, 9),    # Hi-hat
                
                # Off-beat hi-hats
                MIDINote(42, 50, 0.5, 0.25, 9),
                MIDINote(42, 55, 1.5, 0.25, 9),
                MIDINote(42, 55, 2.5, 0.25, 9),
                MIDINote(42, 50, 3.5, 0.25, 9),
            ],
            length_beats=4.0,
            tempo_range=(75, 95),
            description="Steppers drum pattern with kick on 1 & 3"
        )
        
        return patterns
    
    def _create_rockers_patterns(self) -> Dict[str, MIDIPattern]:
        """Create Rockers riddim patterns - syncopated kick pattern."""
        patterns = {}
        
        # Rockers Drums - Kick on 1 & 4+, snare on 3
        patterns["drums"] = MIDIPattern(
            name="Rockers Drums", 
            notes=[
                # Beat 1: Kick + hi-hat
                MIDINote(36, 115, 0.0, 0.5, 9),    # Kick
                MIDINote(42, 70, 0.0, 0.25, 9),    # Hi-hat
                
                # Beat 2: Hi-hat only
                MIDINote(42, 60, 1.0, 0.25, 9),    # Hi-hat
                
                # Beat 3: Snare + hi-hat
                MIDINote(38, 105, 2.0, 0.25, 9),   # Snare
                MIDINote(42, 65, 2.0, 0.25, 9),    # Hi-hat
                
                # Beat 4: Hi-hat
                MIDINote(42, 60, 3.0, 0.25, 9),    # Hi-hat
                
                # Beat 4.5: Syncopated kick (the "rocker")
                MIDINote(36, 100, 3.5, 0.25, 9),   # Kick
                
                # Off-beat hi-hats
                MIDINote(42, 45, 0.5, 0.25, 9),
                MIDINote(42, 50, 1.5, 0.25, 9),
                MIDINote(42, 50, 2.5, 0.25, 9),
            ],
            length_beats=4.0,
            tempo_range=(70, 85),
            description="Rockers pattern with syncopated kick on beat 4+"
        )
        
        return patterns
    
    def _create_digital_patterns(self) -> Dict[str, MIDIPattern]:
        """Create Digital riddim patterns - 80s electronic style."""
        patterns = {}
        
        # Digital Drums - Crisp, quantized
        patterns["drums"] = MIDIPattern(
            name="Digital Drums",
            notes=[
                # Beat 1: Kick + sharp hi-hat
                MIDINote(36, 120, 0.0, 0.25, 9),   # Sharp kick
                MIDINote(42, 80, 0.0, 0.125, 9),   # Crisp hi-hat
                
                # Beat 2: Snare + hi-hat
                MIDINote(38, 110, 1.0, 0.125, 9),  # Sharp snare
                MIDINote(42, 75, 1.0, 0.125, 9),   # Hi-hat
                
                # Beat 3: Kick + hi-hat  
                MIDINote(36, 115, 2.0, 0.25, 9),   # Kick
                MIDINote(42, 80, 2.0, 0.125, 9),   # Hi-hat
                
                # Beat 4: Snare + hi-hat
                MIDINote(38, 105, 3.0, 0.125, 9),  # Snare
                MIDINote(42, 75, 3.0, 0.125, 9),   # Hi-hat
                
                # 16th note hi-hats (digital precision)
                MIDINote(42, 55, 0.25, 0.125, 9),
                MIDINote(42, 60, 0.5, 0.125, 9),
                MIDINote(42, 55, 0.75, 0.125, 9),
                MIDINote(42, 60, 1.25, 0.125, 9),
                MIDINote(42, 55, 1.5, 0.125, 9),
                MIDINote(42, 55, 1.75, 0.125, 9),
            ],
            length_beats=4.0,
            tempo_range=(80, 100),
            description="Digital reggae with precise, electronic-style drums"
        )
        
        return patterns
    
    def _create_rubadub_patterns(self) -> Dict[str, MIDIPattern]:
        """Create Rub-a-Dub riddim patterns - early 80s style."""
        return {}  # Simplified for now
    
    def _create_dancehall_patterns(self) -> Dict[str, MIDIPattern]:
        """Create Dancehall riddim patterns - faster, more aggressive."""
        return {}  # Simplified for now
    
    def get_pattern(self, riddim_type: RiddimType, instrument: str) -> Optional[MIDIPattern]:
        """Get a specific pattern for a riddim type and instrument."""
        if riddim_type in self.patterns and instrument in self.patterns[riddim_type]:
            return self.patterns[riddim_type][instrument]
        return None
    
    def get_available_instruments(self, riddim_type: RiddimType) -> List[str]:
        """Get available instruments for a riddim type."""
        if riddim_type in self.patterns:
            return list(self.patterns[riddim_type].keys())
        return []
    
    def get_compatible_tempo(self, riddim_type: RiddimType) -> Tuple[int, int]:
        """Get the tempo range for a riddim type."""
        if riddim_type in self.patterns:
            # Get tempo range from first available pattern
            instruments = self.get_available_instruments(riddim_type)
            if instruments:
                pattern = self.get_pattern(riddim_type, instruments[0])
                if pattern:
                    return pattern.tempo_range
        
        # Default reggae tempo range
        return (70, 90)
    
    def generate_arrangement(
        self, 
        riddim_type: RiddimType, 
        instruments: List[str],
        measures: int = 4,
        variations: bool = True
    ) -> Dict[str, List[MIDINote]]:
        """
        Generate a full arrangement with multiple measures.
        
        Args:
            riddim_type: Type of reggae riddim
            instruments: List of instruments to include
            measures: Number of measures to generate
            variations: Whether to add subtle variations
            
        Returns:
            Dictionary mapping instrument names to lists of MIDI notes
        """
        arrangement = {}
        
        for instrument in instruments:
            pattern = self.get_pattern(riddim_type, instrument)
            if not pattern:
                logger.warning(f"Pattern not found for {riddim_type} {instrument}")
                continue
            
            notes = []
            pattern_length = pattern.length_beats
            
            for measure in range(measures):
                measure_offset = measure * pattern_length
                
                for note in pattern.notes:
                    # Copy note with measure offset
                    new_note = MIDINote(
                        note=note.note,
                        velocity=note.velocity,
                        start_beat=note.start_beat + measure_offset,
                        duration=note.duration,
                        channel=note.channel
                    )
                    
                    # Add subtle variations
                    if variations and measure > 0:
                        new_note.velocity = self._add_velocity_variation(new_note.velocity, measure)
                        
                        # Occasional note omissions for human feel
                        if instrument == "drums" and np.random.random() < 0.05:
                            continue  # Skip this note occasionally
                    
                    notes.append(new_note)
            
            arrangement[instrument] = notes
        
        return arrangement
    
    def _add_velocity_variation(self, base_velocity: int, measure: int) -> int:
        """Add subtle velocity variations for human feel."""
        # Add slight random variation
        variation = np.random.randint(-5, 6)
        
        # Add measure-based dynamics (builds energy)
        measure_boost = min(measure * 2, 10)
        
        # Ensure velocity stays in valid MIDI range
        new_velocity = base_velocity + variation + measure_boost
        return max(1, min(127, new_velocity))
    
    def get_riddim_info(self, riddim_type: RiddimType) -> Dict:
        """Get information about a specific riddim type."""
        info = {
            RiddimType.ONE_DROP: {
                "name": "One Drop",
                "description": "Classic reggae with kick on beat 3, creating the signature 'drop'",
                "era": "1970s-present",
                "characteristics": ["Sparse kick", "Off-beat emphasis", "Walking bass"],
                "famous_examples": ["No Woman No Cry", "Three Little Birds"]
            },
            RiddimType.STEPPERS: {
                "name": "Steppers", 
                "description": "Four-on-the-floor variation with kick on beats 1 & 3",
                "era": "1970s-1980s",
                "characteristics": ["Steady kick", "Driving rhythm", "Militant feel"],
                "famous_examples": ["Marcus Garvey", "War Ina Babylon"]
            },
            RiddimType.ROCKERS: {
                "name": "Rockers",
                "description": "Syncopated pattern with kick on 1 and 4+",
                "era": "Mid-1970s",
                "characteristics": ["Syncopated kick", "Rolling feel", "Hypnotic groove"],
                "famous_examples": ["Exodus", "Jamming"]
            },
            RiddimType.DIGITAL: {
                "name": "Digital",
                "description": "Electronic-influenced reggae with precise timing",
                "era": "1980s-1990s",
                "characteristics": ["Quantized timing", "Electronic sounds", "Sharp attacks"],
                "famous_examples": ["Under Mi Sleng Teng", "Bam Bam"]
            }
        }
        
        return info.get(riddim_type, {"name": "Unknown", "description": "Unknown riddim type"})
    

"""MIDI pattern analysis functionality"""

from typing import List, Dict, Any

class MidiPatternAnalyzer:
    """Analyzes MIDI files for musical patterns"""
    
    def __init__(self):
        self.pattern_library = {}
    
    def analyze_patterns(self, midi_file_path: str) -> List[Dict[str, Any]]:
        """
        Analyze MIDI file for musical patterns.
        
        Args:
            midi_file_path: Path to MIDI file
            
        Returns:
            List of detected patterns
        """
        # TODO: Implement MIDI pattern analysis
        return []
    
    def extract_chord_progressions(self, midi_file_path: str) -> List[str]:
        """Extract chord progressions from MIDI file"""
        # TODO: Implement chord progression extraction
        return []