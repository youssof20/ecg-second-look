# Security

## Reporting vulnerabilities

Email security reports to the repository maintainer via the GitHub Security Advisories flow for this project when available. Include steps to reproduce and impact.

Do not file public issues for exploitable upload, path, or dependency vulnerabilities until a fix is ready.

## Clinical behavior

Unsafe clinical presentation — for example diagnostic wording, suppressed uncertainty, or implied clearance — is treated as a product defect. Report it with the label `clinical-safety` or through the same private channel.

## Upload handling (when Second Look lands)

Planned controls: file-size limits, image-decoding validation that does not trust filenames or browser MIME headers, local processing by default, and no upload retention by default.
