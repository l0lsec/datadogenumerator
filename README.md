# Datadog API Key Enumerator

A security reconnaissance tool that enumerates what resources and data a Datadog API key has access to. Useful for security assessments, penetration testing, and validating the principle of least privilege on Datadog API credentials.

## Features

- **API Key Validation** - Confirms the API key is valid
- **Organization Discovery** - Retrieves org name, public ID, and creation date
- **User Enumeration** - Lists all users in the organization
- **Key Management** - Enumerates API keys and Application keys
- **Infrastructure** - Lists hosts, metrics, and dashboards
- **Monitoring** - Discovers monitors, SLOs, downtimes, and events
- **Logs & APM** - Checks access to log indexes, pipelines, and APM services
- **Security** - Tests access to security monitoring rules and signals
- **Integrations** - Probes AWS, Azure, GCP, Slack, PagerDuty, and webhook configs
- **Additional Resources** - Notebooks, Synthetics tests, RUM applications, roles & permissions

## Installation

```bash
git clone https://github.com/yourusername/datadogenumerator.git
cd datadogenumerator
pip install requests
```

## Usage

### Basic Usage

```bash
# With API key only
python3 datadog_enum.py <API_KEY>

# With API key and Application key (recommended for full enumeration)
python3 datadog_enum.py <API_KEY> <APP_KEY>

# Specify a region
python3 datadog_enum.py <API_KEY> <APP_KEY> --region eu
```

### Environment Variables

You can also set credentials via environment variables:

```bash
export DD_API_KEY="your_api_key"
export DD_APP_KEY="your_app_key"
python3 datadog_enum.py
```

### Supported Regions

| Region | Flag | API Endpoint |
|--------|------|--------------|
| US1 (default) | `--region us1` | api.datadoghq.com |
| US3 | `--region us3` | api.us3.datadoghq.com |
| US5 | `--region us5` | api.us5.datadoghq.com |
| EU | `--region eu` | api.datadoghq.eu |
| AP1 | `--region ap1` | api.ap1.datadoghq.com |

## Example Output

```
╔═══════════════════════════════════════════════════════════╗
║          DATADOG API KEY ENUMERATION TOOL                 ║
╚═══════════════════════════════════════════════════════════╝
[i] Using API endpoint: https://api.datadoghq.com

============================================================
VALIDATING API KEY
============================================================
[✓] API Key Validation: ACCESSIBLE
[i]   → Confirms the API key is valid
[i]   Valid: True

============================================================
ORGANIZATION INFO
============================================================
[✓] Organization Details: ACCESSIBLE
[i]   → Organization settings and info
[i]   Name: Acme Corp
[i]   Public ID: abc123xyz
[i]   Created: 2020-01-15T00:00:00Z

============================================================
USERS
============================================================
[✓] List Users: ACCESSIBLE
[i]   → All users in the organization
[i]   Found 42 users
[i]     - admin@acme.com (active)
[i]     - dev@acme.com (active)
...
```

## Understanding Results

| Symbol | Meaning |
|--------|---------|
| `[✓]` Green | Endpoint accessible - API key has permission |
| `[✗]` Red | Forbidden (403) or Unauthorized (401) |
| `[!]` Yellow | Not Found (404) or other status |
| `[i]` Blue | Informational details |

## API Key vs Application Key

Datadog uses two types of keys:

- **API Key**: Required for submitting data to Datadog. Limited read access.
- **Application Key**: Required for reading data from Datadog APIs. Provides broader access when combined with an API key.

For comprehensive enumeration, provide both keys. With only an API key, many read operations will return 403 Forbidden.

## Security Considerations

⚠️ **This tool is intended for authorized security testing only.**

- Only use on Datadog organizations you have permission to test
- API keys and results may contain sensitive information
- Consider the scope and permissions before running in production environments

## Dependencies

- Python 3.6+
- `requests` library

## License

MIT License

## Contributing

Contributions welcome! Feel free to submit issues and pull requests.

