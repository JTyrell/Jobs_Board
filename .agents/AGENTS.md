# Jobs Board — Agent Rules

## Command Chaining: NEVER use `&&`

- **NEVER** chain shell commands together using `&&`. This applies universally:
  - Local PowerShell terminals
  - Railway `buildCommand` / `startCommand` in `railway.json`
  - Any other shell context
- `&&` does not work reliably across environments in this project.
- Instead, use a **shell script** (`.sh`) with each command on its own line, and invoke it as a single command.
- Example of what **NOT** to do: `cd SonaJobs && pip install -r requirements.txt`
- Example of what **TO DO**: create a `railway-build.sh` file and reference it as `bash SonaJobs/railway-build.sh`
