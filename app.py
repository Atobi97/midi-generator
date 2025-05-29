from flask import Flask, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename
import os
from main import MelodyGenerator
import tempfile
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'static/generated'

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize the melody generator
generator = MelodyGenerator()

@app.route('/')
def index():
    return render_template('index.html',
                         scales=generator.SCALE_MODES.keys(),
                         rhythm_patterns=generator.RHYTHM_PATTERNS.keys(),
                         chord_progressions=generator.CHORD_PROGRESSIONS.keys(),
                         notes=generator.NOTE_TO_MIDI.keys())

@app.route('/generate_melody', methods=['POST'])
def generate_melody():
    try:
        data = request.get_json()
        
        # Create a temporary file to store the MIDI
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mid', dir=app.config['UPLOAD_FOLDER']) as tmp:
            # Extract parameters from request
            root_note = data.get('root_note', 'C').upper()
            mode = data.get('mode', 'major').lower()
            rhythm_pattern = data.get('rhythm_pattern', 'basic').lower()
            bpm = int(data.get('bpm', 120))
            bars = int(data.get('bars', 4))
            use_swing = data.get('use_swing', False)
            swing_type = data.get('swing_type', 'medium')
            use_humanization = data.get('use_humanization', False)
            humanization_amount = float(data.get('humanization_amount', 0.2))

            # Generate the melody
            generator.generate_melody_web(
                output_file=tmp.name,
                root_note=root_note,
                mode=mode,
                rhythm_pattern=rhythm_pattern,
                bpm=bpm,
                bars=bars,
                use_swing=use_swing,
                swing_type=swing_type,
                use_humanization=use_humanization,
                humanization_amount=humanization_amount
            )

            # Get the filename only
            filename = os.path.basename(tmp.name)
            
            return jsonify({
                'status': 'success',
                'filename': filename,
                'download_url': f'/download/{filename}'
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@app.route('/generate_chord_progression', methods=['POST'])
def generate_chord_progression():
    try:
        data = request.get_json()
        
        # Create a temporary file to store the MIDI
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mid', dir=app.config['UPLOAD_FOLDER']) as tmp:
            # Extract parameters from request
            root_note = data.get('root_note', 'C').upper()
            progression_type = data.get('progression_type', 'basic')
            bpm = int(data.get('bpm', 120))
            total_bars = int(data.get('total_bars', 4))
            octave_choice = int(data.get('octave', 2))
            timing_mode = int(data.get('timing_mode', 1))
            chord_type = int(data.get('chord_type', 1))
            inversion = int(data.get('inversion', 0))
            strum_in = data.get('strum_in', 'none')
            strum_out = data.get('strum_out', 'none')

            # Generate the chord progression
            generator.generate_chord_progression_web(
                output_file=tmp.name,
                root_note=root_note,
                progression_type=progression_type,
                bpm=bpm,
                total_bars=total_bars,
                octave_choice=octave_choice,
                timing_mode=timing_mode,
                chord_type=chord_type,
                inversion=inversion,
                strum_in=strum_in,
                strum_out=strum_out
            )

            # Get the filename only
            filename = os.path.basename(tmp.name)
            
            return jsonify({
                'status': 'success',
                'filename': filename,
                'download_url': f'/download/{filename}'
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@app.route('/download/<filename>')
def download_file(filename):
    try:
        return send_file(
            os.path.join(app.config['UPLOAD_FOLDER'], filename),
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return str(e), 404

@app.route('/get_options')
def get_options():
    return jsonify({
        'scales': list(generator.SCALE_MODES.keys()),
        'rhythm_patterns': list(generator.RHYTHM_PATTERNS.keys()),
        'chord_progressions': list(generator.CHORD_PROGRESSIONS.keys()),
        'notes': list(generator.NOTE_TO_MIDI.keys()),
        'swing_amounts': list(generator.SWING_AMOUNTS.keys()),
        'strum_patterns': list(generator.STRUM_PATTERNS.keys())
    })

if __name__ == '__main__':
    app.run(debug=True) 