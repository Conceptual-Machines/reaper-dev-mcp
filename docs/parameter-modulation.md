# Parameter Modulation (plink API)

## What is plink?

**plink** is REAPER's internal parameter modulation system. It allows one FX parameter to modulate another FX parameter, creating dynamic automation and modulation effects.

### Format
plink parameters use the format: `param.X.plink.active/effect/param/scale`

Where:
- `X` = target parameter index (the parameter being modulated)
- `active` = "1" if link is active, "0" or missing if inactive
- `effect` = source FX index (local or global, see below)
- `param` = source parameter index (the parameter providing modulation)
- `scale` = modulation amount (typically 0.0 to 1.0, as string)

### Used By
- LFO plugins
- Modulators (like SideFX Modulator)
- Parameter automation
- MIDI CC modulation

## Local vs Global FX Indices (CRITICAL)

**This is the most common source of bugs when working with container FX!**

### The Rule

- **When both source and target FX are in the SAME container**: Use **LOCAL index** (0, 1, 2, ...)
- **When in different containers or track-level**: Use **GLOBAL encoded index** (0x2000000 + offset)

### How to Detect

Compare parent container GUIDs:
```lua
local target_parent = target_fx:get_parent_container()
local source_parent = source_fx:get_parent_container()

if target_parent and source_parent then
  if target_parent:get_guid() == source_parent:get_guid() then
    -- Same container: use LOCAL index
  else
    -- Different containers: use GLOBAL index
  end
end
```

### How to Get Local Index

Iterate container children, find by GUID, use position:

```lua
if target_parent then
  local children = target_parent:get_container_children()
  local source_guid = source_fx:get_guid()
  
  for i, child in ipairs(children) do
    if child:get_guid() == source_guid then
      local local_index = i - 1  -- Convert to 0-based
      -- Use local_index for plink.effect
      break
    end
  end
end
```

### Real Bug Story

In SideFX, we encountered a bug where parameter links were created successfully (all API calls returned true), but modulation didn't work. The issue was:

**Before fix:**
- Used global encoded index: `plink.effect = 33554439` (0x2000000 + offset)
- Links were created, but REAPER couldn't find the source FX

**After fix:**
- Detected same container, found local position: `plink.effect = 2`
- Modulation worked correctly

**Root cause**: When FX are in the same container, REAPER expects the local position (0, 1, 2...) not the encoded global index.

## Creating Links

### Step-by-Step Process

1. **Store GUIDs** (indices change when FX move)
2. **Move FX if needed** (e.g., move modulator into target's container)
3. **Re-find FX by GUID** (indices have changed)
4. **Determine index type** (local vs global)
5. **Create plink parameters**

### Example: Creating a Parameter Link

```lua
-- 1. Store GUIDs before any operations
local source_guid = source_fx:get_guid()
local target_guid = target_fx:get_guid()

-- 2. Move source into target's container if needed
local target_parent = target_fx:get_parent_container()
if target_parent then
  -- Move source FX into the container
  target_parent:add_fx_to_container(source_fx)
end

-- 3. Re-find FX by GUID (indices changed after move)
local source_fx = track:find_fx_by_guid(source_guid)
local target_fx = track:find_fx_by_guid(target_guid)

-- 4. Determine plink effect index
local plink_effect_idx = source_fx.pointer  -- Default to global

if target_parent then
  local source_parent = source_fx:get_parent_container()
  
  -- Check if same container
  if source_parent and source_parent:get_guid() == target_parent:get_guid() then
    -- Find local position
    local children = target_parent:get_container_children()
    for i, child in ipairs(children) do
      if child:get_guid() == source_guid then
        plink_effect_idx = i - 1  -- Use local index
        break
      end
    end
  end
end

-- 5. Create the link
local plink_prefix = string.format("param.%d.plink.", target_param_idx)

reaper.TrackFX_SetNamedConfigParm(track, target_fx_idx, plink_prefix .. "active", "1")
reaper.TrackFX_SetNamedConfigParm(track, target_fx_idx, plink_prefix .. "effect", tostring(plink_effect_idx))
reaper.TrackFX_SetNamedConfigParm(track, target_fx_idx, plink_prefix .. "param", tostring(source_param_idx))
reaper.TrackFX_SetNamedConfigParm(track, target_fx_idx, plink_prefix .. "scale", tostring(scale or 1.0))
```

### Using ReaWrap's High-Level API

ReaWrap provides a convenient method that handles all this:

```lua
local fx = TrackFX:new(track, target_fx_idx)
local success = fx:create_param_link(source_fx, source_param_idx, target_param_idx, scale)
```

This method automatically:
- Detects same container
- Finds local index
- Creates all plink parameters
- Returns boolean success

## Reading Links

### Check if Link Exists

```lua
local plink_prefix = string.format("param.%d.plink.", param_idx)
local active = reaper.TrackFX_GetNamedConfigParm(track, fx_idx, plink_prefix .. "active")

if active == "1" then
  -- Link is active
end
```

### Read Link Information

```lua
local plink_prefix = string.format("param.%d.plink.", param_idx)

local active = reaper.TrackFX_GetNamedConfigParm(track, fx_idx, plink_prefix .. "active")
local effect = reaper.TrackFX_GetNamedConfigParm(track, fx_idx, plink_prefix .. "effect")
local param = reaper.TrackFX_GetNamedConfigParm(track, fx_idx, plink_prefix .. "param")
local scale = reaper.TrackFX_GetNamedConfigParm(track, fx_idx, plink_prefix .. "scale")

if active == "1" then
  local effect_idx = tonumber(effect)
  local param_idx = tonumber(param)
  local scale_val = tonumber(scale) or 1.0
  
  -- Use the link information
end
```

### Using ReaWrap

```lua
local fx = TrackFX:new(track, fx_idx)
local link_info = fx:get_param_link_info(param_idx)

if link_info then
  -- link_info = { active = true, effect = 2, param = 0, scale = 1.0 }
  local source_fx_idx = link_info.effect
  local source_param = link_info.param
end
```

## Removing Links

### Raw API

```lua
local plink_prefix = string.format("param.%d.plink.", param_idx)
reaper.TrackFX_SetNamedConfigParm(track, fx_idx, plink_prefix .. "active", "0")
```

### ReaWrap

```lua
local fx = TrackFX:new(track, fx_idx)
fx:remove_param_link(param_idx)
```

## Common Pitfalls

1. **Forgetting to re-find FX after moves**: Always use GUIDs and re-find after structural changes
2. **Using global index for same-container FX**: Always check container relationship first
3. **Not converting numbers to strings**: plink values must be strings
4. **Assuming indices are stable**: FX indices change when FX are moved - always use GUIDs

## Real-World Example: SideFX Modulator

From `SideFX/lib/modulator.lua`:

```lua
-- After moving modulator into target's container
local mod_fx_idx = mod_fx_obj.pointer
local target_fx_idx = target_fx_obj.pointer

-- Determine plink effect index
local plink_effect_idx = mod_fx_idx  -- Default to global

if target_parent then
  -- Both FX are now in the same container - find modulator's LOCAL position
  local children = target_parent:get_container_children()
  local mod_guid = mod_fx_obj:get_guid()
  
  for i, child in ipairs(children) do
    if child:get_guid() == mod_guid then
      plink_effect_idx = i - 1  -- Convert to 0-based index
      break
    end
  end
end

-- Create the parameter link
local plink_prefix = string.format("param.%d.plink.", target_param_idx)

reaper.TrackFX_SetNamedConfigParm(track, target_fx_idx, plink_prefix .. "active", "1")
reaper.TrackFX_SetNamedConfigParm(track, target_fx_idx, plink_prefix .. "effect", tostring(plink_effect_idx))
reaper.TrackFX_SetNamedConfigParm(track, target_fx_idx, plink_prefix .. "param", tostring(M.MOD_OUTPUT_PARAM))
```

This pattern ensures modulation works correctly for nested FX in containers.

