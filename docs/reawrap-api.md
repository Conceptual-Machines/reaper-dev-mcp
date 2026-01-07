# ReaWrap API Reference

## Object Model Overview

ReaWrap provides an object-oriented wrapper around REAPER's ReaScript API, making it easier to work with tracks, FX, items, and takes.

### Core Classes

- **Track**: Represents a media track
- **TrackFX**: Represents an FX on a track
- **Item**: Represents a media item
- **Take**: Represents a take within an item

### How Objects Work

Objects wrap REAPER pointers and provide:
- **GUID-based identification**: Stable across structural changes
- **Method chaining**: Convenient API
- **Automatic pointer management**: Handles stale pointers

### Creating Objects

```lua
local Track = require("track")
local TrackFX = require("track_fx")

-- Get track
local track = Track:new(reaper.GetTrack(0, 0))  -- First track

-- Get FX
local fx = TrackFX:new(track, 0)  -- First FX on track
```

## TrackFX Methods

### Standard Wrapped Methods

These wrap REAPER API functions with consistent return value patterns:

#### Parameter Access

```lua
-- Get parameter (returns min, max)
local min_val, max_val = fx:get_param(param_idx)

-- Get normalized parameter (0.0-1.0)
local value = fx:get_param_normalized(param_idx)

-- Set parameter (raw value)
fx:set_param(param_idx, raw_value)

-- Set normalized parameter
fx:set_param_normalized(param_idx, 0.5)  -- 50%
```

#### Named Config Parameters

```lua
-- Get named config param (returns string or nil)
local value = fx:get_named_config_param("param.0.plink.active")

-- Set named config param (value must be string)
fx:set_named_config_param("param.0.plink.active", "1")
```

**Important**: `get_named_config_param` returns a **single value** (string or nil), not a tuple.

#### FX Information

```lua
-- Get FX name
local name = fx:get_name()

-- Get GUID (stable identifier)
local guid = fx:get_guid()

-- Get number of parameters
local count = fx:get_num_params()

-- Get parameter name
local param_name = fx:get_param_name(param_idx)
```

### Custom High-Level Methods

ReaWrap adds convenient methods that handle complex operations:

#### Parameter Links

```lua
-- Create parameter link (handles local/global index automatically)
local success = fx:create_param_link(source_fx, source_param_idx, target_param_idx, scale)

-- Remove parameter link
fx:remove_param_link(target_param_idx)

-- Get parameter link info
local link_info = fx:get_param_link_info(target_param_idx)
-- Returns: { active = true, effect = 2, param = 0, scale = 1.0 } or nil
```

#### Container Operations

```lua
-- Check if container
if fx:is_container() then
  local child_count = fx:get_container_child_count()
  local children = fx:get_container_children()
end

-- Get parent container
local parent = fx:get_parent_container()

-- Move FX into container
container:add_fx_to_container(fx, position)

-- Move FX out of container
fx:move_out_of_container(position)
```

### Return Value Patterns

**ReaWrap methods return single values**, not tuples:

```lua
-- ReaWrap (single return)
local value = fx:get_named_config_param("param.0.plink.active")
-- value is string or nil

-- Raw ReaScript (tuple return)
local retval, buf = reaper.TrackFX_GetNamedConfigParm(track, fx_idx, "param.0.plink.active")
-- retval is boolean, buf is string
```

## Track Methods

### FX Enumeration

```lua
-- Get all FX on track
local fxs = track:get_track_fx_chain()
-- Returns array of TrackFX objects

-- Iterate over FX
for fx in track:iter_track_fx_chain() do
  local name = fx:get_name()
end

-- Get all FX including nested (flat list)
local all_fx = track:get_all_fx_flat()
-- Returns array of {fx: TrackFX, depth: number, is_container: boolean}
```

### Finding FX

```lua
-- Find FX by GUID (stable across moves)
local fx = track:find_fx_by_guid(guid)

-- Get FX by index
local fx = track:get_track_fx(fx_idx)
```

### Adding/Removing FX

```lua
-- Add FX by name
local fx = track:add_fx_by_name("JS: My Plugin", false, -1)

-- Delete FX
fx:delete()
```

### Container Operations

```lua
-- Create new container
local container = track:create_container(position)

-- Move FX into new container
local container = track:add_fx_to_new_container(fx_list)
```

## Important Notes

### Return Value Conventions

**Single values, not tuples:**
- `get_named_config_param()`: Returns `string|nil`
- `get_param_normalized()`: Returns `number`
- `get_name()`: Returns `string`

**No separate retval:**
- Methods throw errors on failure (use `pcall` if needed)
- Or return `nil` for optional values

### Pointer Refresh Requirements

**Always re-find FX after structural changes:**

```lua
-- Store GUID
local fx_guid = fx:get_guid()

-- Perform operations
container:add_fx_to_container(fx)

-- Re-find (pointer changed)
fx = track:find_fx_by_guid(fx_guid)
```

### When Objects Become Stale

FX objects become stale when:
- FX are moved between containers
- FX are reordered
- FX are added/removed
- Container structure changes

**Solution**: Always use GUIDs and re-find after operations.

### Container Index Handling

ReaWrap's `create_param_link` method automatically handles local vs global indices:

```lua
-- Automatically detects same container and uses local index
fx:create_param_link(source_fx, source_param_idx, target_param_idx, scale)
```

This is much easier than manually checking container relationships!

## Code Examples

### Example 1: Creating a Parameter Link

```lua
local Track = require("track")
local TrackFX = require("track_fx")

-- Get track and FX
local track = Track:new(reaper.GetTrack(0, 0))
local modulator = track:get_track_fx(0)  -- Modulator FX
local target = track:get_track_fx(1)     -- Target FX

-- Create link (handles local/global index automatically)
local success = target:create_param_link(modulator, 0, 5, 1.0)
-- Links modulator param 0 to target param 5 at 100% scale
```

### Example 2: Working with Containers

```lua
-- Create container
local container = track:create_container()

-- Add FX to container
local fx1 = track:add_fx_by_name("JS: Plugin1", false, -1)
local fx1_guid = fx1:get_guid()

container:add_fx_to_container(fx1)

-- Re-find (pointer changed)
fx1 = track:find_fx_by_guid(fx1_guid)

-- Check container relationship
local parent = fx1:get_parent_container()
if parent and parent:get_guid() == container:get_guid() then
  -- fx1 is in container
end
```

### Example 3: Finding All FX in Containers

```lua
-- Get all FX including nested
for fx_info in track:iter_all_fx_flat() do
  local fx = fx_info.fx
  local depth = fx_info.depth
  local is_container = fx_info.is_container
  
  print(string.format("FX: %s, Depth: %d, Container: %s", 
    fx:get_name(), depth, tostring(is_container)))
end
```

### Example 4: Reading Parameter Links

```lua
-- Get link info
local link_info = fx:get_param_link_info(param_idx)

if link_info then
  print(string.format("Link active: effect=%d, param=%d, scale=%.2f",
    link_info.effect, link_info.param, link_info.scale))
else
  print("No link on this parameter")
end
```

## Method Reference

### TrackFX Methods

#### Parameter Methods
- `get_param(param_idx)` → `min_val, max_val`
- `get_param_normalized(param_idx)` → `number`
- `set_param(param_idx, val)` → `boolean`
- `set_param_normalized(param_idx, value)` → `boolean`
- `get_param_name(param_idx)` → `string`
- `get_num_params()` → `number`

#### Named Config Methods
- `get_named_config_param(param_name)` → `string|nil`
- `set_named_config_param(param_name, value)` → `boolean`

#### Container Methods
- `is_container()` → `boolean`
- `get_container_child_count()` → `number`
- `get_container_children()` → `table` (array of TrackFX)
- `get_parent_container()` → `TrackFX|nil`
- `add_fx_to_container(fx, position)` → `boolean`

#### Link Methods
- `create_param_link(source_fx, source_param_idx, target_param_idx, scale)` → `boolean`
- `remove_param_link(target_param_idx)` → `boolean`
- `get_param_link_info(target_param_idx)` → `table|nil`

### Track Methods

#### FX Methods
- `get_track_fx(fx_idx)` → `TrackFX`
- `get_track_fx_chain()` → `table` (array of TrackFX)
- `iter_track_fx_chain()` → `function` (iterator)
- `find_fx_by_guid(guid)` → `TrackFX|nil`
- `add_fx_by_name(fx_name, rec_fx, instantiate)` → `TrackFX`

#### Container Methods
- `create_container(position)` → `TrackFX|nil`
- `add_fx_to_new_container(fx_list)` → `TrackFX|nil`
- `get_all_fx_flat()` → `table` (array of {fx, depth, is_container})
- `iter_all_fx_flat()` → `function` (iterator)

