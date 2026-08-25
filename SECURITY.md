# Security policy

## Scope

`contrib-lint` is an offline, read-only repository hygiene checker. It reads selected text files under the path supplied by the user and does not execute project code, install project dependencies, clone repositories, or make network requests.

## Reporting a vulnerability

Please do not include secrets or exploit details in a public issue. Open a private security report through GitHub's security advisory workflow for this repository, or contact the repository maintainer through the email listed on the maintainer's GitHub profile.

## Limitations

The linter is not a sandbox and should not be treated as a security boundary. A malicious local repository could still exploit vulnerabilities in the Python runtime or dependencies used to invoke the tool. Run it with ordinary user privileges and keep Python and packaging tools updated.
