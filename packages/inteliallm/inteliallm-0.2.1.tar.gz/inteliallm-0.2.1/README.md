Classe para facilitar o acesso ao litellm

Uso Básico:

```python
from inteliallm import InteliaLLMClient

client = InteliaLLMClient()

client.call_llm("escreva uma historia sobre um robo em um json","gpt-4o-mini",key="<chave aqui>")
```

uso Completo:

Todos os parametros do construtor são opcionais.

| Parâmetro         | Obrigatório para:                          |
|-------------------|--------------------------------------------|
| pht_api_token     | consultar/salvar uma chave no banco dado um account_id  |
| litellm_gen_key   | gerar uma chave caso account_id ainda não tenha         |
| litellm_user_id   | gerar uma chave caso account_id ainda não tenha         |
| litellm_team_id   | gerar uma chave caso account_id ainda não tenha         |
| redis_conn        | Usar o Redis e não acessar o banco direto todas as vezes|

Parametros da função call_llm:

| Parâmetro    | Tipo           | Obrigatório | Descrição                                                    |
|--------------|----------------|-------------|--------------------------------------------------------------|
| prompt       | str            | Sim         | Texto da solicitação para o modelo LLM                       |
| model        | str            | Sim         | Nome do modelo a ser utilizado (ex: "gpt-4o-mini")           |
| key          | str            | Apenas se não houver account_id         | Chave de acesso ao LLM (opcional se usar account_id)         |
| account_id   | int/str        | apenas se não houver key         | ID da conta para buscar a chave automaticamente              |
| tags         | list[str]      | Não         | Lista de tags para categorizar a chamada                     |
| no_cache     | bool           | Não         | Se True, ignora o cache e força nova chamada                 |
| metadata     | dict           | Não         | Dicionário com metadados adicionais para a chamada           |
| return_tokens| bool           | Não         | Se True, retorna também o número de tokens usados na resposta|

```python
from inteliallm import InteliaLLMClient

redis_conn = "<connect to redis here>"

client = InteliaLLMClient(
    pht_api_token="<token>",
    litellm_gen_key="<key>",
    litellm_user_id="<id1>",
    litellm_team_id="<id2>",
    redis_conn=redis_conn
)

tags = ['qualquer',"tag"]

no_cache = False

metadata = {
    "qualquer": "valor",
    "outra": "ideia"
}

client.call_llm("escreva uma historia sobre um robo", "gpt-4o-mini",account_id=123,tags=tags,no_cache=no_cache,metadata=metadata)
```

Ou alternativamente, caso já tenha uma chave gerada, você pode usar 

```python
from inteliallm import InteliaLLMClient

redis_conn = "<connect to redis here>"

client = InteliaLLMClient(
    pht_api_token="<token>",
    litellm_gen_key="<key>",
    litellm_user_id="<id1>",
    litellm_team_id="<id2>",
    redis_conn=redis_conn
)

tags = ['qualquer',"tag"]

no_cache = False

metadata = {
    "qualquer": "valor",
    "outra": "ideia"
}

client.call_llm("escreva uma historia sobre um robo", "gpt-4o-mini",key="<insira a chave aqui>",tags=tags,no_cache=no_cache,metadata=metadata)
```