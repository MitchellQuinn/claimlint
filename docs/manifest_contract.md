# Manifest Contract

The input manifest selects the audit corpus. ClaimLint v0.1 does not perform broad repository crawling outside manifest-selected files.

Supported include entries:

- `path`: explicit repository-relative path.
- `glob`: repository-relative glob.
- `role`: corpus role used for retrieval boosts and reporting.

Supported exclude entries:

- `glob`: repository-relative glob to ignore.

Supported limits:

- `max_file_bytes`
- `max_total_files`

Missing explicit paths are recorded as manifest warnings. If all selected inputs are missing or unsupported, the CLI exits with manifest validation failure.

