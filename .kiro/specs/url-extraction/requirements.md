# Requirements Document

## Introduction

Esta funcionalidade permite que a CLI do weekseries-downloader aceite URLs diretas do site weekseries.info (como as que os usuários normalmente acessam) e extraia automaticamente as URLs de streaming reais necessárias para o download. Isso elimina a necessidade dos usuários encontrarem manualmente as URLs de streaming, tornando o processo muito mais simples e intuitivo.

## Requirements

### Requirement 1

**User Story:** Como usuário da CLI, eu quero poder fornecer uma URL do weekseries.info diretamente, para que eu não precise encontrar manualmente a URL de streaming.

#### Acceptance Criteria

1. WHEN o usuário fornece uma URL no formato "https://www.weekseries.info/series/[serie]/temporada-[numero]/episodio-[numero]" THEN o sistema SHALL aceitar e processar essa URL
2. WHEN uma URL do weekseries.info é fornecida THEN o sistema SHALL extrair automaticamente a URL de streaming correspondente
3. IF a URL fornecida não for válida ou não seguir o padrão esperado THEN o sistema SHALL exibir uma mensagem de erro clara
4. WHEN a extração da URL de streaming falhar THEN o sistema SHALL informar o usuário sobre o problema específico

### Requirement 2

**User Story:** Como usuário, eu quero que o sistema valide a URL fornecida antes de tentar extrair o streaming, para que eu receba feedback imediato sobre URLs inválidas.

#### Acceptance Criteria

1. WHEN uma URL é fornecida THEN o sistema SHALL validar se ela pertence ao domínio weekseries.info
2. WHEN uma URL tem formato inválido THEN o sistema SHALL exibir uma mensagem explicativa sobre o formato esperado
3. WHEN uma URL é válida mas a página não existe THEN o sistema SHALL informar que o episódio não foi encontrado
4. IF a URL não contém informações suficientes (série, temporada, episódio) THEN o sistema SHALL solicitar esclarecimentos

### Requirement 3

**User Story:** Como desenvolvedor, eu quero que o sistema de extração seja modular e testável, para que possa ser facilmente mantido e expandido.

#### Acceptance Criteria

1. WHEN o sistema extrai URLs THEN ele SHALL usar uma função separada e reutilizável para parsing de URLs
2. WHEN o sistema faz requisições web THEN ele SHALL implementar tratamento adequado de erros de rede
3. WHEN o sistema processa HTML THEN ele SHALL usar parsing robusto que funcione mesmo com pequenas mudanças na estrutura da página
4. IF o site mudar sua estrutura THEN o sistema SHALL falhar de forma controlada com mensagens informativas

### Requirement 4

**User Story:** Como usuário, eu quero que o processo de extração seja rápido e eficiente, para que eu não tenha que esperar muito tempo para iniciar o download.

#### Acceptance Criteria

1. WHEN uma URL é processada THEN o sistema SHALL completar a extração em menos de 10 segundos em condições normais de rede
2. WHEN múltiplas requisições são necessárias THEN o sistema SHALL implementar cache apropriado para evitar requisições desnecessárias
3. WHEN a rede estiver lenta THEN o sistema SHALL exibir indicadores de progresso apropriados
4. IF o processo demorar mais que o esperado THEN o sistema SHALL permitir que o usuário cancele a operação

### Requirement 5

**User Story:** Como usuário, eu quero que a CLI mantenha compatibilidade com URLs de streaming diretas, para que eu ainda possa usar o método antigo se necessário.

#### Acceptance Criteria

1. WHEN uma URL de streaming direta é fornecida THEN o sistema SHALL detectar automaticamente e pular a etapa de extração
2. WHEN ambos os tipos de URL são suportados THEN o sistema SHALL funcionar transparentemente sem confundir o usuário
3. WHEN uma URL ambígua é fornecida THEN o sistema SHALL tentar primeiro como URL do weekseries.info e depois como streaming direto
4. IF nenhum método funcionar THEN o sistema SHALL exibir ajuda sobre os formatos de URL suportados