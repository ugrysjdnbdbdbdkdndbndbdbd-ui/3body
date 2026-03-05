// Simple Sci-Fi UI Sound Synthesizer using Web Audio API
class SoundManager {
  private ctx: AudioContext | null = null;
  private masterGain: GainNode | null = null;
  private enabled: boolean = true;

  constructor() {
    try {
      // Initialize on user interaction usually, but we'll try lazy init
      const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext;
      if (AudioContextClass) {
        this.ctx = new AudioContextClass();
        this.masterGain = this.ctx.createGain();
        this.masterGain.gain.value = 0.3; // Default volume
        this.masterGain.connect(this.ctx.destination);
      }
    } catch (e) {
      console.warn('Web Audio API not supported');
    }
  }

  private ensureContext() {
    if (this.ctx && this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
  }

  // Generate a simple oscillator tone
  playTone(freq: number, type: OscillatorType, duration: number, volume: number = 1) {
    if (!this.ctx || !this.masterGain || !this.enabled) return;
    this.ensureContext();

    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();

    osc.type = type;
    osc.frequency.setValueAtTime(freq, this.ctx.currentTime);
    
    // Envelope
    gain.gain.setValueAtTime(0, this.ctx.currentTime);
    gain.gain.linearRampToValueAtTime(volume, this.ctx.currentTime + 0.01);
    gain.gain.exponentialRampToValueAtTime(0.01, this.ctx.currentTime + duration);

    osc.connect(gain);
    gain.connect(this.masterGain);

    osc.start();
    osc.stop(this.ctx.currentTime + duration);
  }

  // --- Public SFX Methods ---

  // 1. Hover: Short, high-pitch chirp
  playHover() {
    // 2000Hz sine wave, very short
    this.playTone(800, 'sine', 0.05, 0.1);
  }

  // 2. Click: Mechanical/Tech "Blip"
  playClick() {
    if (!this.ctx || !this.masterGain || !this.enabled) return;
    this.ensureContext();

    const t = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();

    osc.type = 'square';
    osc.frequency.setValueAtTime(400, t);
    osc.frequency.exponentialRampToValueAtTime(100, t + 0.1);

    gain.gain.setValueAtTime(0.3, t);
    gain.gain.exponentialRampToValueAtTime(0.01, t + 0.1);

    osc.connect(gain);
    gain.connect(this.masterGain);

    osc.start();
    osc.stop(t + 0.1);
  }

  // 3. Confirm/Success: Ascending chime
  playConfirm() {
    if (!this.ctx || !this.masterGain || !this.enabled) return;
    this.ensureContext();

    const ctx = this.ctx;
    const masterGain = this.masterGain;
    const now = ctx.currentTime;
    [440, 554, 659].forEach((freq, i) => {
       const osc = ctx.createOscillator();
       const gain = ctx.createGain();
       osc.type = 'sine';
       osc.frequency.value = freq;
       gain.gain.setValueAtTime(0, now);
       gain.gain.linearRampToValueAtTime(0.2, now + i * 0.05);
       gain.gain.exponentialRampToValueAtTime(0.01, now + i * 0.05 + 0.2);
       
       osc.connect(gain);
       gain.connect(masterGain);
       osc.start(now + i * 0.05);
       osc.stop(now + i * 0.05 + 0.3);
    });
  }

  // 4. Alert/Error: Low buzz
  playAlert() {
    this.playTone(150, 'sawtooth', 0.3, 0.4);
  }

  // Toggle Mute
  toggle() {
    this.enabled = !this.enabled;
    if (!this.enabled) {
      this.stopAmbient();
    }
    return this.enabled;
  }

  // --- Ambient & Special SFX ---
  private ambientOsc: OscillatorNode | null = null;
  private ambientGain: GainNode | null = null;
  private lfo: OscillatorNode | null = null;

  startAmbient(type: 'void' | 'nature') {
    if (!this.ctx || !this.enabled) return;
    this.ensureContext();
    this.stopAmbient(); // Stop existing

    const t = this.ctx.currentTime;
    this.ambientOsc = this.ctx.createOscillator();
    this.ambientGain = this.ctx.createGain();
    this.lfo = this.ctx.createOscillator();
    const lfoGain = this.ctx.createGain();

    if (type === 'void') {
      // Deep Space Drone
      this.ambientOsc.type = 'sine';
      this.ambientOsc.frequency.setValueAtTime(55, t); // Low A

      // LFO modulates amplitude for "breathing"
      this.lfo.frequency.value = 0.1; // Very slow
      this.lfo.connect(lfoGain);
      lfoGain.gain.value = 0.05; // Subtle modulation
      lfoGain.connect(this.ambientGain.gain);

      this.ambientGain.gain.setValueAtTime(0.05, t); // Quiet base volume
    } else if (type === 'nature') {
      // Wind-like (White noise approximation using FM modulation)
      // Since we can't easily generate white noise without buffer, we use FM synthesis
      this.ambientOsc.type = 'triangle';
      this.ambientOsc.frequency.setValueAtTime(220, t);
      
      this.lfo.type = 'sawtooth';
      this.lfo.frequency.value = 0.5;
      this.lfo.connect(lfoGain);
      lfoGain.gain.value = 100;
      lfoGain.connect(this.ambientOsc.frequency);

      this.ambientGain.gain.setValueAtTime(0.02, t);
    }

    this.ambientOsc.connect(this.ambientGain);
    this.ambientGain.connect(this.masterGain!);
    this.ambientOsc.start();
    this.lfo.start();
  }

  stopAmbient() {
    if (this.ambientOsc) {
      try {
        this.ambientOsc.stop();
        this.ambientOsc.disconnect();
      } catch {}
      this.ambientOsc = null;
    }
    if (this.lfo) {
      try {
        this.lfo.stop();
        this.lfo.disconnect();
      } catch {}
      this.lfo = null;
    }
  }

  playBigCrunch() {
    if (!this.ctx || !this.masterGain || !this.enabled) return;
    this.ensureContext();

    const t = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();

    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(100, t);
    osc.frequency.exponentialRampToValueAtTime(10, t + 2); // Pitch drop

    gain.gain.setValueAtTime(0.5, t);
    gain.gain.exponentialRampToValueAtTime(0.01, t + 2);

    osc.connect(gain);
    gain.connect(this.masterGain);

    osc.start();
    osc.stop(t + 2);
  }
}

export const soundManager = new SoundManager();
