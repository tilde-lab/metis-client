# Contributing Guidelines

Thank you for considering contributing to our open source application!
We welcome any and all contributions, and appreciate the time and effort
you put into making our project better.

## How to Contribute

1. Fork the project and create a new branch for your contribution.
2. Make your changes, ensuring that you follow our coding conventions.
3. Write tests for your changes, if applicable.
4. Submit a pull request with a clear and detailed description of your changes.

## Code Style

We use [The Black Code Style](https://black.readthedocs.io/en/stable/the_black_code_style/index.html).
`black` and `isort` are used as formatters.

## Code Linters

We use almost default configuration of [flake8](https://flake8.pycqa.org/)
and [pylint](https://pylint.readthedocs.io/).

## Type Annotations

Use them whenever possible.

## Tests

We use [pytest](https://docs.pytest.org/) framework for unit tests.
Coverage should be 100%.

## Commit Guidelines

We use [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)
for all of our commit messages. Please ensure that your commit messages follow
this format to help us keep track of changes more easily:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

The `type` field describes the kind of change that you are making,
such as `feat` for a new feature or `fix` for a bug fix.
The `scope` field is optional, and is used to specify the component of
the application that your change affects.
The `description` field should be a short, concise summary of the change.

For example:

```
feat(users): add user registration functionality

This commit adds the ability for users to create a new account on our application.

Closes #123
```

[Commitizen](https://commitizen-tools.github.io/commitizen/) tool (`cz commit`)
may be used as commit message wizard.

## Versioning

We use [Semantic Versioning](https://semver.org/) for all of our releases.
This means that our version numbers follow the format of major.minor.patch,
where:

- A `major` release indicates a breaking change that is
  not backwards compatible.
- A `minor` release adds new features or functionality in
  a backwards-compatible manner.
- A `patch` release contains bug fixes or minor changes that
  do not affect compatibility.

Version bumps are automated and are not required.
An appropriate git tag and GitHub release is created for each version.

## Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Changelog is automatically updated with the Conventional Commit messages.

## Conclusion

We appreciate your contributions to our open source application, and hope that these guidelines will help make the process smoother for everyone involved. Thank you for your support!
