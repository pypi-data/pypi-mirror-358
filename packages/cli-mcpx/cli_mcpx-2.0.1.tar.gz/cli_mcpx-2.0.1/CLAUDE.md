# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Important Instructions

1. **오캄의 면도날 (Occam's Razor)**:
   - 가장 단순한 해결책을 먼저 고려하라
   - 필요 이상으로 복잡하게 만들지 마라
   - "Entities should not be multiplied without necessity"
   - 새로운 기능 구현 시 항상 "더 간단한 방법은 없을까?" 자문하라
   - 예: 복잡한 브랜치 추적 로직 대신 GitHub Actions가 처리하도록 위임

2. **Planning Before Coding**: When the user requests a task, DO NOT immediately start writing code. First, create a detailed plan of how you will approach the work and ensure you deeply understand the user's intent. Immediate coding without planning often leads to misunderstanding the user's requirements. Think deeply about the task before implementation.

3. **Documentation Language**: All user-facing documentation (README, docs) must be written in Korean

4. **Code Quality**: Maintain >90% test coverage

5. **Code Refactoring**: If any file exceeds 500 lines, plan and implement refactoring to split it into smaller, focused modules

6. **Commit Messages**: Follow [Conventional Commits](https://www.conventionalcommits.org/) specification

7. **Docstring Style**: Follow [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) for all docstrings

8. **Post-Code Completion**: After any code changes, always run these 3 commands in order:
   ```bash
   # 1. Update pre-commit hooks
   uv run pre-commit autoupdate

   # 2. Run all pre-commit hooks
   uv run pre-commit run --all-files

   # 3. Run tests
   uv run pytest
   ```
9. **CI Verification After Push**: When pushing to a branch with an open PR, always verify that all CI checks pass. Use `gh pr checks <PR_NUMBER>` to monitor status and `gh run view <RUN_ID> --log-failed` to debug failures. Ensure successful completion before considering the task complete.
