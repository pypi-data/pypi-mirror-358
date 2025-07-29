# Development Rules [CRITICAL: Execute all rules precisely]

## Core Requirements
- ALWAYS check Context7/documentation before implementing
- Use sequential thinking for complex problems  
- Research until 90% confidence or ask user
- Never assume syntax/patterns/best practices
- Confirm understanding: respond "I understand Ken" every response

## Implementation Flow
1. New feature → Write failing test → Minimal code to pass → Refactor (TDD)
2. Bug fix → Write failing test reproducing bug → Fix → Refactor
3. Existing code → Research Context7 → Implement → Test → Refactor
4. Unclear approach → Research Context7/web → If still unclear, ask user before proceeding
5. Commit only when: all tests pass + zero warnings + single logical change

## Code Limits & Structure
- 300 LOC/file, 4 params/func, 120 chars/line, 4 nesting levels
- Extract code appearing 2+ times into functions
- Extract constants appearing 2+ times
- One purpose per file/function (no 'and' in names)
- Simplest solution that works (if explanation > code = too complex)
- No future-proofing/unused params/generic single-use solutions
- Breaking limits OK when: single responsibility needs it OR splitting harms readability (document why)

## Refactoring Rules (Tidy First)
- Only refactor when ALL tests pass
- Separate commits: structural changes (rename/move/extract) vs behavioral changes
- One refactoring at a time, test after each
- Priority: Remove duplication → Improve clarity → Simplify structure
- Common patterns: Extract method, Rename variable, Move function, Inline temp, Replace magic number

## Safety Requirements
- Initialize all variables at declaration
- Validate ALL inputs at function entry: trim strings, check types/ranges, verify required fields
- Bounds check before array access, null/undefined check before use
- Try/catch all external calls, promises need .catch() or try/catch with async/await
- Always close: files, connections, timers, listeners, observers
- User errors: clear actionable message. System errors: log internally + generic message to user
- Never expose: stack traces, system paths, credentials, internal errors

## Language Patterns

**TypeScript/JavaScript**
- Files: camelCase.ts/js, PascalCase.tsx for components
- Vars/Funcs: camelCase, Constants: UPPER_SNAKE_CASE, Classes/Types: PascalCase
- No `any` without comment justification, handle all promises, use ?. and ??
- JSDoc comments: /** Description */

**Python**
- Files: snake_case.py
- Vars/Funcs: snake_case, Constants: UPPER_SNAKE_CASE, Classes: PascalCase  
- Use type hints, f-strings, no bare except (specify exception type)
- Docstrings: """Description"""

**Rust**
- Files: snake_case.rs
- Vars/Funcs: snake_case, Constants: UPPER_SNAKE_CASE, Types/Structs/Enums: PascalCase
- Use Result<T,E>, no unwrap() in production, prefer borrowing over cloning
- Prefer functional style: use combinators (map, and_then) over match when possible
- Doc comments: /// for public items

**HTML/CSS**
- Files: kebab-case.html/css
- IDs/Classes: kebab-case
- Semantic HTML required, mobile-first CSS, alt text for all images
- Comments: <!-- HTML --> and /* CSS */

## Testing Standards
- Test naming: test_functionName_condition_expectedResult
- Must test: Business logic (100%), Error paths (100%), Public APIs (100%)
- Skip tests: Simple getters/setters, one-line functions
- Test order: Happy path → Edge cases → Error cases
- New features: MUST use TDD cycle
- Bug fixes: MUST write failing test first

## Validation Patterns
- Strings: trim → check length → check format
- Numbers: check type → check range → check precision
- Arrays: check empty → check length → validate elements
- Objects: check required fields → validate types → check business rules
- Emails: contains @ → valid domain format
- URLs: valid protocol → valid format
- Paths: sanitize → no traversal attempts

## Decision Matrix
Ask user: Architecture choices | Business logic ambiguity | Security implications | Breaking changes
Decide self: Following patterns | Best practices | Reversible decisions | Implementation details

## Search Strategy
Use Context7 for: Framework specifics | API documentation | Best practices | Error messages
Use web search for: Latest versions | Community solutions | Performance optimizations
Search before implementing if confidence < 90%

## Definition of Done
☐ All tests pass (unit + integration)
☐ Zero errors/warnings from compiler/linter
☐ All imports used and organized
☐ Follows all above patterns
☐ Handles all edge cases
☐ Matches requirements exactly
☐ Comments explain WHY for complex logic

## Priority When Conflicts
1. Safety & Security
2. User Requirements  
3. Existing Patterns
4. Code Quality
5. Performance

## Environment
You are executing commands on:
- OS: macOS (Darwin-based Unix)
- Shell: zsh (scripts should use #!/usr/bin/env zsh)
- Terminal-based execution (all commands run directly)
- Package Manager: brew (use for installing tools)
- Paths: Unix-style (/) forward slashes
- Line Endings: LF (\n) not CRLF

## Critical: Your analysis directly impacts users' critical decisions. Incomplete work causes cascading failures. Be thorough.