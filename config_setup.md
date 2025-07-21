# 🔧 Guia de Configuração - Chronos AI

## ❌ Problema Identificado

O erro **"📋 Notion: Configuração de database incorreta (ID: 23248c51...)"** está acontecendo porque:

**As variáveis de ambiente `NOTION_TOKEN` e `DATABASE_ID` não estão configuradas.**

## ✅ Solução Completa

### 1. Criar Arquivo de Configuração

Crie um arquivo `.env` na raiz do projeto:

```bash
# Na raiz do projeto chronos-ai
touch .env
```

### 2. Configurar Integração Notion

#### Passo 1: Criar Integração

1. Acesse: https://www.notion.so/my-integrations
2. Clique **"New integration"**
3. Preencha:
   - **Name**: `Chronos AI`
   - **Workspace**: Selecione seu workspace
   - **Type**: Internal
4. Clique **"Submit"**
5. **Copie o "Internal Integration Token"** (começa com `secret_`)

#### Passo 2: Criar Database no Notion

Crie um database com estas propriedades **exatas**:

| Propriedade      | Tipo         | Descrição                                    |
| ---------------- | ------------ | -------------------------------------------- |
| `Name`           | Title        | Nome da tarefa                               |
| `Category`       | Select       | Development, Meetings, Personal, etc.        |
| `Priority`       | Select       | Baixa, Média, Alta, Urgente                  |
| `Status`         | Select       | Pendente, Em Andamento, Concluído, Cancelado |
| `Estimated Time` | Number       | Tempo estimado em minutos                    |
| `Actual Time`    | Number       | Tempo real gasto                             |
| `Created`        | Created time | Data de criação                              |
| `Due Date`       | Date         | Data limite                                  |
| `Scheduled Time` | Date         | Horário agendado                             |
| `Description`    | Text         | Descrição da tarefa                          |
| `Tags`           | Multi-select | Tags personalizadas                          |

#### Passo 3: Conectar Integração ao Database

1. No seu database do Notion, clique **"..."** (três pontos)
2. Selecione **"Add connections"**
3. Escolha **"Chronos AI"**
4. Copie o **ID do database** da URL do navegador

**Exemplo de URL:**

```
https://www.notion.so/workspace/23248c51a1b2c3d4e5f6789012345678?v=...
```

**Database ID:** `23248c51a1b2c3d4e5f6789012345678`

### 3. Configurar Claude AI (Opcional)

1. Acesse: https://console.anthropic.com/
2. Faça login ou crie uma conta
3. Vá em **"API Keys"** → **"Create Key"**
4. Copie a chave gerada

### 4. Preencher Arquivo .env

Edite o arquivo `.env` com suas configurações:

```bash
# Configuração Notion
NOTION_TOKEN=secret_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
DATABASE_ID=23248c51a1b2c3d4e5f6789012345678

# Configuração Claude (opcional)
CLAUDE_API_KEY=sk-ant-api03-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# Configuração Database
DB_PASSWORD=chronos_secure_password_2024
```

### 5. Reiniciar Sistema

```bash
# Parar containers
docker-compose down

# Iniciar com nova configuração
docker-compose up

# Ou em background
docker-compose up -d
```

## 🔍 Validação da Configuração

Execute o diagnóstico para verificar se tudo está funcionando:

```bash
# Ativar ambiente virtual
source venv/bin/activate

# Executar diagnóstico
python integrations/notion_diagnostic.py
```

## ⚠️ Problemas Comuns

### Database ID Inválido

- **Erro**: ID tem comprimento incorreto
- **Solução**: Verifique se copiou os 32 caracteres corretos da URL

### Token Inválido

- **Erro**: API retorna 401
- **Solução**: Gere um novo token na página de integrações

### Permissão Negada

- **Erro**: API retorna 401/403
- **Solução**: Adicione a integração ao database usando "Add connections"

### Propriedades Ausentes

- **Erro**: Database não tem propriedades esperadas
- **Solução**: Adicione todas as propriedades listadas acima com os tipos corretos

## 📊 Status Esperado Após Configuração

Logs de sucesso:

```
✅ CHRONOS inicializado com sucesso
📋 Notion: 5 tarefa(s) encontrada(s) para hoje
🤖 Claude: ✅ Sugestão IA gerada com sucesso
```

## 🆘 Precisa de Ajuda?

Se o problema persistir:

1. Execute o diagnóstico completo
2. Verifique os logs detalhados
3. Confirme que todas as propriedades do database estão corretas
4. Teste a conectividade manualmente com a Notion API
