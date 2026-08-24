# Output Format

After the interview has completed:

1. Generate a complete Business Requirements Document.
2. Generate it as a standalone Markdown document.
3. Never summarize the interview instead of producing the document.
4. Save the document inside:

`<project-root>/docs/`

Use the filename:

`BRD-<Feature-Name>.md`

Examples:

* BRD-Visitor-Management.md
* BRD-QR-Code-Scanning.md
* BRD-Leave-Approval.md

Create the docs directory if it does not exist.

After saving the file:

* inform the stakeholder
* display the filename
* display the full file path

Then ask:

1. Approve BRD
2. Modify BRD
3. Add More Requirements

Wait for explicit approval.

If the stakeholder approves:

* confirm approval
* do not regenerate the BRD
* do not continue automatically
* wait for the next instruction

The approved BRD becomes the source of truth for all later SDLC stages.

