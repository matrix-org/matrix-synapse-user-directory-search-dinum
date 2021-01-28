# Synapse User Directory Search Module for DINUM

A Synapse module which augments user directory search results
as specified by the French Government deployment. For example,
with this module installed, users from the same ministry are
more likely to see other users from the same ministry during
searches.

## Installation

This plugin can be installed into a locally active Python virtualenv via:

```
pip install -e .
```

### Config

Add the following in your Synapse config:

```yaml
   user_directory:
     user_directory_search_module:
       module: "matrix_synapse_user_directory_search_dinum.UserDirectorySearchModule"
       config: {}
```

### Configuration Options

Custom configuration can be specified through the
`user_directory.user_directory_search_module.config` option.

Currently, the following options are supported:

 * `weighted_display_name_like`: Ranks users with a displayname that matches this
   string (using SQL `LIKE` syntax) higher than other users. For example, if this
   option is set to `[Modernisation]`, users with `[Modernisation]` in their
   display name will be matched. Disabled if not set.

## Development and Testing

This repository uses `tox` to run linting and tests.

### Linting

Code is linted with the `flake8` tool. Run `tox -e lint` to check for linting
errors in the codebase.

### Tests

This repository uses `unittest` to run the tests located in the `tests`
directory. They can be ran with `tox -e tests`.

### Making a release

```
git tag vX.Y.Z
python3 setup.py sdist
twine upload dist/matrix-synapse-user-directory-search-dinum-X.Y.Z.tar.gz
git push origin vX.Y.Z
```
