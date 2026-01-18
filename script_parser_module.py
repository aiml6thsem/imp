"""
Advanced Script Parser with Character Detection and Voice Assignment
"""

import re
from typing import List, Tuple, Dict, Optional
from collections import Counter
import logging

logger = logging.getLogger(__name__)


class ScriptParser:
    """
    Intelligent script parser that detects dialogue and assigns voices
    """
    
    def __init__(self):
        # Default voice assignments
        self.default_voices = {
            "NARRATOR": "af_heart",
            "MALE": "am_adam",
            "FEMALE": "af_bella",
            "DEFAULT": "af_heart"
        }
        
        # Character gender hints for smart voice assignment
        self.male_names = {
            'john', 'mike', 'david', 'james', 'robert', 'michael', 'william',
            'joseph', 'thomas', 'charles', 'daniel', 'paul', 'mark', 'george',
            'peter', 'alex', 'adam', 'steve', 'jack', 'tom', 'bob', 'henry',
            'knox', 'bernard', 'mclain', 'sims'
        }
        
        self.female_names = {
            'sarah', 'mary', 'jennifer', 'linda', 'patricia', 'barbara',
            'elizabeth', 'susan', 'jessica', 'karen', 'nancy', 'lisa',
            'betty', 'margaret', 'sandra', 'ashley', 'emily', 'donna',
            'bella', 'emma', 'sophia', 'isabella', 'shirley'
        }
        
        # Available Kokoro voices
        self.available_voices = {
            'male': ['am_adam', 'am_michael'],
            'female': ['af_bella', 'af_sarah', 'af_heart', 'af_sky', 'af_nicole'],
            'neutral': ['af_heart']
        }
        
        # Blacklist for scene directions
        self.scene_keywords = {
            'INT', 'EXT', 'FADE IN', 'FADE OUT', 'CUT TO', 'DISSOLVE TO',
            'CONTINUED', 'SCENE', 'LOCATION', 'NIGHT', 'DAY', 'MORNING',
            'EVENING', 'LATER', 'MEANWHILE', 'FLASHBACK', 'MONTAGE'
        }
    
    def parse_script(
        self,
        script_text: str,
        voice_mappings: Optional[Dict[str, str]] = None
    ) -> List[Tuple[str, str]]:
        """
        Parse script and return list of (voice, text) tuples
        
        Args:
            script_text: The script content
            voice_mappings: Optional custom voice mappings
            
        Returns:
            List of (voice_id, dialogue_text) tuples
        """
        if voice_mappings is None:
            voice_mappings = {}
        
        segments = []
        
        # Split by lines
        lines = script_text.split('\n')
        
        current_speaker = None
        current_text = []
        
        for line in lines:
            line = line.strip()
            
            if not line:
                continue
            
            # Try to detect speaker
            speaker_match = self._detect_speaker(line)
            
            if speaker_match:
                # Save previous segment
                if current_speaker and current_text:
                    text = ' '.join(current_text)
                    voice = self._get_voice_for_speaker(
                        current_speaker,
                        voice_mappings
                    )
                    segments.append((voice, text))
                    current_text = []
                
                current_speaker = speaker_match['speaker']
                dialogue = speaker_match['dialogue']
                
                if dialogue:
                    current_text.append(dialogue)
            else:
                # Continuation of previous dialogue
                if current_speaker:
                    current_text.append(line)
                else:
                    # No speaker detected, treat as narrator
                    if not self._is_scene_direction(line):
                        current_speaker = "NARRATOR"
                        current_text.append(line)
        
        # Add final segment
        if current_speaker and current_text:
            text = ' '.join(current_text)
            voice = self._get_voice_for_speaker(current_speaker, voice_mappings)
            segments.append((voice, text))
        
        logger.info(f"Parsed {len(segments)} dialogue segments")
        
        return segments
    
    def _detect_speaker(self, line: str) -> Optional[Dict[str, str]]:
        """
        Detect if line contains a speaker name
        
        Returns dict with 'speaker' and 'dialogue' keys, or None
        """
        # Pattern 1: "CHARACTER: dialogue"
        match = re.match(r'^([A-Z][A-Z\s\'\-\.]+?):\s*(.+)$', line)
        if match:
            speaker = match.group(1).strip()
            dialogue = match.group(2).strip()
            
            # Filter out scene directions
            if speaker.upper() not in self.scene_keywords:
                return {'speaker': speaker, 'dialogue': dialogue}
        
        # Pattern 2: "[CHARACTER] dialogue" or "(CHARACTER) dialogue"
        match = re.match(r'^[\[\(]([A-Z][A-Z\s\'\-\.]+?)[\]\)]\s*(.+)$', line)
        if match:
            speaker = match.group(1).strip()
            dialogue = match.group(2).strip()
            return {'speaker': speaker, 'dialogue': dialogue}
        
        # Pattern 3: "CHARACTER" on its own line (screenplay format)
        match = re.match(r'^([A-Z][A-Z\s\'\-\.]{2,})$', line)
        if match:
            speaker = match.group(1).strip()
            if speaker.upper() not in self.scene_keywords:
                return {'speaker': speaker, 'dialogue': ''}
        
        # Pattern 4: "**CHARACTER** dialogue" (markdown bold)
        match = re.match(r'^\*\*([A-Z][A-Z\s\'\-\.]+?)\*\*\s*(.+)$', line)
        if match:
            speaker = match.group(1).strip()
            dialogue = match.group(2).strip()
            return {'speaker': speaker, 'dialogue': dialogue}
        
        return None
    
    def _get_voice_for_speaker(
        self,
        speaker: str,
        voice_mappings: Dict[str, str]
    ) -> str:
        """
        Get appropriate voice for a speaker
        """
        # Check custom mappings first
        speaker_upper = speaker.upper()
        
        if speaker_upper in voice_mappings:
            return voice_mappings[speaker_upper]
        
        # Check if name exists in mappings (case insensitive)
        for key, voice in voice_mappings.items():
            if key.upper() == speaker_upper:
                return voice
        
        # Auto-detect based on name
        speaker_lower = speaker.lower().split()[0]  # First word only
        
        if speaker_lower in self.male_names:
            return self.available_voices['male'][0]  # am_adam
        
        if speaker_lower in self.female_names:
            return self.available_voices['female'][0]  # af_bella
        
        # Check for narrator keywords
        if 'narr' in speaker_lower or speaker_upper == 'NARRATOR':
            return self.default_voices['NARRATOR']
        
        # Default to neutral voice
        return self.default_voices['DEFAULT']
    
    def _is_scene_direction(self, line: str) -> bool:
        """
        Check if line is a scene direction/action line
        """
        line_upper = line.upper()
        
        # Check if starts with scene keywords
        for keyword in self.scene_keywords:
            if line_upper.startswith(keyword):
                return True
        
        # Check if it's an action line (parenthetical)
        if re.match(r'^\(.+\)$', line):
            return True
        
        return False
    
    def detect_characters(self, script_text: str) -> Dict[str, int]:
        """
        Detect all characters and count their lines
        """
        character_counts = Counter()
        
        lines = script_text.split('\n')
        
        for line in lines:
            speaker_match = self._detect_speaker(line)
            if speaker_match:
                speaker = speaker_match['speaker'].upper()
                if speaker not in self.scene_keywords:
                    character_counts[speaker] += 1
        
        return dict(character_counts)
    
    def suggest_voice_mappings(self, script_text: str) -> Dict[str, str]:
        """
        Analyze script and suggest voice mappings
        """
        characters = self.detect_characters(script_text)
        suggestions = {}
        
        male_voice_idx = 0
        female_voice_idx = 0
        
        for character in characters.keys():
            char_lower = character.lower().split()[0]
            
            if 'narr' in char_lower:
                suggestions[character] = 'af_heart'
            elif char_lower in self.male_names:
                voices = self.available_voices['male']
                suggestions[character] = voices[male_voice_idx % len(voices)]
                male_voice_idx += 1
            elif char_lower in self.female_names:
                voices = self.available_voices['female']
                suggestions[character] = voices[female_voice_idx % len(voices)]
                female_voice_idx += 1
            else:
                # Default to alternating
                if len(suggestions) % 2 == 0:
                    suggestions[character] = 'am_adam'
                else:
                    suggestions[character] = 'af_bella'
        
        logger.info(f"Suggested voices for {len(suggestions)} characters")
        
        return suggestions
