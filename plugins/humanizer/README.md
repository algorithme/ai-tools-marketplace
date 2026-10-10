# Humanizer

Edit prose to sound more natural using 25 writing patterns. The skill produces
a draft rewrite, a brief audit of remaining patterns, and a final rewrite.
Its guidance covers inflated claims, promotional language, vague attribution,
repetitive phrasing, formatting habits, filler, and hedging.

One [SKILL.md](./skills/humanizer/SKILL.md) supplies the instructions for every
host. The plugin has no hooks, scripts, MCP servers, or runtime dependencies.

## Compatibility

| Host | How to use it |
|---|---|
| Claude Code | Install the marketplace plugin and invoke `/humanizer:humanizer`. |
| Codex | Install the marketplace plugin and select Humanizer with `/skills` or `$humanizer`. |
| Claude / Cowork | Use a Claude marketplace available to your account, or upload the standalone skill. |
| ChatGPT and other chat assistants | Attach the skill file or paste its body and explicitly ask the assistant to follow it. This is manual reuse. |
| Other hosts supporting Agent Skills | Copy the `skills/humanizer/` folder into the host's documented skill location. |

## Claude Code

```bash
claude plugin marketplace add omorel/ai-tools-marketplace
claude plugin install humanizer@olivier-vault
```

In a session, use `/humanizer:humanizer` followed by the text to edit, or ask
Claude to humanize your writing. To update an existing installation:

```bash
claude plugin marketplace update olivier-vault
claude plugin update humanizer@olivier-vault
```

Restart the session after updating. From a local checkout of this repository,
use `claude plugin marketplace add ./` instead of the GitHub source.

## Codex

Use a Codex version with plugin support:

```bash
codex plugin marketplace add omorel/ai-tools-marketplace
codex plugin add humanizer@olivier-vault
```

Select Humanizer through `/skills`, mention `$humanizer`, or ask naturally:
"Humanize this paragraph while preserving its meaning and tone: ..."

To update a Git marketplace installation:

```bash
codex plugin marketplace upgrade olivier-vault
codex plugin add humanizer@olivier-vault
```

Start a new session after installation or update. For a local checkout, use
`codex plugin marketplace add ./`. The two manifests share the same skill
directory using the supported [Codex compatibility layout](https://developers.openai.com/plugins/build/plugins).

## Claude and Cowork

If this marketplace is available in your account, select Humanizer in
Customize > Plugins and add it. Account-installed plugin skills are available
in chat and Cowork; see [Claude's plugin directory guide](https://support.claude.com/en/articles/14328846-browse-skills-connectors-and-plugins-in-one-directory).

For organization distribution, Team/Enterprise owners can sync a marketplace
through Organization settings > Plugins & skills. Both Cowork and Skills must
be enabled. GitHub organization sync requires a private or internal repository;
use an organization copy of the marketplace for that route. See
[organization marketplace setup](https://support.claude.com/en/articles/13837433-manage-plugins-for-your-organization).

For a personal custom skill, take only the `skills/humanizer/` folder from this
plugin. Claude's upload flow requires you to compress that folder locally,
with `humanizer/SKILL.md` inside the archive, then choose Customize > Skills >
Create skill > Upload a skill. Enable it and ask Claude to humanize your text.
This repository stores the unpacked source; it provides no ZIP artifacts.

Custom-skill upload requires code execution/file creation and Skills to be
enabled, subject to your account and organization controls. Follow
[Claude's skill instructions](https://support.claude.com/en/articles/12512180-use-skills-in-claude)
and [archive layout guide](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills).

## ChatGPT and other assistants

For manual use, download [SKILL.md](./skills/humanizer/SKILL.md), attach it to
the conversation, and explicitly request:

> Use the attached Humanizer skill as editing guidance for the text below.
> Preserve its meaning and tone. Text: ...

If file attachments are unavailable, paste the Markdown body after the closing
YAML frontmatter delimiter, then provide the same request and your text.
Attaching a file supplies guidance for that conversation; it does not install
a persistent skill or publish this plugin to ChatGPT's directory.

For a host with native Agent Skills support, copy the entire `skills/humanizer/`
folder into its documented skill directory and use that host's discovery and
invocation flow. For example, Codex supports repository-local
`.agents/skills/humanizer/SKILL.md`; see its [skill location guide](https://learn.chatgpt.com/docs/build-skills).
Choose either standalone installation or the marketplace plugin to avoid
duplicate skill entries. Replace the copied folder when updating it.

## Source and versions

Marketplace package version: **1.0.0**. Supplied skill version: **2.3.0**,
preserved as `metadata.version` in the skill frontmatter.

Imported from the user-provided `humanizer-v1.zip`. Only the skill metadata was
adapted: the Claude-specific `allowed-tools` list was removed, and the source
version moved into `metadata`. The Markdown body is unchanged.

Writing-pattern source:
[Wikipedia:Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing),
maintained by WikiProject AI Cleanup. The supplied archive does not identify
the skill’s author or include a license; the manifests leave those fields unset.
