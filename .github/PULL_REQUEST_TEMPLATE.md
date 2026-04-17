## Summary

<!-- One-paragraph description of what this PR does and why. -->

## Checklist

- [ ] `./scripts/validate.sh` passes locally
- [ ] Each new or modified plugin has an entry in `.claude-plugin/marketplace.json`
- [ ] Plugin directory name is kebab-case (e.g. `my-plugin`, not `MyPlugin` or `my_plugin`)
- [ ] Plugin version is set in `plugin.json` (not in `marketplace.json`)
- [ ] If this introduces a significant architectural decision: an ADR has been added to `adr/`
- [ ] PR diff is under 1 000 lines — or a split has been discussed and agreed in the issue/comments
- [ ] Docs updated if the change affects how users install or author plugins

## Test plan

<!-- How was this tested? e.g. ran `/plugin marketplace add ./` and `/plugin install <name>@olivier-vault` locally -->
