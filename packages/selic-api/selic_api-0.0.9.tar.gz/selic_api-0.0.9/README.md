# selic_api
 API para obter a taxa SELIC acumulada para fins de cálculo da atualização monetária para os tributos da Prefeitura de Belo Horizonte.

## Publishing a new version on PyPI

To publish a new version of a Poetry package to PyPI, follow these steps:

1. Update the version number of your package in your project's pyproject.toml file. This should be done according to the Semantic Versioning guidelines.
2. Build the distribution files for the new version of your package by running the following command in your project's root directory:

`poetry build`

This will create a dist directory with the distribution files for your package.

3. Check that the generated distribution files are correct by running the following command:

`poetry check`

This will perform several checks on the generated distribution files and report any issues.

4. Publish the new version of your package to PyPI by running the following command:

`poetry publish`

This will upload the distribution files to PyPI and make the new version of your package available for installation.

Note that you will need to have a PyPI account and be logged in to it for this step to work.

Also, if this is the first time you are publishing your package to PyPI, you will need to create a new release on GitHub (or other version control system you use) and tag it with the new version number before running the poetry publish command. This is because PyPI requires that the source code for each release be available online.
