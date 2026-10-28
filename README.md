# Agent Skills

Reusable Agent Skills for `vpx skills` and skills.sh-compatible clients.

## Skills

| Skill                    | Description                                                                        |
| ------------------------ | ---------------------------------------------------------------------------------- |
| `agents-guide`           | Create, review, shorten, migrate, and organize `AGENTS.md` and `CLAUDE.md` files.  |
| `code-explainer`         | Explain code with visual diagrams and analogies.                                   |
| `conventional-commits`   | Write and review Conventional Commit messages and pull request titles.             |
| `frontend-design`        | Build, redesign, and visually review frontend experiences.                         |
| `technical-doc-rewriter` | Rewrite and review technical documents in simplified technical English or Chinese. |

## Install

- List available skills: `vpx skills add iashc/skills --list`
- Install one skill: `vpx skills add iashc/skills --skill <skill-name>`
- Install all skills: `vpx skills add iashc/skills --all`

## Development

- Install dependencies: `vp install`
- Format files: `vp run format`
- Validate local skill discovery: `vpx skills add . --list`

## License

MIT
