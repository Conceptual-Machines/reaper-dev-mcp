# FX Container System

## Container Pointers

### Track-Level FX
- Direct indices: `0, 1, 2, 3, ...`
- First FX on track = index `0`
- Second FX on track = index `1`
- etc.

### Container Children
- Encoded indices: `0x2000000 + local_index`
- First child in container = `0x2000000 + 0`
- Second child in container = `0x2000000 + 1`
- etc.

### Nested Containers
- Multiple levels of encoding: `0x2000000 + (0x2000000 + ...)`
- Each nesting level adds complexity to the index calculation

## Pointer Refresh

### The Problem

**FX indices are NOT stable**. When FX are moved between containers or reordered, their indices change. This means:

- Storing an FX index and using it later will fail
- After moving FX, you must re-find them
- Container operations invalidate all stored indices

### The Solution: GUIDs

**Always use GUIDs for stable identification:**

```lua
-- Before any operations
local fx_guid = fx:get_guid()

-- Perform operations (moves, adds, etc.)
container:add_fx_to_container(fx)

-- Re-find by GUID (index has changed!)
local fx = track:find_fx_by_guid(fx_guid)
```

### When to Refresh

Refresh pointers after:
- Moving FX into/out of containers
- Reordering FX
- Adding/removing FX
- Any container structural changes

## Adding FX to Containers

### Step-by-Step Process

1. **Create FX at track level first**
2. **Store GUID** (stable identifier)
3. **Move into container**
4. **Re-find by GUID** (pointer changed)

### Example

```lua
-- 1. Create FX at track level
local fx = track:add_fx_by_name("JS: My Plugin", false, -1)

-- 2. Store GUID
local fx_guid = fx:get_guid()

-- 3. Move into container
container:add_fx_to_container(fx)

-- 4. Re-find by GUID (pointer changed!)
local fx = track:find_fx_by_guid(fx_guid)

-- Now fx.pointer is the new encoded index
```

### ReaWrap Method

ReaWrap's `add_fx_to_container` handles this internally, but you still need to re-find if you're keeping references:

```lua
local fx_guid = fx:get_guid()
container:add_fx_to_container(fx)

-- Re-find to get updated pointer
fx = track:find_fx_by_guid(fx_guid)
```

## Parent/Child Navigation

### Get Parent Container

```lua
local parent = fx:get_parent_container()
if parent then
  -- FX is nested in a container
  local parent_guid = parent:get_guid()
else
  -- FX is at track level
end
```

### Get Container Children

```lua
if container:is_container() then
  local children = container:get_container_children()
  -- Returns array of TrackFX objects (1-indexed Lua array)
  
  for i, child in ipairs(children) do
    local child_guid = child:get_guid()
    local local_index = i - 1  -- Convert to 0-based
    -- Use local_index for plink API when both FX are in same container
  end
end
```

### Check if Container

```lua
if fx:is_container() then
  local child_count = fx:get_container_child_count()
  -- Work with container
end
```

## Safe Container Manipulation Patterns

### Pattern 1: Moving Multiple FX

```lua
-- Collect GUIDs first (indices will change)
local guids = {}
for fx in helpers.iter(fx_list) do
  guids[#guids + 1] = fx:get_guid()
end

-- Create container
local container = track:create_container()

-- Re-find and move each FX
for guid in helpers.iter(guids) do
  local fx = track:find_fx_by_guid(guid)
  if fx then
    container:add_fx_to_container(fx)
  end
end
```

### Pattern 2: Finding FX After Structural Changes

```lua
-- Store GUID before operations
local fx_guid = fx:get_guid()

-- Perform operations that might change indices
container:add_fx_to_container(fx)
-- ... other operations ...

-- Always re-find by GUID
local fx = track:find_fx_by_guid(fx_guid)
if not fx then
  error("FX not found after operations")
end

-- Now safe to use fx.pointer
```

### Pattern 3: Checking Container Relationships

```lua
local target_parent = target_fx:get_parent_container()
local source_parent = source_fx:get_parent_container()

if target_parent and source_parent then
  -- Both are in containers
  if target_parent:get_guid() == source_parent:get_guid() then
    -- Same container: use local indices for plink
  else
    -- Different containers: use global indices
  end
elseif target_parent then
  -- Only target is in container
  -- Use global index for source
elseif source_parent then
  -- Only source is in container
  -- Use global index
else
  -- Both at track level
  -- Use direct indices
end
```

## Container Depth and Hierarchy

### Get Container Depth

```lua
local depth = fx:get_container_depth()
-- Returns 0 for track-level FX
-- Returns 1 for FX in top-level container
-- Returns 2 for FX in nested container, etc.
```

### Walk Up Hierarchy

```lua
local current = fx
while current do
  local parent = current:get_parent_container()
  if parent then
    -- Process parent
    current = parent
  else
    break  -- Reached track level
  end
end
```

## Common Pitfalls

1. **Using stale pointers**: Always re-find FX by GUID after structural changes
2. **Assuming indices are stable**: They're not - use GUIDs
3. **Forgetting to check container relationship**: Critical for plink API
4. **Not handling nested containers**: Each level adds encoding complexity
5. **Mixing local and global indices**: Know which to use when

## Real-World Example: SideFX Device System

SideFX uses containers (D{n}) that contain plugins and utilities:

```lua
-- Create device container
local device = track:create_container()

-- Add utility FX
local utility = track:add_fx_by_name("JS: SideFX_Utility", false, -1)
local utility_guid = utility:get_guid()

-- Move into device
device:add_fx_to_container(utility)

-- Re-find (pointer changed)
utility = track:find_fx_by_guid(utility_guid)

-- Now utility.pointer is encoded (0x2000000 + local_index)
```

When creating parameter links between FX in the same device container, SideFX uses local indices:

```lua
-- Both FX are in same container
local children = device:get_container_children()
for i, child in ipairs(children) do
  if child:get_guid() == source_guid then
    local local_index = i - 1
    -- Use local_index for plink.effect
  end
end
```

This ensures parameter modulation works correctly for nested FX.

