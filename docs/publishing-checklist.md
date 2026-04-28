# Publishing Checklist

Use this checklist before publishing an AI workspace governance repo.

## Must Remove

- Real client or business names.
- Personal documents.
- Raw PDFs, spreadsheets, and Word documents.
- API keys and credentials.
- Generated outputs.
- Run artifacts.
- Local path references that reveal private folder names.

## Should Generalize

- Project names.
- Pipeline names.
- Example data.
- Rule examples.
- Directory paths.
- Commit examples.

## Should Keep

- The scanner.
- Generic rule configuration.
- Operating model.
- Commit decision rules.
- Templates.
- Sanitized examples.
- Tests.

## Final Checks

Run:

```powershell
git status --short
python .\workspace_guard\scan.py --root .
```

Search for private markers:

```powershell
git grep -n "client\|secret\|password\|api_key\|C:\\Users"
```

Review all `REVIEW` and `BLOCK` findings before pushing.

