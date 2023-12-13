# Contributing to `snowplow-python-tracker`

`snowplow-python-tracker` is a fork of the original Snowplow Python tracker v0.8.0.


1. [About this document](#about-this-document)
2. [Getting the code](#getting-the-code)
3. [Setting up an environment](#setting-up-an-environment)
4. [Running in development](#running-snowplow-python-tracker-in-development)
5. [Testing](#testing)
6. [Debugging](#debugging)
7. [Adding or modifying a changelog entry](#adding-or-modifying-a-changelog-entry)
8. [Submitting a Pull Request](#submitting-a-pull-request)
9. [Troubleshooting Tips](#troubleshooting-tips)

## About this document

There are many ways to contribute to the ongoing development of `snowplow-python-tracker`, such as by participating in discussions and issues. We encourage you to first read our higher-level document: ["Expectations for Open Source Contributors"](https://docs.getdbt.com/docs/contributing/oss-expectations).

The rest of this document serves as a more granular guide for contributing code changes to `snowplow-python-tracker` (this repository). It is not intended as a guide for using `snowplow-python-tracker`, and some pieces assume a level of familiarity with Python development (virtualenvs, `pip`, etc). Specific code snippets in this guide assume you are using macOS or Linux and are comfortable with the command line.

### Notes

- **CLA:** Please note that anyone contributing code to `snowplow-python-tracker` must sign the [Contributor License Agreement](https://docs.getdbt.com/docs/contributor-license-agreements). If you are unable to sign the CLA, the `snowplow-python-tracker` maintainers will unfortunately be unable to merge any of your Pull Requests. We welcome you to participate in discussions, open issues, and comment on existing ones.
- **Branches:** All pull requests from community contributors should target the `master` branch (default).
- **Releases**: This repository is released only as needed.

## Getting the code

### Installing git

You will need `git` in order to download and modify the source code.

### External contributors

If you are not a member of the `dbt-labs` GitHub organization, you can contribute to `snowplow-python-tracker` by forking the `snowplow-python-tracker` repository. For a detailed overview on forking, check out the [GitHub docs on forking](https://help.github.com/en/articles/fork-a-repo). In short, you will need to:

1. Fork the `snowplow-python-tracker` repository
2. Clone your fork locally
3. Check out a new branch for your proposed changes
4. Push changes to your fork
5. Open a pull request against `dbt-labs/snowplow-python-tracker` from your forked repository

### dbt Labs contributors

If you are a member of the `dbt-labs` GitHub organization, you will have push access to the `snowplow-python-tracker` repo. Rather than forking `snowplow-python-tracker` to make your changes, just clone the repository, check out a new branch, and push directly to that branch.

## Setting up an environment

There are some tools that will be helpful to you in developing locally. While this is the list relevant for `snowplow-python-tracker` development, many of these tools are used commonly across open-source python projects.

#### Virtual environments

We strongly recommend using virtual environments when developing code in `snowplow-python-tracker`. We recommend creating this virtualenv
in the root of the `snowplow-python-tracker` repository. To create a new virtualenv, run:
```sh
python3 -m venv env
source env/bin/activate
```

This will create and activate a new Python virtual environment.

## Running `snowplow-python-tracker` in development

### Installation

First make sure that you set up your `virtualenv` as described in [Setting up an environment](#setting-up-an-environment).  Also ensure you have the latest version of pip installed with `pip install --upgrade pip`. Next, install `snowplow-python-tracker` (and its dependencies):

```sh
git
pre-commit install
```

## Testing

Once you're able to manually test that your code change is working as expected, it's important to run existing automated tests, as well as adding some new ones. These tests will ensure that:
- Your code changes do not unexpectedly break other established functionality
- Your code changes can handle all known edge cases
- The functionality you're adding will _keep_ working in the future

### Initial setup

None needed.

### Test commands

docker-compose run --rm test tox


### Assorted development tips
* This is a fork of [snowplow-python-tracker](https://github.com/snowplow/snowplow-python-tracker) and bets practices in that repository should be followed here

## Submitting a Pull Request

Code can be merged into the current development branch `main` by opening a pull request. A `snowplow-python-tracker` maintainer will review your PR. They may suggest code revision for style or clarity, or request that you add unit or integration test(s). These are good things! We believe that, with a little bit of help, anyone can contribute high-quality code.

Automated tests run via GitHub Actions. If you're a first-time contributor, all tests (including code checks and unit tests) will require a maintainer to approve. Changes in the `snowplow-python-tracker` repository trigger integration tests against Postgres. dbt Labs also provides CI environments in which to test changes to other adapters, triggered by PRs in those adapters' repositories, as well as periodic maintenance checks of each adapter in concert with the latest `snowplow-python-tracker` code changes.

Once all tests are passing and your PR has been approved, a `snowplow-python-tracker` maintainer will merge your changes into the active development branch. And that's it! Happy developing :tada:

## Troubleshooting Tips
- Sometimes, the content license agreement auto-check bot doesn't find a user's entry in its roster. If you need to force a rerun, add `@cla-bot check` in a comment on the pull request.
