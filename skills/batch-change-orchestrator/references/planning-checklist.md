# Planning Checklist

## Use this skill only if most answers are yes
- Can the work be split into independent units?
- Is the change mostly mechanical or policy-driven?
- Can each unit be verified locally?
- Will parallel execution reduce total time meaningfully?
- Can failures be isolated without poisoning the whole migration?

## Good fits
- bulk rename
- repeated API migration
- codemod + cleanup
- repetitive config normalization
- many-file formatting or pattern replacement

## Bad fits
- architecture redesign with strong coupling
- tasks needing frequent human steering mid-flight
- work that depends on a single shared mutable branch/state
- unclear verification criteria

## Minimum per-unit metadata
- label
- scope
- exact goal
- expected artifacts
- verification path
- failure fallback