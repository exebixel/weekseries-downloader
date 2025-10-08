# 🤝 Contribuindo para o WeekSeries Downloader

Obrigado por considerar contribuir para este projeto! 

## 🚀 Configuração do Ambiente de Desenvolvimento

### 1. Fork e Clone

```bash
# Fork o repositório no GitHub
# Clone seu fork
git clone https://github.com/SEU_USUARIO/weekseries-downloader.git
cd weekseries-downloader

# Adicione o repositório original como upstream
git remote add upstream https://github.com/USUARIO_ORIGINAL/weekseries-downloader.git
```

### 2. Configuração do Poetry

```bash
# Configure Poetry para usar .venv local
poetry config virtualenvs.in-project true

# Instale dependências
poetry install

# Ative o ambiente virtual
poetry shell
```

### 3. Verificação da Instalação

```bash
# Teste o comando
poetry run weekseries-dl --help

# Execute testes (quando disponíveis)
pytest

# Verifique formatação
black --check weekseries_downloader/
flake8 weekseries_downloader/
```

## 📝 Processo de Contribuição

### 1. Crie uma Branch

```bash
# Sempre crie uma nova branch para suas mudanças
git checkout -b feature/nova-funcionalidade
# ou
git checkout -b fix/correcao-bug
# ou
git checkout -b docs/melhoria-documentacao
```

### 2. Faça suas Mudanças

- Mantenha o código limpo e bem documentado
- Siga as convenções de código existentes
- Adicione testes se necessário
- Atualize a documentação se relevante

### 3. Teste suas Mudanças

```bash
# Formate o código
black weekseries_downloader/

# Verifique linting
flake8 weekseries_downloader/

# Execute testes
pytest

# Teste o comando CLI
poetry run weekseries-dl --help
```

### 4. Commit e Push

```bash
# Adicione arquivos modificados
git add .

# Faça commit com mensagem descritiva
git commit -m "✨ feat: adiciona nova funcionalidade X

- Implementa funcionalidade Y
- Corrige problema Z
- Atualiza documentação"

# Push para seu fork
git push origin feature/nova-funcionalidade
```

### 5. Abra um Pull Request

- Vá para o GitHub e abra um Pull Request
- Descreva claramente suas mudanças
- Referencie issues relacionadas se houver

## 🎯 Tipos de Contribuição

### 🐛 Correção de Bugs
- Reporte bugs via Issues
- Inclua passos para reproduzir
- Forneça informações do sistema

### ✨ Novas Funcionalidades
- Discuta a funcionalidade em uma Issue primeiro
- Mantenha o escopo focado
- Adicione testes e documentação

### 📚 Documentação
- Melhore o README
- Adicione exemplos
- Corrija typos

### 🧹 Refatoração
- Melhore a estrutura do código
- Otimize performance
- Mantenha compatibilidade

## 📋 Convenções

### Mensagens de Commit

Use o formato:
```
<tipo>: <descrição>

<corpo opcional>
```

Tipos:
- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Documentação
- `style`: Formatação
- `refactor`: Refatoração
- `test`: Testes
- `chore`: Tarefas de manutenção

### Código

- Use type hints quando possível
- Docstrings para funções públicas
- Nomes descritivos para variáveis
- Mantenha funções pequenas e focadas

### Testes

- Teste funcionalidades críticas
- Use nomes descritivos para testes
- Inclua casos de erro

## 🏷️ Versionamento

Seguimos [Semantic Versioning](https://semver.org/):

- `MAJOR`: Mudanças incompatíveis
- `MINOR`: Novas funcionalidades compatíveis
- `PATCH`: Correções de bugs

## 📞 Suporte

- Abra Issues para bugs e sugestões
- Use Discussions para perguntas gerais
- Seja respeitoso e construtivo

## 📄 Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a mesma licença do projeto.