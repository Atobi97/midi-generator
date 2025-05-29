// MIDI.js library for client-side MIDI generation
class MIDIGenerator {
    constructor() {
        this.initializeMIDI();
    }

    async initializeMIDI() {
        if (navigator.requestMIDIAccess) {
            try {
                this.midiAccess = await navigator.requestMIDIAccess();
                console.log('MIDI Access initialized');
            } catch (err) {
                console.error('Error initializing MIDI:', err);
            }
        }
    }

    generateMelody(params) {
        // Create MIDI file data
        const midiData = this.createMIDIFile(params);
        
        // Create download
        this.createDownload(midiData, this.generateMelodyFilename(params));
    }

    generateChordProgression(params) {
        // Create MIDI file data
        const midiData = this.createMIDIFile(params);
        
        // Create download
        this.createDownload(midiData, this.generateChordFilename(params));
    }

    createMIDIFile(params) {
        // This is a simplified version - you'll need to implement the actual MIDI generation logic
        // For now, we'll create a simple MIDI file with a single note
        const midiData = new Uint8Array([
            0x4D, 0x54, 0x68, 0x64, // MThd
            0x00, 0x00, 0x00, 0x06, // Header size
            0x00, 0x00, // Format type
            0x00, 0x01, // Number of tracks
            0x00, 0x60, // Time division
            0x4D, 0x54, 0x72, 0x6B, // MTrk
            0x00, 0x00, 0x00, 0x0B, // Chunk size
            0x00, 0x90, // Note on
            0x3C, // Note number (middle C)
            0x40, // Velocity
            0x83, 0x00, // Note off (after delay)
            0x3C, // Note number
            0x00, // Velocity
            0x00  // End of track
        ]);

        return midiData;
    }

    createDownload(midiData, filename) {
        const blob = new Blob([midiData], { type: 'audio/midi' });
        const url = window.URL.createObjectURL(blob);
        const downloadLink = document.createElement('a');
        downloadLink.href = url;
        downloadLink.download = filename;
        document.body.appendChild(downloadLink);
        downloadLink.click();
        document.body.removeChild(downloadLink);
        window.URL.revokeObjectURL(url);
    }

    generateMelodyFilename(params) {
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        return `melody_${params.root_note}_${params.mode}_${params.bpm}bpm_${timestamp}.mid`;
    }

    generateChordFilename(params) {
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        return `chord_${params.root_note}_${params.progression_type}_${params.bpm}bpm_${timestamp}.mid`;
    }
}

// Initialize the generator
const midiGenerator = new MIDIGenerator();

// Form handling
document.addEventListener('DOMContentLoaded', function() {
    // Melody form submission
    document.getElementById('melody-form').addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(this);
        const params = Object.fromEntries(formData.entries());
        
        // Add checkbox values
        params.use_swing = document.getElementById('use_swing').checked;
        params.use_humanization = document.getElementById('use_humanization').checked;

        try {
            midiGenerator.generateMelody(params);
            showSuccess();
        } catch (error) {
            showError(error.message);
        }
    });

    // Chord form submission
    document.getElementById('chord-form').addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(this);
        const params = Object.fromEntries(formData.entries());

        try {
            midiGenerator.generateChordProgression(params);
            showSuccess();
        } catch (error) {
            showError(error.message);
        }
    });

    // UI helpers
    function showSuccess() {
        document.getElementById('result-section').style.display = 'block';
        document.getElementById('error-section').style.display = 'none';
    }

    function showError(message) {
        document.getElementById('error-message').textContent = message;
        document.getElementById('error-section').style.display = 'block';
        document.getElementById('result-section').style.display = 'none';
    }
}); 