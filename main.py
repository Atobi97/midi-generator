import os
import time
from mido import Message, MidiFile, MidiTrack, bpm2tempo, MetaMessage
import random
import pygame
import numpy as np


class MelodyGenerator:
    SCALE_MODES = {
        "major": [0, 2, 4, 5, 7, 9, 11],
        "minor": [0, 2, 3, 5, 7, 8, 10],
        "dorian": [0, 2, 3, 5, 7, 9, 10],
        "phrygian": [0, 1, 3, 5, 7, 8, 10],
        "mixolydian": [0, 2, 4, 5, 7, 9, 10],
        "blues": [0, 3, 5, 6, 7, 10]
    }

    NOTE_TO_MIDI = {
        "C": 60, "C#": 61, "D": 62, "D#": 63,
        "E": 64, "F": 65, "F#": 66, "G": 67,
        "G#": 68, "A": 69, "A#": 70, "B": 71
    }

    RHYTHM_PATTERNS = {
        "basic": [(1, 1)] * 4,  # Quarter notes
        "upbeat": [(0.5, 0.5), (0.5, 0.5), (1, 1), (1, 1)],  # Eighth notes + quarters
        "waltz": [(1, 1), (0.5, 0.5), (0.5, 0.5)],  # 3/4 time
        "syncopated": [(1.5, 1.5), (0.5, 0.5), (1, 1)],  # Syncopated rhythm
        "swing_eighth": [(0.5, 1), (0.5, 0.8)] * 2,  # Swing eighth notes
        "swing_sixteenth": [(0.25, 1), (0.25, 0.8)] * 4,  # Swing sixteenth notes
        "experimental": [(0.25, 1), (0.25, 0.7), (0.5, 0.9), (0.25, 1)],
        "chaos": [(random.random(), random.random()) for _ in range(4)]
    }

    SWING_AMOUNTS = {
        "light": 0.55,    # 55% swing
        "medium": 0.60,   # 60% swing
        "heavy": 0.67,    # 67% swing (2:1 ratio)
        "extreme": 0.75   # 75% swing
    }

    CHORD_PROGRESSIONS = {
        "basic": [0, 5, 3, 4],          # I-vi-IV-V
        "jazz": [1, 4, 0, 5],           # ii-V-I-vi
        "blues": [0, 0, 0, 0, 4, 4, 0, 0, 5, 4, 0, 5],  # 12-bar blues
        "pop": [0, 3, 5, 4],            # I-IV-vi-V
        "jazz_2_5_1": [1, 4, 0],        # ii-V-I
        "andalusian": [5, 4, 3, 2],     # vi-V-IV-III
        "pachelbel": [0, 5, 3, 4, 0, 5, 3, 4],  # Pachelbel's Canon
        "50s": [0, 5, 1, 4],            # I-vi-ii-V
        "minor_epic": [5, 3, 4, 0],     # vi-IV-V-I
        "sad": [0, 5, 3, 4],            # i-vi-iv-v (minor)
        "royal_road": [0, 5, 1, 4, 0, 5, 3, 4],  # I-vi-ii-V-I-vi-IV-V
        "emotional": [0, 3, 5, 4, 0, 3, 5, 2],   # I-IV-vi-V-I-IV-vi-III
        "experimental": [0, 2, 5, 6, 1, 4, 3]    # I-III-vi-vii-ii-V-IV
    }

    STRUM_PATTERNS = {
        "none": {"direction": "none", "speed": 0},
        "down_slow": {"direction": "down", "speed": 20},
        "down_med": {"direction": "down", "speed": 10},
        "down_fast": {"direction": "down", "speed": 5},
        "up_slow": {"direction": "up", "speed": 20},
        "up_med": {"direction": "up", "speed": 10},
        "up_fast": {"direction": "up", "speed": 5},
        "alt_slow": {"direction": "alt", "speed": 20},  # Alternating up/down
        "alt_med": {"direction": "alt", "speed": 10},
        "alt_fast": {"direction": "alt", "speed": 5}
    }

    def __init__(self):
        pygame.init()
        pygame.mixer.init()

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def show_menu(self):
        while True:
            self.clear_screen()
            print("🎵 Python Melody Generator 🎵")
            print("\n1. Generate new melody")
            print("2. Generate experimental melody")
            print("3. Generate arpeggio pattern")
            print("4. Generate chord progression")
            print("5. List available scales/modes")
            print("6. List rhythm patterns")
            print("7. Exit")

            choice = input("\nEnter your choice (1-7): ")

            if choice == "1":
                self.generate_melody()
            elif choice == "2":
                self.generate_experimental_melody()
            elif choice == "3":
                self.generate_arpeggio()
            elif choice == "4":
                self.generate_chord_progression()
            elif choice == "5":
                self.show_scales()
            elif choice == "6":
                self.show_rhythms()
            elif choice == "7":
                print("\nGoodbye! 🎶")
                break
            else:
                input("Invalid choice. Press Enter to continue...")

    def show_scales(self):
        self.clear_screen()
        print("Available Scales/Modes:")
        for mode in self.SCALE_MODES:
            print(f"- {mode}")
        input("\nPress Enter to continue...")

    def show_rhythms(self):
        self.clear_screen()
        print("Available Rhythm Patterns:")
        for pattern in self.RHYTHM_PATTERNS:
            print(f"- {pattern}")
        input("\nPress Enter to continue...")

    def get_valid_input(self, prompt, valid_options=None, value_type=str):
        while True:
            try:
                value = value_type(input(prompt))
                if valid_options is None or value in valid_options:
                    return value
                print(f"Please enter one of: {', '.join(map(str, valid_options))}")
            except ValueError:
                print(f"Please enter a valid {value_type.__name__}")

    def apply_microshift(self, time_value, intensity=0.2):
        """Apply subtle timing variations to make melody feel more human"""
        # Use normal distribution for natural variation
        shift = np.random.normal(0, intensity * time_value)
        return max(0, int(time_value + shift))

    def apply_swing(self, ticks, is_offbeat, swing_amount):
        """Apply swing feel to note timing"""
        if is_offbeat:  # Delay every other note
            return int(ticks * (1 + swing_amount))
        return ticks

    def get_strum_speed(self, pattern_name):
        """Get strum speed from pattern name"""
        if pattern_name == "none":
            return 0
        if "alt_" in pattern_name:
            # For alternating patterns, use the first speed (down stroke speed)
            _, down_speed, _ = pattern_name.split("_")
            return self.STRUM_PATTERNS[f"down_{down_speed}"]["speed"]
        return self.STRUM_PATTERNS[pattern_name]["speed"]

    def apply_strum(self, notes, velocities, strum_pattern, is_note_on=True, base_time=0):
        """Apply strumming pattern to a chord"""
        if strum_pattern == "none":
            # All notes start together with the base_time
            return [(note, vel, base_time if idx == 0 else 0) 
                   for idx, (note, vel) in enumerate(zip(notes, velocities))]
        
        # Create a copy of notes and velocities to avoid modifying originals
        notes = list(notes)
        velocities = list(velocities)
        
        # For alternating patterns, extract speeds from pattern name
        if "alt_" in strum_pattern:
            _, down_speed, up_speed = strum_pattern.split("_")
            if is_note_on:
                speed = self.STRUM_PATTERNS[f"down_{down_speed}"]["speed"]
                direction = "down"
            else:
                speed = self.STRUM_PATTERNS[f"up_{up_speed}"]["speed"]
                direction = "up"
        else:
            direction = self.STRUM_PATTERNS[strum_pattern]["direction"]
            speed = self.STRUM_PATTERNS[strum_pattern]["speed"]
        
        # Determine note order based on strum direction
        if direction == "up":
            notes.reverse()
            velocities.reverse()
        
        # Calculate timing for each note in the strum
        result = []
        for idx, (note, vel) in enumerate(zip(notes, velocities)):
            if idx == 0:
                # First note gets the base timing
                time = base_time
            else:
                # Subsequent notes are spaced by the speed
                time = speed
            result.append((note, vel, time))
        
        return result

    def get_strum_pattern(self, prompt):
        """Get strum pattern using numbered menu"""
        print("\nStrum Patterns:")
        print("0. None (all notes together)")
        print("\nDownward Strums:")
        print("1. Down - Slow")
        print("2. Down - Medium")
        print("3. Down - Fast")
        print("\nUpward Strums:")
        print("4. Up - Slow")
        print("5. Up - Medium")
        print("6. Up - Fast")
        print("\nAlternating Strums:")
        print("7. Alternating")

        # Map numbers to pattern names
        pattern_map = {
            0: "none",
            1: "down_slow",
            2: "down_med",
            3: "down_fast",
            4: "up_slow",
            5: "up_med",
            6: "up_fast",
            7: "alternating"
        }

        while True:
            try:
                choice = int(input(f"\n{prompt} (0-7): "))
                if choice in pattern_map:
                    if choice == 7:  # Alternating pattern selected
                        # Get down strum speed
                        print("\nSelect Down Strum Speed:")
                        print("1. Slow")
                        print("2. Medium")
                        print("3. Fast")
                        down_speed = int(input("Choose down strum speed (1-3): "))
                        if down_speed not in [1, 2, 3]:
                            print("Invalid speed selection")
                            continue

                        # Get up strum speed
                        print("\nSelect Up Strum Speed:")
                        print("1. Slow")
                        print("2. Medium")
                        print("3. Fast")
                        up_speed = int(input("Choose up strum speed (1-3): "))
                        if up_speed not in [1, 2, 3]:
                            print("Invalid speed selection")
                            continue

                        # Map speeds to pattern names
                        speed_map = {1: "slow", 2: "med", 3: "fast"}
                        return f"alt_{speed_map[down_speed]}_{speed_map[up_speed]}"
                    
                    return pattern_map[choice]
                print("Please enter a number between 0 and 7")
            except ValueError:
                print("Please enter a valid number")

    def generate_melody(self, microshift_intensity=0.0):
        self.clear_screen()
        print("🎼 Melody Generation Settings 🎼\n")

        # Get user inputs with validation
        root_note = self.get_valid_input("Enter root note (C, C#, D, D#, etc.): ", self.NOTE_TO_MIDI.keys()).upper()
        mode = self.get_valid_input("Enter scale mode: ", self.SCALE_MODES.keys()).lower()
        rhythm_pattern = self.get_valid_input("Enter rhythm pattern: ", self.RHYTHM_PATTERNS.keys()).lower()
        bpm = self.get_valid_input("Enter tempo in BPM (60-180): ", range(60, 181), int)
        bars = self.get_valid_input("Enter number of bars (1-8): ", range(1, 9), int)
        
        # Swing options
        use_swing = self.get_valid_input("Add swing feel (y/n)? ", ["y", "n"]) == "y"
        swing_amount = 0
        if use_swing:
            swing_type = self.get_valid_input("Enter swing amount (light/medium/heavy/extreme): ", self.SWING_AMOUNTS.keys())
            swing_amount = self.SWING_AMOUNTS[swing_type]

        # Microshift options
        use_microshift = self.get_valid_input("Add humanization (y/n)? ", ["y", "n"]) == "y"
        if use_microshift:
            microshift_intensity = self.get_valid_input("Enter humanization amount (0.1-0.5): ", None, float)
            microshift_intensity = max(0.1, min(0.5, microshift_intensity))

        # Create MIDI file
        mid = MidiFile()
        track = MidiTrack()
        mid.tracks.append(track)

        # Setup track
        track.append(Message('program_change', program=0, time=0))
        track.append(Message('control_change', control=7, value=100, time=0))
        track.append(Message('control_change', control=10, value=64, time=0))

        # Calculate scale notes
        root_midi = self.NOTE_TO_MIDI[root_note]
        scale_intervals = self.SCALE_MODES[mode]
        scale_notes = [root_midi + interval for interval in scale_intervals]
        scale_notes.extend([note + 12 for note in scale_notes])

        # Generate melody
        ticks_per_beat = mid.ticks_per_beat
        pattern = self.RHYTHM_PATTERNS[rhythm_pattern]

        for bar in range(bars):
            for i, (duration, velocity) in enumerate(pattern):
                note = random.choice(scale_notes)
                ticks = int(ticks_per_beat * duration)
                velocity_val = int(velocity * 64)

                # Apply swing if enabled
                if use_swing:
                    ticks = self.apply_swing(ticks, i % 2 == 1, swing_amount)

                # Apply microshift if enabled
                if use_microshift:
                    ticks = self.apply_microshift(ticks, microshift_intensity)
                    velocity_val = self.apply_microshift(velocity_val, microshift_intensity/2)

                track.append(Message('note_on', note=note, velocity=velocity_val, time=0))
                track.append(Message('note_off', note=note, velocity=velocity_val, time=ticks))

        # Save MIDI file
        modifiers = []
        if use_swing:
            modifiers.append(f"swing_{swing_type}")
        if use_microshift:
            modifiers.append("humanized")
        
        modifier_str = "_" + "_".join(modifiers) if modifiers else ""
        filename = f"{root_note}_{mode}_{bpm}bpm{modifier_str}.mid"
        mid.save(filename)
        print(f"\n✨ Melody generated and saved as: {filename}")
        input("\nPress Enter to return to menu...")

    def generate_arpeggio(self):
        self.clear_screen()
        print("🎼 Arpeggio Generation Settings 🎼\n")

        root_note = self.get_valid_input("Enter root note (C, C#, D, D#, etc.): ", self.NOTE_TO_MIDI.keys()).upper()
        mode = self.get_valid_input("Enter scale mode: ", self.SCALE_MODES.keys()).lower()
        bpm = self.get_valid_input("Enter tempo in BPM (60-180): ", range(60, 181), int)
        pattern = self.get_valid_input("Enter pattern (up/down/random): ", ["up", "down", "random"])

        mid = MidiFile()
        track = MidiTrack()
        mid.tracks.append(track)
        track.append(Message('program_change', program=0, time=0))

        root_midi = self.NOTE_TO_MIDI[root_note]
        scale_intervals = self.SCALE_MODES[mode]
        scale_notes = [root_midi + interval for interval in scale_intervals]
        
        # Create arpeggio pattern
        if pattern == "up":
            notes = scale_notes + list(reversed(scale_notes[1:-1]))
        elif pattern == "down":
            notes = list(reversed(scale_notes)) + scale_notes[1:-1]
        else:
            notes = [random.choice(scale_notes) for _ in range(16)]

        # Generate arpeggio
        for note in notes:
            velocity = random.randint(64, 100)
            track.append(Message('note_on', note=note, velocity=velocity, time=0))
            track.append(Message('note_off', note=note, velocity=velocity, time=mid.ticks_per_beat // 2))

        filename = f"{root_note}_{mode}_arpeggio.mid"
        mid.save(filename)
        print(f"\n✨ Arpeggio generated and saved as: {filename}")
        input("\nPress Enter to return to menu...")

    def generate_experimental_melody(self):
        self.clear_screen()
        print("🎼 Experimental Melody Settings 🎼\n")

        root_note = self.get_valid_input("Enter root note (C, C#, D, D#, etc.): ", self.NOTE_TO_MIDI.keys()).upper()
        mode = self.get_valid_input("Enter scale mode: ", self.SCALE_MODES.keys()).lower()
        bpm = self.get_valid_input("Enter tempo in BPM (60-180): ", range(60, 181), int)
        complexity = self.get_valid_input("Enter complexity (1-10): ", range(1, 11), int)
        use_microshift = self.get_valid_input("Add humanization (y/n)? ", ["y", "n"]) == "y"
        
        if use_microshift:
            microshift_intensity = self.get_valid_input("Enter humanization amount (0.1-0.5): ", None, float)
            microshift_intensity = max(0.1, min(0.5, microshift_intensity))
        else:
            microshift_intensity = 0.0

        mid = MidiFile()
        track = MidiTrack()
        mid.tracks.append(track)
        track.append(Message('program_change', program=0, time=0))

        root_midi = self.NOTE_TO_MIDI[root_note]
        scale_intervals = self.SCALE_MODES[mode]
        scale_notes = [root_midi + interval for interval in scale_intervals]
        scale_notes.extend([note + 12 for note in scale_notes])

        for _ in range(16):
            duration = random.randint(1, complexity) * mid.ticks_per_beat // 4
            velocity = random.randint(30 + complexity * 5, 100)
            
            # Apply microshift if enabled
            if use_microshift:
                duration = self.apply_microshift(duration, microshift_intensity)
                velocity = self.apply_microshift(velocity, microshift_intensity/2)
            
            if random.random() < complexity / 20:
                notes = random.sample(scale_notes, min(3, complexity // 3))
                for note in notes:
                    track.append(Message('note_on', note=note, velocity=velocity, time=0))
                track.append(Message('note_off', note=notes[-1], velocity=velocity, time=duration))
            else:
                note = random.choice(scale_notes)
                track.append(Message('note_on', note=note, velocity=velocity, time=0))
                track.append(Message('note_off', note=note, velocity=velocity, time=duration))

        humanized = "_humanized" if use_microshift else ""
        filename = f"{root_note}_{mode}_experimental_{complexity}{humanized}.mid"
        mid.save(filename)
        print(f"\n✨ Experimental melody generated and saved as: {filename}")
        input("\nPress Enter to return to menu...")

    def get_chord_progression(self):
        """Get chord progression from user input"""
        print("\nChord Progression Type:")
        print("1. Use preset progression")
        print("2. Enter custom progression")
        print("3. Generate random progression")
        
        choice = self.get_valid_input("Select progression type (1-3): ", range(1, 4), int)
        
        if choice == 1:
            # Show available preset progressions
            print("\nAvailable Progressions:")
            for i, (name, prog) in enumerate(self.CHORD_PROGRESSIONS.items(), 1):
                # Convert progression to roman numerals for display
                numerals = [self.to_roman(n + 1) for n in prog]
                print(f"{i}. {name}: {'-'.join(numerals)}")
            
            prog_choice = self.get_valid_input(f"Select progression (1-{len(self.CHORD_PROGRESSIONS)}): ", 
                                             range(1, len(self.CHORD_PROGRESSIONS) + 1), int)
            progression_name = list(self.CHORD_PROGRESSIONS.keys())[prog_choice - 1]
            return progression_name, self.CHORD_PROGRESSIONS[progression_name]
        
        elif choice == 2:
            # Get custom progression
            print("\nEnter chord numbers (1-7) separated by hyphens")
            print("Example: 2-5-1-6 or 1-4-5-1")
            while True:
                try:
                    progression_input = input("Enter progression: ")
                    # Convert input string to list of integers (0-based)
                    progression = [int(n) - 1 for n in progression_input.split('-')]
                    # Validate each number is in range
                    if all(0 <= n <= 6 for n in progression):
                        return "custom", progression
                    print("Please use numbers between 1 and 7")
                except ValueError:
                    print("Invalid format. Use numbers separated by hyphens (e.g., 2-5-1-6)")
        
        else:  # Random progression
            length = self.get_valid_input("Enter number of chords (2-16): ", range(2, 17), int)
            progression = [random.randint(0, 6) for _ in range(length)]
            return "random", progression

    def to_roman(self, num):
        """Convert number to roman numeral"""
        roman_symbols = ['i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii']
        return roman_symbols[num - 1].upper()

    def generate_chord_progression(self):
        self.clear_screen()
        print("🎼 Chord Progression Settings 🎼\n")

        root_note = self.get_valid_input("Enter root note (C, C#, D, D#, etc.): ", self.NOTE_TO_MIDI.keys()).upper()
        
        # Get progression using new method
        progression_type, progression = self.get_chord_progression()
        
        # Show the progression in roman numerals
        progression_display = '-'.join(self.to_roman(n + 1) for n in progression)
        print(f"\nSelected progression: {progression_display}")
        print(f"Length: {len(progression)} bars")
        
        # Get desired total bars
        total_bars = self.get_valid_input("Enter total number of bars (1-32): ", range(1, 33), int)
        
        # Calculate repetitions needed
        repetitions = max(1, total_bars // len(progression))
        remaining_bars = total_bars % len(progression)
        
        bpm = self.get_valid_input("Enter tempo in BPM (60-180): ", range(60, 181), int)
        
        # Add octave selection
        print("\nOctave Selection:")
        print("1. Low (2)")
        print("2. Medium (3)")
        print("3. High (4)")
        print("4. Very High (5)")
        octave_choice = self.get_valid_input("Select octave (1-4): ", range(1, 5), int)
        octave_offset = (octave_choice + 1) * 12  # Map to actual octave numbers
        
        # Add timing mode selection
        print("\nTiming Mode:")
        print("1. Regular - Each chord starts on the beat")
        print("2. Tight - Chords are precisely connected")
        timing_mode = self.get_valid_input("Select timing mode (1-2): ", [1, 2], int)
        
        # Extended chord options
        print("\nChord Types:")
        print("1. Triads")
        print("2. Seventh Chords")
        print("3. Ninth Chords")
        print("4. Eleventh Chords")
        print("5. Thirteenth Chords")
        chord_choice = self.get_valid_input("Select chord type (1-5): ", range(1, 6), int)
        
        # Inversion options
        print("\nInversion Types:")
        print("0. Root Position")
        print("1. First Inversion")
        print("2. Second Inversion")
        print("3. Third Inversion (for 7th chords and up)")
        print("4. Random Inversions")
        inversion = self.get_valid_input("Select inversion type (0-4): ", range(0, 5), int)
        
        # Strum pattern selection
        strum_in = self.get_strum_pattern("Select strum-in pattern")
        strum_out = self.get_strum_pattern("Select strum-out pattern")
        
        mid = MidiFile(type=0)  # Type 0 for better timing
        track = MidiTrack()
        mid.tracks.append(track)

        # All initial MIDI messages with time=0, in correct order
        track.append(MetaMessage('set_tempo', tempo=bpm2tempo(bpm), time=0))
        track.append(Message('program_change', program=0, time=0))
        track.append(Message('control_change', control=7, value=100, time=0))  # Volume
        track.append(Message('control_change', control=10, value=64, time=0))  # Pan
        track.append(Message('control_change', control=91, value=0, time=0))   # Reverb off
        track.append(Message('control_change', control=93, value=0, time=0))   # Chorus off

        # Adjust root note for selected octave (fixed to stay in same octave)
        root_midi = self.NOTE_TO_MIDI[root_note] + octave_offset - 36  # Normalize to the selected octave

        # Define chord types with extensions
        chord_types = {
            # Basic triads
            'major': [0, 4, 7],
            'minor': [0, 3, 7],
            'dim': [0, 3, 6],
            'aug': [0, 4, 8],
            # Seventh chords
            'maj7': [0, 4, 7, 11],
            'min7': [0, 3, 7, 10],
            'dom7': [0, 4, 7, 10],
            'hdim7': [0, 3, 6, 10],
            'dim7': [0, 3, 6, 9],
            # Ninth chords
            'maj9': [0, 4, 7, 11, 14],
            'min9': [0, 3, 7, 10, 14],
            'dom9': [0, 4, 7, 10, 14],
            # Eleventh chords
            'maj11': [0, 4, 7, 11, 14, 17],
            'min11': [0, 3, 7, 10, 14, 17],
            'dom11': [0, 4, 7, 10, 14, 17],
            # Thirteenth chords
            'maj13': [0, 4, 7, 11, 14, 17, 21],
            'min13': [0, 3, 7, 10, 14, 17, 21],
            'dom13': [0, 4, 7, 10, 14, 17, 21]
        }

        # Map scale degrees to chord qualities based on extension level
        chord_qualities = {
            'triad': {
                0: 'major', 1: 'minor', 2: 'minor', 3: 'major',
                4: 'major', 5: 'minor', 6: 'dim'
            },
            'seventh': {
                0: 'maj7', 1: 'min7', 2: 'min7', 3: 'maj7',
                4: 'dom7', 5: 'min7', 6: 'hdim7'
            },
            'ninth': {
                0: 'maj9', 1: 'min9', 2: 'min9', 3: 'maj9',
                4: 'dom9', 5: 'min9', 6: 'hdim7'
            },
            'eleventh': {
                0: 'maj11', 1: 'min11', 2: 'min11', 3: 'maj11',
                4: 'dom11', 5: 'min11', 6: 'hdim7'
            },
            'thirteenth': {
                0: 'maj13', 1: 'min13', 2: 'min13', 3: 'maj13',
                4: 'dom13', 5: 'min13', 6: 'hdim7'
            }
        }

        # Map chord choice to quality dict
        quality_map = {1: 'triad', 2: 'seventh', 3: 'ninth', 
                      4: 'eleventh', 5: 'thirteenth'}
        quality_dict = quality_map[chord_choice]

        # Calculate timing values
        ticks_per_beat = mid.ticks_per_beat
        strum_speeds = {
            'slow': ticks_per_beat // 8,
            'med': ticks_per_beat // 16,
            'fast': ticks_per_beat // 32
        }

        # Update strum speeds based on BPM
        for pattern_name, pattern in self.STRUM_PATTERNS.items():
            if 'slow' in pattern_name:
                pattern['speed'] = strum_speeds['slow']
            elif 'med' in pattern_name:
                pattern['speed'] = strum_speeds['med']
            elif 'fast' in pattern_name:
                pattern['speed'] = strum_speeds['fast']

        def apply_inversion(notes, inv_type):
            """Apply chord inversion to a set of notes"""
            if inv_type == 0 or not notes:  # Root position or empty chord
                return notes
            if inv_type == 4:  # Random inversion
                inv_type = random.randint(0, min(3, len(notes) - 1))
            # Rotate notes for inversion
            inv_type = min(inv_type, len(notes) - 1)
            return notes[inv_type:] + [n + 12 for n in notes[:inv_type]]

        # Generate chord progression with precise timing
        for rep in range(repetitions):
            for i, chord_root in enumerate(progression):
                chord_type = chord_qualities[quality_dict][chord_root]
                chord_intervals = chord_types[chord_type]
                
                # Build chord notes with inversion
                chord_notes = [root_midi + chord_root + interval for interval in chord_intervals]
                chord_notes = apply_inversion(chord_notes, inversion)
                
                # Base velocity with slight random variation
                base_velocity = random.randint(64, 100)
                velocities = [max(40, base_velocity + random.randint(-5, 5)) for _ in range(len(chord_notes))]
                
                # Calculate strum timing
                strum_duration = 0
                if strum_in != 'none':
                    strum_duration = len(chord_notes) * self.get_strum_speed(strum_in)
                
                # Apply strum pattern for note-on events
                strum_on = self.apply_strum(chord_notes, velocities, strum_in, True, 0)
                
                # Add note-on events with timing based on selected mode
                if timing_mode == 1:  # Regular mode
                    for j, (note, velocity, time) in enumerate(strum_on):
                        if j == 0:
                            # First note of each chord
                            track.append(Message('note_on', note=note, velocity=velocity, 
                                              time=ticks_per_beat if (i > 0 or rep > 0) else 0))
                        else:
                            # Subsequent notes in the chord
                            track.append(Message('note_on', note=note, velocity=velocity, time=time))
                else:  # Tight mode
                    for j, (note, velocity, time) in enumerate(strum_on):
                        if i == 0 and j == 0 and rep == 0:
                            # Very first note of progression
                            track.append(Message('note_on', note=note, velocity=velocity, time=0))
                        else:
                            # All other notes - maintain tight timing
                            track.append(Message('note_on', note=note, velocity=velocity, time=time))
                
                # Calculate remaining time for the chord duration
                if timing_mode == 1:  # Regular mode
                    if rep < repetitions - 1 or (rep == repetitions - 1 and i < len(progression) - 1):
                        remaining_time = ticks_per_beat - strum_duration
                    else:
                        remaining_time = ticks_per_beat
                else:  # Tight mode
                    remaining_time = max(1, ticks_per_beat - strum_duration)  # Ensure at least 1 tick
                
                # Apply strum pattern for note-off events
                strum_off = self.apply_strum(chord_notes, velocities, strum_out, False, remaining_time)
                
                # Add note-off events
                for j, (note, _, time) in enumerate(strum_off):
                    if timing_mode == 2 and j == len(strum_off) - 1 and (rep < repetitions - 1 or (rep == repetitions - 1 and i < len(progression) - 1)):
                        # In tight mode, ensure last note-off connects to next chord
                        time = max(1, time)  # Ensure at least 1 tick between chords
                    track.append(Message('note_off', note=note, velocity=0, time=time))

        # If there are remaining bars, add them
        if remaining_bars > 0:
            for i, chord_root in enumerate(progression[:remaining_bars]):
                # ... (same chord generation code as above, just for remaining bars) ...
                pass  # Remove this line when implementing remaining bars

        # Update filename to include progression type and bars
        timing_str = "_regular" if timing_mode == 1 else "_tight"
        extensions = {1: "triad", 2: "7th", 3: "9th", 4: "11th", 5: "13th"}
        inversions = {0: "root", 1: "1st", 2: "2nd", 3: "3rd", 4: "rand"}
        ext_str = extensions[chord_choice]
        inv_str = inversions[inversion]
        strum_str = f"_strum_{strum_in}_{strum_out}"
        octave_str = f"_oct{octave_choice + 1}"
        prog_str = f"_{progression_type}_{progression_display}"
        bars_str = f"_{total_bars}bars"
        
        filename = f"{root_note}{prog_str}_{ext_str}_{inv_str}{strum_str}{timing_str}{octave_str}{bars_str}_{bpm}bpm.mid"
        mid.save(filename)
        print(f"\n✨ Chord progression generated and saved as: {filename}")
        input("\nPress Enter to return to menu...")

    def generate_melody_web(self, output_file, root_note, mode, rhythm_pattern, bpm, bars,
                          use_swing=False, swing_type='medium', use_humanization=False,
                          humanization_amount=0.2):
        """Web version of melody generation that saves to a specific file"""
        # Create MIDI file
        mid = MidiFile()
        track = MidiTrack()
        mid.tracks.append(track)

        # Setup track
        track.append(Message('program_change', program=0, time=0))
        track.append(Message('control_change', control=7, value=100, time=0))
        track.append(Message('control_change', control=10, value=64, time=0))

        # Calculate scale notes
        root_midi = self.NOTE_TO_MIDI[root_note]
        scale_intervals = self.SCALE_MODES[mode]
        scale_notes = [root_midi + interval for interval in scale_intervals]
        scale_notes.extend([note + 12 for note in scale_notes])

        # Get swing amount if enabled
        swing_amount = self.SWING_AMOUNTS[swing_type] if use_swing else 0

        # Generate melody
        ticks_per_beat = mid.ticks_per_beat
        pattern = self.RHYTHM_PATTERNS[rhythm_pattern]

        for bar in range(bars):
            for i, (duration, velocity) in enumerate(pattern):
                note = random.choice(scale_notes)
                ticks = int(ticks_per_beat * duration)
                velocity_val = int(velocity * 64)

                # Apply swing if enabled
                if use_swing:
                    ticks = self.apply_swing(ticks, i % 2 == 1, swing_amount)

                # Apply humanization if enabled
                if use_humanization:
                    ticks = self.apply_microshift(ticks, humanization_amount)
                    velocity_val = self.apply_microshift(velocity_val, humanization_amount/2)

                track.append(Message('note_on', note=note, velocity=velocity_val, time=0))
                track.append(Message('note_off', note=note, velocity=velocity_val, time=ticks))

        # Save to specified file
        mid.save(output_file)

    def generate_chord_progression_web(self, output_file, root_note, progression_type, bpm,
                                    total_bars, octave_choice, timing_mode, chord_type,
                                    inversion, strum_in, strum_out):
        """Web version of chord progression generation that saves to a specific file"""
        # Get progression
        if progression_type in self.CHORD_PROGRESSIONS:
            progression = self.CHORD_PROGRESSIONS[progression_type]
        else:
            # Handle custom or random progression
            progression = [int(n) for n in progression_type.split('-')]

        # Calculate repetitions
        repetitions = max(1, total_bars // len(progression))
        remaining_bars = total_bars % len(progression)

        mid = MidiFile(type=0)  # Type 0 for better timing
        track = MidiTrack()
        mid.tracks.append(track)

        # Setup track
        track.append(MetaMessage('set_tempo', tempo=bpm2tempo(bpm), time=0))
        track.append(Message('program_change', program=0, time=0))
        track.append(Message('control_change', control=7, value=100, time=0))
        track.append(Message('control_change', control=10, value=64, time=0))
        track.append(Message('control_change', control=91, value=0, time=0))
        track.append(Message('control_change', control=93, value=0, time=0))

        # Adjust root note for selected octave
        root_midi = self.NOTE_TO_MIDI[root_note] + (octave_choice + 1) * 12 - 36

        # Map chord choice to quality dict
        quality_map = {1: 'triad', 2: 'seventh', 3: 'ninth', 
                      4: 'eleventh', 5: 'thirteenth'}
        quality_dict = quality_map[chord_type]

        # Generate chord progression
        for rep in range(repetitions):
            for i, chord_root in enumerate(progression):
                chord_type = self.chord_qualities[quality_dict][chord_root]
                chord_intervals = self.chord_types[chord_type]
                
                # Build chord notes with inversion
                chord_notes = [root_midi + chord_root + interval for interval in chord_intervals]
                chord_notes = self.apply_inversion(chord_notes, inversion)
                
                # Base velocity with slight random variation
                base_velocity = random.randint(64, 100)
                velocities = [max(40, base_velocity + random.randint(-5, 5)) 
                            for _ in range(len(chord_notes))]
                
                # Calculate strum timing
                strum_duration = 0
                if strum_in != 'none':
                    strum_duration = len(chord_notes) * self.get_strum_speed(strum_in)
                
                # Apply strum patterns
                strum_on = self.apply_strum(chord_notes, velocities, strum_in, True, 0)
                
                # Add note-on events
                for j, (note, velocity, time) in enumerate(strum_on):
                    if timing_mode == 1:  # Regular mode
                        if j == 0:
                            track.append(Message('note_on', note=note, velocity=velocity, 
                                              time=mid.ticks_per_beat if (i > 0 or rep > 0) else 0))
                        else:
                            track.append(Message('note_on', note=note, velocity=velocity, time=time))
                    else:  # Tight mode
                        if i == 0 and j == 0 and rep == 0:
                            track.append(Message('note_on', note=note, velocity=velocity, time=0))
                        else:
                            track.append(Message('note_on', note=note, velocity=velocity, time=time))
                
                # Calculate remaining time
                if timing_mode == 1:
                    remaining_time = (mid.ticks_per_beat - strum_duration 
                                   if rep < repetitions - 1 or 
                                   (rep == repetitions - 1 and i < len(progression) - 1)
                                   else mid.ticks_per_beat)
                else:
                    remaining_time = max(1, mid.ticks_per_beat - strum_duration)
                
                # Apply strum pattern for note-off events
                strum_off = self.apply_strum(chord_notes, velocities, strum_out, False, remaining_time)
                
                # Add note-off events
                for j, (note, _, time) in enumerate(strum_off):
                    if timing_mode == 2 and j == len(strum_off) - 1 and (rep < repetitions - 1 or (rep == repetitions - 1 and i < len(progression) - 1)):
                        time = max(1, time)
                    track.append(Message('note_off', note=note, velocity=0, time=time))

        # Save to specified file
        mid.save(output_file)


if __name__ == "__main__":
    generator = MelodyGenerator()
    generator.show_menu()
