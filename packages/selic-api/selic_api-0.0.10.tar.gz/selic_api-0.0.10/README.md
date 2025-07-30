# selic_api

API para obter a taxa SELIC acumulada para fins de cálculo da atualização monetária para os tributos da Prefeitura de Belo Horizonte.

## Publicando uma nova versão no PyPI

Para publicar uma nova versão do seu pacote no PyPI, você precisará seguir os seguintes passos:

1. Atualize a versão do pacote no arquivo `pyproject.toml`. Você deve obedecer as regras do versionamento Semantic. Por exemplo, se você está atualizando a versão de um pacote de 0.1.0 para 0.2.0, você precisará atualizar a versão do pacote no arquivo `pyproject.toml` de 0.1.0 para 0.2.0.

Para atualizar a versão do pacote no arquivo `pyproject.toml`, você pode usar o comando `poetry version` seguido do número de versão.

Por exemplo, caso deseje atualizar a versão do pacote de 0.1.0 para 0.2.0, você pode usar o seguinte comando:

`poetry version 0.2.0`

Ou então caso deseje atualizar uma versão de patch, você pode usar o seguinte comando:

`poetry version patch`

Ou caso deseje atualizar uma versão de minor, você pode usar o seguinte comando:

`poetry version minor`

Ou caso deseje atualizar uma versão de major, você pode usar o seguinte comando:

`poetry version major`

Estes comandos irão atualizar a versão do pacote no arquivo `pyproject.toml` e criar um novo commit com a atualização da versão.

Depois de atualizar a versão do pacote no arquivo `pyproject.toml`, você precisará commitar e enviar o novo commit para o seu repositório Git.

Após o commit ser enviado, você deverá criar uma nova tag no seu repositório Git com a nova versão do pacote.

Para criar uma nova tag no seu repositório Git, você pode usar o seguinte comando:

`git tag v0.2.0`

Este comando irá criar uma nova tag no seu repositório Git com o nome "v0.2.0".

A versão da tag deve seguir o padrão `v*.*.*` que corresponde ao número de versão que você deseja lançar e ao arquivo `pyproject.toml`.

Uma maneira de garantir que a versão da tag seja igual ao número de versão do pacote no arquivo `pyproject.toml` é usar o comando:

`git tag v$(poetry version -s)`

Este comando irá criar uma nova tag no seu repositório Git com o nome "v$(poetry version -s)" que corresponde ao número de versão do pacote no arquivo `pyproject.toml`.

Criada a tag, você deve enviá-la para o seu repositório Git.

Para enviar a tag para o seu repositório Git, você pode usar o seguinte comando:

`git push --tags`.

Depois de enviar a tag para o seu repositório Git, você deverá esperar que o Github Actions seja executado para publicar a nova versão do seu pacote no PyPI.

A Action de publicação no PyPI está definifca no arquivo `.github/workflows/publish-to-pypi.yml`. Esta Action será executada automaticamente quando uma nova tag for criada no seu repositório Git.

Ao final do processo, você deverá ser capaz de instalar a nova versão do seu pacote usando o comando `pip install selic_api`.
