# Agent Skills

Reusable Agent Skills for `vpx skills` and skills.sh-compatible clients.

## Skills

| Skill | Description |
|-------|-------------|
| `conventional-commits` | Write, review, and improve Git commit messages following Conventional Commits 1.0.0. |

## Install

- List available skills: `vpx skills add iashc/skills --list`
- Install one skill: `vpx skills add iashc/skills --skill conventional-commits`
- Install all skills: `vpx skills add iashc/skills --all`

## Development

- Install dependencies: `vp install`
- Format files: `vp run format`
- Validate local skill discovery: `vpx skills add . --list`

## License

MIT
