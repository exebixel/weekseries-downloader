# Implementation Plan

- [x] 1. Criar módulo de detecção e validação de URLs usando funções puras
  - Implementar enum `UrlType` para tipos de URL
  - Implementar função `detect_url_type()` com early returns para cada tipo
  - Implementar funções puras: `validate_weekseries_url()`, `is_stream_url()`, `is_base64_string()`
  - Todas as funções devem usar early returns e ser facilmente testáveis
  - _Requirements: 1.1, 2.1, 2.2, 5.1, 5.3_

- [x] 2. Implementar extrator de URLs do WeekSeries usando padrão funcional
  - [x] 2.1 Criar função principal `extract_stream_url()` com injeção de dependências
    - Implementar função pura com early returns para cada etapa
    - Definir protocolos para HttpClient, HtmlParser e Base64Decoder
    - Implementar validação usando função `validate_weekseries_url()`
    - _Requirements: 1.1, 1.2, 2.1_

  - [x] 2.2 Implementar implementações concretas dos protocolos
    - Criar `UrllibHttpClient` implementando protocolo `HttpClient`
    - Implementar `RegexHtmlParser` e `StandardBase64Decoder`
    - Usar função `get_default_headers()` para headers consistentes
    - Implementar early returns em todas as funções
    - _Requirements: 1.2, 3.2, 4.1_

  - [x] 2.3 Implementar funções puras para parsing e decodificação
    - Criar funções puras para parsing HTML/JavaScript com early returns
    - Implementar detecção de padrões base64 usando regex
    - Reutilizar função `decode_base64_url()` existente do utils.py
    - Todas as funções devem ser testáveis independentemente
    - _Requirements: 1.2, 3.3_

  - [ ]* 2.5 Escrever testes unitários para o extrator
    - Criar testes para validação de URLs
    - Criar mocks para requisições HTTP
    - Testar parsing com diferentes estruturas HTML
    - _Requirements: 3.1, 3.3_

- [x] 3. Criar classes de dados e tratamento de erros
  - [x] 3.1 Implementar dataclasses para estruturar dados
    - Criar `EpisodeInfo` para informações extraídas da URL
    - Criar `ExtractionResult` para resultado da extração
    - _Requirements: 2.2, 3.1_

  - [x] 3.2 Implementar hierarquia de exceções customizadas
    - Criar `ExtractionError` como classe base
    - Implementar `InvalidURLError`, `PageNotFoundError`, `ParsingError`
    - Adicionar mensagens de erro informativas
    - _Requirements: 1.3, 1.4, 2.3_

  - [ ]* 3.3 Escrever testes para tratamento de erros
    - Testar diferentes cenários de erro
    - Verificar mensagens de erro apropriadas
    - _Requirements: 1.3, 2.3_

- [x] 4. Integrar extrator com a CLI usando injeção de dependências
  - [x] 4.1 Modificar função `main()` da CLI usando padrão funcional
    - Criar função `create_dependencies()` para setup de dependências
    - Implementar função `process_url_input()` com early returns
    - Manter compatibilidade total com CLI existente
    - _Requirements: 1.1, 5.1, 5.2_

  - [x] 4.2 Implementar configuração automática do referer
    - Definir referer automaticamente quando URL do weekseries é usada
    - Manter opção de override manual do referer
    - _Requirements: 1.1, 5.2_

  - [x] 4.3 Atualizar mensagens de ajuda e documentação da CLI
    - Modificar docstring da função main() com exemplos de URLs do weekseries
    - Atualizar mensagens de erro para incluir formatos suportados
    - _Requirements: 1.4, 2.4, 5.4_

  - [ ]* 4.4 Escrever testes de integração para CLI
    - Testar CLI com diferentes tipos de URL
    - Verificar compatibilidade com opções existentes
    - _Requirements: 5.1, 5.2_

- [x] 5. Implementar otimizações de performance
  - [x] 5.1 Adicionar cache simples para URLs extraídas
    - Implementar cache em memória para sessão atual
    - Evitar requisições desnecessárias para mesma URL
    - _Requirements: 4.2_

  - [x] 5.2 Implementar indicadores de progresso
    - Adicionar mensagens informativas durante extração
    - Implementar timeout configurável com feedback visual
    - _Requirements: 4.3_

  - [ ]* 5.3 Escrever testes de performance
    - Medir tempo de extração
    - Testar comportamento com cache
    - _Requirements: 4.1, 4.2_

- [x] 6. Adicionar dependências necessárias
  - [x] 6.1 Atualizar pyproject.toml com novas dependências
    - Adicionar BeautifulSoup4 para parsing HTML
    - Adicionar requests como alternativa ao urllib (opcional)
    - _Requirements: 3.3_

  - [x] 6.2 Atualizar exemplo de uso
    - Modificar example.py para incluir exemplo com URL do weekseries
    - Demonstrar diferentes tipos de URL suportadas
    - _Requirements: 1.1, 5.4_

- [x] 7. Integração final e testes end-to-end
  - [x] 7.1 Testar fluxo completo com URL real do weekseries
    - Verificar extração, download e conversão funcionando juntos
    - Testar com diferentes séries e episódios
    - _Requirements: 1.1, 1.2, 4.1_

  - [x] 7.2 Verificar tratamento de casos extremos
    - Testar com URLs inválidas ou episódios inexistentes
    - Verificar comportamento com problemas de rede
    - Validar mensagens de erro para usuário final
    - _Requirements: 1.3, 1.4, 2.3_

  - [ ]* 7.3 Executar suite completa de testes
    - Rodar todos os testes unitários e de integração
    - Verificar cobertura de código
    - _Requirements: 3.1, 3.2, 3.3_