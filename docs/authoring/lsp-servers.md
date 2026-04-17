# LSP servers

Plugins can configure [Language Server Protocol](https://microsoft.github.io/language-server-protocol/) (LSP) servers to give Claude real-time code diagnostics, go-to-definition, and hover information while editing.

Upstream reference: [code.claude.com/docs/en/plugins-reference#lsp-servers](https://code.claude.com/docs/en/plugins-reference)

## Important

**LSP plugins configure how Claude Code connects to a language server — they do not bundle the server binary.** Users must install the language server separately before the plugin will work. Document this requirement clearly in your plugin's README.

## File location

```
plugins/my-plugin/
└── .lsp.json
```

Or inline in `plugin.json` via `lspServers`.

## .lsp.json format

```json
{
  "my-language": {
    "command": "my-language-server",
    "args": ["--stdio"],
    "extensionToLanguage": {
      ".myl": "my-language"
    }
  }
}
```

## Required fields

| Field | Description |
|---|---|
| `command` | Binary name or path. Must be in `$PATH` on the user's machine. |
| `extensionToLanguage` | Maps file extensions to language identifiers. |

## Optional fields

| Field | Default | Description |
|---|---|---|
| `args` | `[]` | Command-line arguments. |
| `transport` | `stdio` | `stdio` or `socket`. |
| `env` | — | Environment variables. |
| `initializationOptions` | — | Passed to the server on init. |
| `settings` | — | Sent via `workspace/didChangeConfiguration`. |
| `startupTimeout` | — | Max ms to wait for server startup. |
| `shutdownTimeout` | — | Max ms for graceful shutdown. |
| `restartOnCrash` | — | Auto-restart if the server crashes. |
| `maxRestarts` | — | Maximum restart attempts. |

## Example: TypeScript LSP plugin

`.lsp.json`:

```json
{
  "typescript": {
    "command": "typescript-language-server",
    "args": ["--stdio"],
    "extensionToLanguage": {
      ".ts": "typescript",
      ".tsx": "typescriptreact",
      ".js": "javascript",
      ".jsx": "javascriptreact"
    }
  }
}
```

`README.md` must include:

```markdown
## Prerequisites
Install the TypeScript language server before enabling this plugin:
```bash
npm install -g typescript-language-server typescript
```
```

## Official marketplace

Before building an LSP plugin, check whether one already exists on the official Claude marketplace. Official plugins exist for Python (Pyright), TypeScript, and Rust (rust-analyzer).
