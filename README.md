# Python MIDI Melody Generator 🎵

A powerful MIDI melody and chord progression generator that creates musical patterns with various features including:
- Melody generation with different scales and modes
- Chord progression generation with multiple voicing options
- Arpeggio patterns
- Experimental melodies
- Humanization and swing features
- Customizable strumming patterns

## Requirements

- Python 3.7 or higher
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone <your-repository-url>
cd chord-generator
```

2. Create and activate a virtual environment (recommended):
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Web Application

1. Start the web server:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. Use the web interface to:
   - Generate melodies with different scales and modes
   - Create chord progressions with various voicings
   - Customize rhythm patterns and strumming
   - Add humanization and swing effects
   - Download generated MIDI files

### Command Line Interface

1. Run the application in CLI mode:
```bash
python main.py
```

2. Choose from the following options in the menu:
   - Generate new melody
   - Generate experimental melody
   - Generate arpeggio pattern
   - Generate chord progression
   - List available scales/modes
   - List rhythm patterns

3. Follow the prompts to customize your generation:
   - Select root note (C, C#, D, etc.)
   - Choose scale mode (major, minor, dorian, etc.)
   - Set tempo (BPM)
   - Add humanization and swing effects
   - Configure chord types and inversions
   - Set strumming patterns

4. The generated MIDI files will be saved in the current directory with descriptive filenames.

## Deployment

To deploy the web application to a production server:

1. Install production dependencies:
```bash
pip install gunicorn
```

2. Set up environment variables:
```bash
export FLASK_ENV=production
export FLASK_SECRET_KEY=your-secret-key
```

3. Run with Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

For production deployment, it's recommended to:
- Use a reverse proxy (e.g., Nginx)
- Set up SSL/TLS certificates
- Configure proper security headers
- Use environment variables for sensitive settings

## Features

### Melody Generation
- Multiple scale modes (major, minor, dorian, phrygian, mixolydian, blues)
- Customizable rhythm patterns
- Swing feel options
- Humanization for natural timing variations

### Chord Progressions
- Preset progressions (basic, jazz, blues, etc.)
- Custom progression input
- Extended chord voicings (triads to 13th chords)
- Multiple inversion options
- Strumming patterns with variable speeds

### Arpeggio Generation
- Ascending and descending patterns
- Random pattern generation
- Scale-based note selection

## Output

The generator creates MIDI (.mid) files that can be:
- Imported into any DAW (Digital Audio Workstation)
- Played with MIDI-compatible instruments
- Used as a basis for further musical composition

## File Naming Convention

Generated files follow a descriptive naming pattern including:
- Root note
- Progression type or scale mode
- Tempo (BPM)
- Special features (swing, humanization)
- Chord types and inversions
- Number of bars

Example: `C_major_120bpm_swing_heavy_humanized.mid`

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 