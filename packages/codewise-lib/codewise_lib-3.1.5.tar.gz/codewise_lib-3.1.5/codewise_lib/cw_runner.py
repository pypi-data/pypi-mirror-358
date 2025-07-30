# Arquivo: cw_runner.py (VERSÃO FINAL E COMPLETA)
import os
import sys
from .crew import Codewise
from .entradagit import gerar_entrada_automatica, obter_mudancas_staged
from crewai import Task, Crew

class CodewiseRunner:
    def __init__(self):
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.caminho_entrada = os.path.join(self.BASE_DIR, ".entrada_temp.txt")

    def executar(self, caminho_repo: str, nome_branch: str, modo: str):
        contexto_para_ia = ""
        
        if modo == 'lint':
            resultado_git = obter_mudancas_staged(caminho_repo)
            
            if resultado_git is None:
                print("Nenhum problema aparente detectado.")
                sys.exit(0)
            
            if resultado_git.startswith("AVISO:") or resultado_git.startswith("FALHA:"):
                print(resultado_git)
                sys.exit(0)
            
            contexto_para_ia = resultado_git
        else:
            if not gerar_entrada_automatica(caminho_repo, self.caminho_entrada, nome_branch):
                sys.exit(0)
            contexto_para_ia = self._ler_arquivo(self.caminho_entrada)
        
        codewise_instance = Codewise(commit_message=contexto_para_ia)
        resultado_final = ""

        if modo == 'titulo':
            agent = codewise_instance.summary_specialist()
            task = Task(description=f"Crie um título de PR conciso no padrão Conventional Commits para as seguintes mudanças. A resposta deve ser APENAS o título, **obrigatoriamente em Português do Brasil**, sem aspas, acentos graves ou qualquer outro texto:\n{contexto_para_ia}", expected_output="Um único título de PR.", agent=agent)
            resultado_final = Crew(agents=[agent], tasks=[task]).kickoff()

        elif modo == 'descricao':
            agent = codewise_instance.summary_specialist()
            task = Task(description=f"Crie uma descrição de um parágrafo **obrigatoriamente em Português do Brasil** para um Pull Request para as seguintes mudanças:\n{contexto_para_ia}", expected_output="Um único parágrafo de texto.", agent=agent)
            resultado_final = Crew(agents=[agent], tasks=[task]).kickoff()

        elif modo == 'analise':
            analysis_crew = codewise_instance.crew()
            # O input para a análise profunda é passado aqui
            analysis_crew.kickoff(inputs={'input': contexto_para_ia})
            
            print("Salvando relatórios de análise individuais...", file=sys.stderr)
            task_config = codewise_instance.tasks_config
            task_map = {
                task_config['analise_estrutura']['description']: "arquitetura_atual.md",
                task_config['analise_heuristicas']['description']: "analise_heuristicas_integracoes.md",
                task_config['analise_solid']['description']: "analise_solid.md",
                task_config['padroes_projeto']['description']: "padroes_de_projeto.md"
            }
            
            for task in analysis_crew.tasks:
                if task.description in task_map:
                    filename = task_map[task.description]
                    file_path = os.path.join(caminho_repo, filename)
                    # Usamos .raw_output para pegar apenas o texto gerado pelo agente daquela tarefa
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(task.output.raw_output)
                    print(f"   - Arquivo '{filename}' salvo.", file=sys.stderr)

            resumo_agent = codewise_instance.summary_specialist()
            resumo_task = Task(
                description="Com base no contexto da análise completa fornecida, crie um 'Resumo Executivo do Pull Request' **obrigatoriamente em Português do Brasil**, bem formatado em markdown, com 3-4 bullet points detalhados.",
                expected_output="Um resumo executivo em markdown.",
                agent=resumo_agent,
                context=analysis_crew.tasks
            )
            resultado_final = Crew(agents=[resumo_agent], tasks=[resumo_task]).kickoff()

        elif modo == 'lint':
            agent = codewise_instance.quality_consultant()
            task = Task(description=f"Analise rapidamente as seguintes mudanças de código ('git diff') e aponte APENAS problemas óbvios ou code smells. A resposta deve ser **obrigatoriamente em Português do Brasil**. Seja conciso. Se não houver problemas, retorne 'Nenhum problema aparente detectado.'.\n\nCódigo a ser analisado:\n{contexto_para_ia}", expected_output="Uma lista curta em bullet points com sugestões, ou uma mensagem de que está tudo ok.", agent=agent)
            resultado_final = Crew(agents=[agent], tasks=[task]).kickoff()
        
        if os.path.exists(self.caminho_entrada):
            os.remove(self.caminho_entrada)

        print(str(resultado_final).strip().replace('`', ''))

    def _ler_arquivo(self, file_path: str) -> str:
        try:
            with open(file_path, "r", encoding="utf-8") as f: return f.read()
        except FileNotFoundError: return ""