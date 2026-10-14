## Summary

<!-- Backstage voice: What does this PR do technically? -->

## Changes

<!-- List specific files changed and why -->
-
-

## Related Issues

<!-- Link issues this closes: Closes #XX -->

## Testing

<!-- How did you verify this works? -->
- [ ] Unit tests pass (`make test-fast`)
- [ ] Linter passes (`make lint`)
- [ ] Type checker passes (`make type-check`)
- [ ] Manual test (if applicable): describe what you tested

## Bee Impact

<!-- If adding/modifying bees, complete this section -->
- **Bee(s) affected**:
- **Honeycomb keys read**:
- **Honeycomb keys written**:
- **Constitutional Gateway**: Does this action pass governance checks?

## Deployment Notes

<!-- Any env vars, config changes, or migration steps required? -->

## Checklist

- [ ] Code follows the [stigmergy pattern](../hive/bees/base_bee.py) (no direct bee-to-bee communication)
- [ ] Tool outputs are JSON (not Python code blocks)
- [ ] Type hints added for all new public functions
- [ ] Docstrings in Google style for all public functions
- [ ] No secrets committed (check with `detect-secrets`)
- [ ] `SWARM_ROLES.md` updated if adding a new bee
- [ ] `hive/config.json` updated if registering a new bee
