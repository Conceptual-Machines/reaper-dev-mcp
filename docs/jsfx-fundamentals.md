# JSFX Fundamentals

## Parameter Indexing (CRITICAL)

**The most common source of bugs in JSFX development**: Parameters are indexed by **SLIDER NUMBER ORDER**, not declaration order.

### How It Works

When you declare sliders in JSFX, REAPER assigns parameter indices based on the **numeric value** of the slider number, not the order they appear in your code.

### Real Example: SideFX_Modulator.jsfx

```jsfx
// Slider declarations (in order of appearance):
slider1:0<0,1,1{Free,Sync}>-Tempo Mode
slider2:1<0.01,20,0.01>-Rate (Hz)
slider3:5<0,17,1{8 bars,4 bars,...}>-Sync Rate
slider4:0<0,1,0.001>-Output
slider5:0<0,1,0.001>-Phase
slider6:1<0,1,0.01>-Depth

slider20:0<0,3,1{Free,Transport,MIDI,Audio}>-Trigger Mode
slider21:0<0,1,1{This Track,MIDI Bus}>-MIDI Source
slider22:0<0,127,1>-MIDI Note (0=any)
slider23:0.5<0,1,0.01>-Audio Threshold
slider24:100<1,2000,1>-Attack (ms)
slider25:500<1,5000,1>-Release (ms)

slider26:2<0,4,1{Off,4,8,16,32}>Grid
slider27:1<0,1,1{Off,On}>Snap

slider28:0<0,1,1{Loop,One Shot}>-LFO Mode

slider30:4<2,16,1>-Num Points
```

**Parameter indices** (accessed via `param[0]`, `param[1]`, etc.):
- `param[0]` = slider1
- `param[1]` = slider2
- `param[2]` = slider3
- `param[3]` = slider4
- `param[4]` = slider5
- `param[5]` = slider6
- `param[6]` = slider20 (not slider7!)
- `param[7]` = slider21
- `param[8]` = slider22
- `param[9]` = slider23
- `param[10]` = slider24
- `param[11]` = slider25
- `param[12]` = slider26 (comes BEFORE slider28!)
- `param[13]` = slider27
- `param[14]` = slider28
- `param[15]` = slider30

**Key insight**: `slider26` (param[12]) comes **before** `slider28` (param[14]) in the parameter index, even though slider28 appears earlier in the code!

### Common Bug Pattern

```jsfx
// WRONG: Assuming parameters are indexed by declaration order
slider1:0<0,1,0.001>-Param1
slider5:0<0,1,0.001>-Param2
slider10:0<0,1,0.001>-Param3

// In code:
param[0] = slider1  // ✓ Correct
param[1] = slider5  // ✗ WRONG! slider5 is param[1], but you might think it's param[4]
param[2] = slider10 // ✗ WRONG! slider10 is param[2], but you might think it's param[9]
```

### Correct Pattern

Always access parameters by their **slider number order**, not declaration order:

```jsfx
// Access by slider number order:
param[0]  // slider1
param[1]  // slider2
param[2]  // slider3
// ... skip to slider20
param[6]  // slider20 (first slider >= 20)
param[7]  // slider21
// etc.
```

## Slider Visibility

Use the `-` prefix to hide sliders from the JSFX UI while keeping them functional:

```jsfx
slider4:0<0,1,0.001>-Output  // Hidden output parameter
```

The `-` prefix hides the slider from the UI, but it still:
- Appears in the parameter index
- Can be automated
- Can be accessed via `param[]` array
- Can be linked via plink API

## @sections

JSFX code is organized into sections that run at different times:

### @init
- Runs **once** when the plugin loads
- Use for: initializing variables, setting up memory arrays, calculating initial values

```jsfx
@init
MAX_NODES = 16;
mem_c1 = 1000;  // Memory array starting index
lfo_phase = 0;  // Initialize state
```

### @slider
- Runs **whenever any slider value changes**
- Use for: recalculating derived values, updating coefficients

```jsfx
@slider
attack_coeff = calc_coeff(slider24);  // Recalculate when slider24 changes
update_spline();  // Rebuild spline when curve points change
```

### @block
- Runs **once per audio block** (typically 64-512 samples)
- Use for: MIDI processing, transport state checking, block-level calculations

```jsfx
@block
trigger_mode = slider20;
// Process MIDI events
while (midirecv(offset, msg1, msg2, msg3)) (
  // Handle MIDI
  midisend(offset, msg1, msg2, msg3);
);
```

### @sample
- Runs **for each audio sample**
- Use for: audio processing, per-sample calculations, LFO/oscillator updates

```jsfx
@sample
// Update LFO phase
lfo_phase += rate / srate;
lfo_phase >= 1 ? lfo_phase -= 1;  // Wrap

// Process audio
spl0 = spl0 * gain;
spl1 = spl1 * gain;
```

### @gfx
- Runs **for graphics/UI rendering** (optional)
- Use for: drawing custom UI, handling mouse input

```jsfx
@gfx 500 400  // Width x Height
gfx_clear = 0x1a1a1a;  // Background color
// Draw UI elements
gfx_line(x1, y1, x2, y2);
```

## Memory Management

### Local Variables
- Scoped to the current section
- Fast access
- Use for: temporary calculations, loop counters

```jsfx
@sample
local(i, temp, result) (
  i = 0;
  temp = 0;
  result = temp * 2;
);
```

### Memory Arrays
- Persistent across sections
- Use `mem[index]` syntax
- Use for: storing data that persists between samples/blocks

```jsfx
@init
mem_c1 = 1000;  // Starting index for coefficient array
mem_c2 = 1020;  // Starting index for another array

@slider
// Store values in memory arrays
mem_c1[0] = coefficient1;
mem_c1[1] = coefficient2;
```

### When to Use Which

**Use local variables for:**
- Temporary calculations
- Loop counters
- Intermediate values that don't need to persist

**Use memory arrays for:**
- Data that needs to persist between samples
- Lookup tables
- Buffers (delay lines, etc.)
- State that needs to survive section transitions

## Common Pitfalls

1. **Parameter indexing confusion**: Always remember parameters are indexed by slider number order, not declaration order
2. **Memory array index conflicts**: Make sure your memory array starting indices don't overlap
3. **Section execution order**: `@init` runs once, `@slider` runs on changes, `@block` runs per block, `@sample` runs per sample
4. **Hidden sliders still count**: Sliders with `-` prefix still appear in parameter indices

