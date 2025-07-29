def main():
    print("""
CodeWise CLI 

Ferramenta para análise de código, documentação automática e geração de Pull Requests com IA (Gemini + CrewAI).

 Pré-requisitos:
- Criar um arquivo .env com: GEMINI_API_KEY=sua-chave
- Ter o GitHub CLI (gh) instalado e autenticado
- Estar dentro de um repositório Git com commits válidos

 Comandos disponíveis:

  codewise-init --all
    → Instala os hooks na pasta .git (pré-push e pré-commit), ativando a automação para o repositório atual.

  codewise-pr
    → Analisa commits e cria ou atualiza Pull Request com IA (título, descrição e análise técnica).

  codewise-lint
    → Analisa os arquivos staged antes do commit (modo leve, sem IA de PR).

💡 Dica:

- Rode codewise-pr após fazer commits e **antes do push**, para evitar erros silenciosos (ex: falta do `.env`, falha no gh, conflito de branch).
- O pre-push roda codewise-pr automaticamente — útil como backup, mas **pode bloquear o push se algo falhar**.
- Use codewise-init --all uma única vez por repositório.
- ⚠️ **LEMBRE-SE DE CONFIGURAR O .env COM SUA CHAVE DO GEMINI.**
- ⚠️ Se você estiver apenas na branch main (sem commits ou sem branch separada), **o PR não poderá ser criado**, pois não há base de comparação.

""")
