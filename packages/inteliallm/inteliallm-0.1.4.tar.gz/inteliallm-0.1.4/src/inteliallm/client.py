import logging
from typing import Any, Tuple

import dirtyjson
import openai
import requests
from redis import Redis
from slugify import slugify
import uuid

# É uma boa prática configurar o logger para o módulo específico
logger = logging.getLogger(__name__)


class InteliaLLMClient:
    """
    Cliente para gerenciar chaves e interagir com as APIs da PhoneTrack e LiteLLM.
    """
    
    # URLs das APIs como constantes de classe
    _PHT_API_BASE_URL = "https://api.phonetrack.app/api/v3"
    _LITELLM_API_BASE_URL = "https://llm.intelia.com.br"

    def __init__(
        self,
        pht_api_token: str,
        litellm_gen_key: str,
        litellm_user_id: str,
        litellm_team_id: str,
        redis_conn: Redis,
    ):
        """
        Inicializa o cliente com as dependências necessárias.

        Args:
            redis_conn: Uma instância de cliente Redis conectado.
            pht_api_token: Token de API para a PhoneTrack.
            litellm_gen_key: Token para gerar novas chaves virtuais na LiteLLM.
            litellm_user_id: User ID para a criação de chaves na LiteLLM.
            litellm_team_id: Team ID para a criação de chaves na LiteLLM.
        """
        if not all([pht_api_token, litellm_gen_key, litellm_user_id, litellm_team_id]):
            raise ValueError("Todos os argumentos do construtor são obrigatórios.")

        self.pht_api_token = pht_api_token
        self.litellm_gen_key = litellm_gen_key
        self.litellm_user_id = litellm_user_id
        self.litellm_team_id = litellm_team_id
        self.redis = redis_conn
        
        # Cria uma sessão de requests para reutilizar conexões HTTP
        self.session = requests.Session()
        self.session.headers['Authorization'] = self.pht_api_token

        logger.info("InteliaLLMClient inicializado com sucesso.")

    # MÉTODOS PÚBLICOS (A API DA SUA BIBLIOTECA)

    def get_key(self, account_id: int) -> str:
        """
        Obtém a chave virtual da LiteLLM para um determinado ID de conta.
        Primeiro, tenta buscar do cache (Redis). Se não encontrar, busca no
        banco de dados da PHT e, em último caso, cria uma nova chave.
        """
        redis_key = f"litellm_key:{account_id}"
        if self.redis:
            cached_key = self.redis.get(redis_key)
        else:
            cached_key = None

        if cached_key:
            logger.info(f"Chave para account_id {account_id} encontrada no cache Redis.")
            return cached_key.decode('utf-8')

        logger.info(f"Chave para account_id {account_id} não encontrada no cache. Buscando no banco de dados.")
        db_key = self._get_key_from_database(account_id)
        if self.redis:
            self.redis.set(redis_key, db_key, ex=3600)  # Expira em 1 hora
            logger.info(f"Chave para account_id {account_id} salva no cache Redis.")

        return db_key

    def call_llm(self, account_id: int, prompt: str, model: str, tags: list | None = None, no_cache: bool = False, metadata: dict | None = None) -> Tuple[str, int, int]:
        """
        Faz uma chamada para a API da LiteLLM usando a chave associada à conta.

        Args:
            account_id: O ID da conta para obter a chave e associar a chamada.
            prompt: O prompt a ser enviado para o modelo.
            model: O nome do modelo a ser usado (ex: "gpt-4o").
            tags: Tags para associar à chamada na LiteLLM.
            no_cache: Se True, desativa o cache da LiteLLM para esta chamada.
            metadata: Metadados adicionais para a chamada.

        Returns:
            Uma tupla contendo (resposta, tokens_de_entrada, tokens_de_saida).
        """
        if metadata is None:
            metadata = {}
            
        key = self.get_key(account_id)
        session_id = (
            metadata.get("call_id")
            or metadata.get("conversation_id")
            or str(uuid.uuid4())
        )

        client = openai.OpenAI(api_key=key, base_url=self._LITELLM_API_BASE_URL)

        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            extra_body={
                "tags": tags,
                "fallbacks": ["gpt-4o-mini"],
                "cache": {"no-cache": no_cache},
                "litellm_session_id": session_id,
                "metadata": metadata
            }
        )
        
        # Usar model_dump() é mais limpo que model_dump_json() + dirtyjson
        response_data = response.model_dump()
        answer = response_data['choices'][0]['message']['content']

        if not answer:
            raise ValueError("Nenhuma resposta recebida da API LLM.")
            
        input_tokens = response_data['usage']['prompt_tokens']
        output_tokens = response_data['usage']['completion_tokens']
        
        # Limpa a resposta se ela vier formatada como um bloco de código JSON
        if "```json" in answer:
            answer = answer.split("```json")[1].split("```")[0]
        elif answer.strip().startswith("json"):
            answer = answer.split("json", 1)[1]

        return answer, input_tokens, output_tokens

    # MÉTODOS PRIVADOS (LÓGICA INTERNA)

    def _get_pht_account_details(self, account_id: int) -> dict[str, Any]:
        """Busca os detalhes completos de uma conta na PhoneTrack."""
        url = f"{self._PHT_API_BASE_URL}/accounts/{account_id}"
        response = self.session.get(url)
        response.raise_for_status() # Lança um erro para status 4xx/5xx
        return response.json().get("row", {})

    def _get_key_from_database(self, account_id: int) -> str:
        """Busca a chave no banco de dados da PhoneTrack."""
        url = f"{self._PHT_API_BASE_URL}/accounts/{account_id}/configs/llm_virtual_key"
        response = self.session.get(url)
        
        if response.ok and response.json().get('value'):
            key = response.json()['value']
            logger.info(f"Chave recuperada do banco de dados para account_id {account_id}.")
            return key
        
        logger.warning(f"Chave não encontrada no banco de dados para account_id {account_id}.")
        if account_id == 1: # Mantém a lógica de exceção para a conta principal
            raise ValueError("Chave não encontrada para account_id 1. Adicione manualmente.")

        # Se não encontrou, cria, salva no banco e retorna a nova chave
        new_key = self._create_litellm_key(account_id)
        self._put_key_into_database(account_id, new_key)
        return new_key

    def _create_litellm_key(self, account_id: int) -> str:
        """Cria uma nova chave virtual na API da LiteLLM."""
        account_details = self._get_pht_account_details(account_id)
        account_name = account_details.get("name")
        account_uuid = account_details.get("uuid")

        if not account_name or not account_uuid:
            raise ValueError(f"Nome ou UUID não encontrados para account_id {account_id}.")

        logger.info(f"Criando chave para a conta: {account_name}")
        url = f'{self._LITELLM_API_BASE_URL}/key/generate'
        headers = {
            'Authorization': f'Bearer {self.litellm_gen_key}',
            'Content-Type': 'application/json'
        }
        payload = {
            "user_id": self.litellm_user_id,
            "team_id": self.litellm_team_id,
            "key_alias": f"{slugify(account_name)}|{account_uuid}",
            "metadata": {
                "name": account_name,
                "description": f"Key for {account_name}",
                "tags": [account_name],
                "account_id": account_id,
                "account_uuid": account_uuid
            }
        }
        
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        key = response.json().get('key')
        if not key:
            raise ValueError(f"Falha ao extrair a nova chave da resposta da API para account_id {account_id}.")
            
        logger.info(f"Chave virtual LLM criada com sucesso para account_id {account_id}.")
        return key

    def _put_key_into_database(self, account_id: int, key: str):
        """Salva a chave virtual no banco de dados da PhoneTrack."""
        url = f'{self._PHT_API_BASE_URL}/accounts/{account_id}/configs/llm_virtual_key'
        headers = {'Content-Type': 'application/json'} # O token já está na sessão
        json_data = {'value': key}
        
        response = self.session.put(url, headers=headers, json=json_data)
        response.raise_for_status()
        
        logger.info(f"Chave LLM salva com sucesso no banco de dados para account_id {account_id}.")
