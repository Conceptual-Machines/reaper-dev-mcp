# REAPER Parameter System

## Parameter Types

### Continuous Parameters
- Normalized range: **0.0 to 1.0**
- Represent continuous values (volume, pan, frequency, etc.)
- Can use either normalized or raw values

### Discrete/Switch Parameters
- **Toggles**: 0 = off, 1 = on
- **Enums**: Integer steps (0, 1, 2, 3, etc.) representing discrete choices
- **Must use raw values**, not normalized

### When to Use Which Function

- **`TrackFX_SetParam`**: Use for discrete params (switches, enums) with raw values
- **`TrackFX_SetParamNormalized`**: Use for continuous params (can use normalized 0.0-1.0)

## Reading Parameters

### TrackFX_GetParam
```lua
local retval, min_val, max_val = reaper.TrackFX_GetParam(track, fx_idx, param_idx)
```
- Returns: `retval` (boolean), `min_val` (number), `max_val` (number)
- Returns **raw value range**, not the current value
- For current value, use `TrackFX_GetParamNormalized` or `TrackFX_GetParamEx`

### TrackFX_GetParamNormalized
```lua
local value = reaper.TrackFX_GetParamNormalized(track, fx_idx, param_idx)
```
- Returns: normalized value (0.0 to 1.0)
- Use for: continuous parameters

### TrackFX_GetParamEx
```lua
local retval, min_val, max_val, mid_val = reaper.TrackFX_GetParamEx(track, fx_idx, param_idx)
```
- Returns: `retval` (boolean), `min_val`, `max_val`, `mid_val` (number)
- Includes midpoint value (useful for some parameter types)

### For Discrete Parameters
Always use **raw values** when reading discrete parameters:
```lua
-- For a toggle (0 or 1)
local raw_val = reaper.TrackFX_GetParam(track, fx_idx, param_idx)
-- raw_val will be 0 or 1, not 0.0-1.0
```

## Setting Parameters

### Discrete Parameters (Switches, Enums)
**Always use `TrackFX_SetParam` with raw values:**

```lua
-- Toggle parameter (0 = off, 1 = on)
reaper.TrackFX_SetParam(track, fx_idx, param_idx, 1)  -- Turn on

-- Enum parameter (0, 1, 2, 3, etc.)
reaper.TrackFX_SetParam(track, fx_idx, param_idx, 2)  -- Select option 2
```

**Common mistake**: Using normalized values on discrete params causes the wrong parameter to change or unexpected behavior.

### Continuous Parameters
Can use either normalized or raw:

```lua
-- Using normalized (0.0 to 1.0)
reaper.TrackFX_SetParamNormalized(track, fx_idx, param_idx, 0.5)  -- 50%

-- Using raw value
reaper.TrackFX_SetParam(track, fx_idx, param_idx, raw_value)
```

## Named Config Parameters

### TrackFX_GetNamedConfigParm
```lua
local retval, buf = reaper.TrackFX_GetNamedConfigParm(track, fx_idx, param_name)
```

**CRITICAL**: This function returns a **single value** (`buf` or `nil`), NOT a tuple like `(retval, buf)`.

**Common mistake**: Destructuring as two values:
```lua
-- WRONG:
local retval, buf = reaper.TrackFX_GetNamedConfigParm(track, fx_idx, "param.0.plink.active")
-- This will fail because the function doesn't return retval separately

-- CORRECT:
local buf = reaper.TrackFX_GetNamedConfigParm(track, fx_idx, "param.0.plink.active")
if buf then
  -- buf contains the value (as a string)
  local active = (buf == "1")
end
```

### TrackFX_SetNamedConfigParm
```lua
local ok = reaper.TrackFX_SetNamedConfigParm(track, fx_idx, param_name, value)
```
- Returns: `boolean` (success)
- `value` must be a **string** (even for numeric values)

```lua
-- Set plink active
reaper.TrackFX_SetNamedConfigParm(track, fx_idx, "param.0.plink.active", "1")

-- Set plink effect index (as string!)
reaper.TrackFX_SetNamedConfigParm(track, fx_idx, "param.0.plink.effect", "2")
```

### Common Uses
- **plink API**: Parameter modulation links
- **Container info**: `parent_container`, `container_count`, `container_item.X`
- **FX-specific config**: PDC, pin mappings, FX type, etc.

## ReaWrap API Patterns

### ReaWrap's High-Level API

ReaWrap provides convenient wrappers that handle return value patterns:

```lua
local TrackFX = require("track_fx")
local fx = TrackFX:new(track, fx_idx)

-- Get named config param (returns single value or nil)
local active = fx:get_named_config_param("param.0.plink.active")
if active == "1" then
  -- Link is active
end

-- Set named config param
fx:set_named_config_param("param.0.plink.active", "1")
```

### Return Value Conventions

**ReaWrap methods return single values**, not tuples:
- `get_named_config_param()`: Returns `string|nil` (not `retval, buf`)
- `get_param_normalized()`: Returns `number`
- `set_named_config_param()`: Returns `boolean`

This is different from raw ReaScript API which often returns `(retval, ...)` tuples.

## Code Examples

### Correct: Reading a Discrete Parameter
```lua
-- For a toggle switch
local raw_val = reaper.TrackFX_GetParam(track, fx_idx, param_idx)
local is_on = (raw_val > 0.5)  -- Convert to boolean
```

### Correct: Setting a Discrete Parameter
```lua
-- Toggle on
reaper.TrackFX_SetParam(track, fx_idx, param_idx, 1)

-- Select enum option 2
reaper.TrackFX_SetParam(track, fx_idx, param_idx, 2)
```

### Correct: Reading Named Config Param
```lua
-- Single return value
local buf = reaper.TrackFX_GetNamedConfigParm(track, fx_idx, "param.0.plink.active")
if buf and buf == "1" then
  -- Link is active
end
```

### Incorrect: Destructuring Named Config Param
```lua
-- WRONG - This will fail!
local retval, buf = reaper.TrackFX_GetNamedConfigParm(track, fx_idx, "param.0.plink.active")
-- The function doesn't return retval separately
```

### Correct: Using ReaWrap
```lua
local fx = TrackFX:new(track, fx_idx)
local active = fx:get_named_config_param("param.0.plink.active")
-- Returns string or nil directly
```

