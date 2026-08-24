# Acceptance Criteria

## AC-1 Skill selection
Given the `skills/` folder contains one or more skill directories with `SKILL.md`, when the operator opens the app, then they can see and select those skills.

## AC-2 Existing project directory
Given a directory exists under the configured browse root, when the operator browses and selects it, then a session is bound to that path.

## AC-3 New project directory
Given a parent path under the browse root, when the operator creates a new folder name, then that directory is created and can be used as the project root.

## AC-4 Interview then BRD
Given a selected skill (business-requirement-analysis) and project, when the operator describes a business need, then the assistant interviews in rounds of several questions and can produce a BRD matching the skill template.

## AC-5 Persist BRD
Given a generated BRD, when the operator saves or approves, then the file is written to `<project-root>/docs/BRD-<Feature-Name>.md`.

## AC-6 Provider
Given `OPENROUTER_API_KEY` is set, when a chat turn runs, then the app calls OpenRouter using `deepseek/deepseek-v4-flash`.
