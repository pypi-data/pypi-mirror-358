import shutil
import subprocess
import os
import sys
import re
import json
import argparse
from datetime import datetime

# ===================================================================
# SEÇÃO DE FUNÇÕES AUXILIARES (COMPARTILHADAS)
# ===================================================================

def run_codewise_mode(mode, repo_path, branch_name):
    """Executa a IA como um MÓDULO e captura a saída, resolvendo o ImportError."""
    print(f"\n--- *! Executando IA [modo: {mode}] !* ---")
    
    command = [
        sys.executable, "-m", "codewise_lib.main",
        "--repo", repo_path,
        "--branch", branch_name,
        "--mode", mode
    ]
    try:
        env = os.environ.copy()
        # Adiciona a raiz do projeto ao PYTHONPATH para garantir que os módulos sejam encontrados
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        env['PYTHONPATH'] = f"{project_root}{os.pathsep}{env.get('PYTHONPATH', '')}"
        
        result = subprocess.run(
            command, 
            check=True, 
            capture_output=True, 
            text=True, 
            encoding='utf-8', 
            errors='ignore', 
            env=env,
            stdin=subprocess.DEVNULL
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        # LÓGICA DE DEBUG MELHORADA PARA CAPTURAR TODOS OS ERROS
        print(f"❌ FALHA no modo '{mode}': O subprocesso falhou com o código de saída {e.returncode}", file=sys.stderr)
        print("\n--- Saída de Erro (stderr) do Subprocesso ---", file=sys.stderr)
        print(e.stderr if e.stderr else "Nenhuma saída de erro foi capturada.")
        print("\n--- Saída Padrão (stdout) do Subprocesso ---", file=sys.stderr)
        print(e.stdout if e.stdout else "Nenhuma saída padrão foi capturada.")
        print("---------------------------------------------", file=sys.stderr)
        return None

def obter_branch_padrao_remota(repo_path):
    try:
        remote_url_result = subprocess.check_output(["git", "config", "--get", "remote.origin.url"], cwd=repo_path, text=True, encoding='utf-8').strip()
        match = re.search(r'github\.com/([^/]+/[^/]+?)(\.git)?$', remote_url_result)
        if not match: return "main"
        repo_slug = match.group(1)
        result = subprocess.check_output(
            ["gh", "repo", "view", repo_slug, "--json", "defaultBranchRef", "-q", ".defaultBranchRef.name"],
            text=True, encoding='utf-8', stderr=subprocess.DEVNULL
        ).strip()
        if not result: return "main"
        print(f"✅ Branch principal detectada no GitHub: '{result}'", file=sys.stderr)
        return result
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "main"

def extrair_titulo_valido(texto):
    match = re.search(r"(feat|fix|refactor|docs):\s.+", texto, re.IGNORECASE)
    if match: return match.group(0).strip()
    return None

def obter_pr_aberto_para_branch(branch, repo_dir):
    try:
        result = subprocess.run(["gh", "pr", "list", "--head", branch, "--state", "open", "--json", "number"], check=True, capture_output=True, text=True, encoding='utf-8', cwd=repo_dir)
        return json.loads(result.stdout)[0]['number'] if json.loads(result.stdout) else None
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return None

def obter_repo_slug(remote_name, repo_path):
    """Obtém o slug 'usuario/repo' de um remote específico ('origin' ou 'upstream')."""
    try:
        remote_url = subprocess.check_output(
            ["git", "config", "--get", f"remote.{remote_name}.url"],
            cwd=repo_path, text=True, encoding='utf-8'
        ).strip()
        match = re.search(r'github\.com[/:]([^/]+/[^/]+?)(\.git)?$', remote_url)
        if match:
            return match.group(1)
        return None
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

def verificar_remote_existe(remote_name, repo_path):
    """Verifica se um remote com o nome especificado existe."""
    try:
        remotes = subprocess.check_output(["git", "remote"], cwd=repo_path, text=True, encoding='utf-8')
        return remote_name in remotes.split()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

# ===================================================================
# LÓGICA DO COMANDO 'codewise-lint' (PARA PRE-COMMIT)
# ===================================================================
def main_lint():
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    repo_path = os.getcwd()
    try:
        current_branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], encoding='utf-8', cwd=repo_path).strip()
    except Exception:
        current_branch = ""
        
    print("--- 🔍 Executando análise rápida pré-commit do CodeWise ---", file=sys.stderr)
    sugestoes = run_codewise_mode("lint", repo_path, current_branch)

    if sugestoes is None:
        print("--- ❌ A análise rápida falhou. Verifique os erros acima. ---", file=sys.stderr)
        sys.exit(1)

    sugestoes_limpas = sugestoes.strip()

    if "AVISO:" in sugestoes_limpas or "FALHA:" in sugestoes_limpas:
        print("\n--- ⚠️  ATENÇÃO ---", file=sys.stderr)
        print(sugestoes_limpas, file=sys.stderr)
        print("-------------------", file=sys.stderr)
    elif "Nenhum problema aparente detectado" in sugestoes_limpas:
        print("--- ✅ Nenhuma sugestão crítica. Bom trabalho! ---", file=sys.stderr)
    elif sugestoes_limpas:
        print("\n--- 💡 SUGESTÕES DE MELHORIA ---", file=sys.stderr)
        print(sugestoes_limpas, file=sys.stderr)
        print("---------------------------------", file=sys.stderr)
    else:
        print("--- ✅ Nenhuma sugestão crítica. Bom trabalho! ---", file=sys.stderr)

# ===================================================================
# LÓGICA DO COMANDO 'codewise-pr' (PARA PRE-PUSH)
# ===================================================================
def run_pr_logic(target_selecionado):
    """Função principal que contém toda a lógica de criação de PR."""
    if not shutil.which("gh"):
        print("❌ Erro: GitHub CLI ('gh') não foi encontrado no seu sistema.", file=sys.stderr)
        print("   Por favor, instale-a a partir de: https://cli.github.com/", file=sys.stderr)
        sys.exit(1)

    os.environ['PYTHONIOENCODING'] = 'utf-8'
    repo_path = os.getcwd()

    upstream_existe = verificar_remote_existe('upstream', repo_path)
    upstream_renomeado = False

    try:
        if target_selecionado == 'origin' and upstream_existe:
            print("🔧 Truque: Renomeando 'upstream' temporariamente para evitar bug do gh...", file=sys.stderr)
            subprocess.run(["git", "remote", "rename", "upstream", "upstream_temp"], cwd=repo_path, check=True, capture_output=True)
            upstream_renomeado = True

        print(f"📍 Analisando o repositório em: {repo_path}", file=sys.stderr)
        print(f"🎯 Alvo do Pull Request definido para: '{target_selecionado}'", file=sys.stderr)

        if target_selecionado == 'upstream' and not upstream_existe:
            sys.exit("❌ Erro: O alvo é 'upstream', mas o remote 'upstream' não está configurado.")

        try:
            current_branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], encoding='utf-8', cwd=repo_path).strip()
        except Exception as e:
            sys.exit(f"❌ Erro ao detectar a branch Git: {e}")

        base_branch_target = obter_branch_padrao_remota(repo_path)
        if current_branch == base_branch_target:
            sys.exit(f"❌ A automação não pode ser executada na branch principal ('{base_branch_target}').")

        origin_slug = obter_repo_slug('origin', repo_path)
        if not origin_slug:
            sys.exit("❌ Falha crítica: Não foi possível determinar o repositório 'origin'.")

        head_branch_completa = f"{origin_slug.split('/')[0]}:{current_branch}"
        repo_alvo_pr = obter_repo_slug(target_selecionado, repo_path)

        print("\n--- 🤖 Executando IA para documentação do PR ---", file=sys.stderr)
        titulo_bruto = run_codewise_mode("titulo", repo_path, current_branch)
        descricao = run_codewise_mode("descricao", repo_path, current_branch)
        analise_tecnica = run_codewise_mode("analise", repo_path, current_branch)

        if not all([titulo_bruto, descricao, analise_tecnica]):
            sys.exit("❌ Falha ao gerar todos os textos necessários da IA.")

        titulo_final = extrair_titulo_valido(titulo_bruto) or f"feat: Modificações da branch {current_branch}"
        print(f"✔️ Título definido para o PR: {titulo_final}", file=sys.stderr)

        temp_analise_path = os.path.join(repo_path, ".codewise_analise_temp.txt")
        with open(temp_analise_path, "w", encoding='utf-8') as f: f.write(analise_tecnica)
        pr_numero = obter_pr_aberto_para_branch(current_branch, repo_path)

        if pr_numero:
            print(f"⚠️ PR #{pr_numero} já existente. Acrescentando nova análise...", file=sys.stderr)
            try:
                descricao_antiga_raw = subprocess.check_output(
                    ["gh", "pr", "view", str(pr_numero), "--json", "body", "--repo", repo_alvo_pr],
                    cwd=repo_path, text=True, encoding='utf-8'
                )
                descricao_antiga = json.loads(descricao_antiga_raw).get("body", "")
                timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                nova_entrada_descricao = (f"\n\n---\n\n" f"**🔄 Atualização em {timestamp}**\n\n" f"{descricao}")
                body_final = descricao_antiga + nova_entrada_descricao
                subprocess.run(["gh", "pr", "edit", str(pr_numero), "--title", titulo_final, "--body", body_final, "--repo", repo_alvo_pr], check=False, cwd=repo_path)
                print(f"✅ Descrição do PR #{pr_numero} atualizada com novas informações.")
            except Exception as e:
                print(f"⚠️ Não foi possível buscar a descrição antiga. Substituindo pela nova. Erro: {e}", file=sys.stderr)
                subprocess.run(["gh", "pr", "edit", str(pr_numero), "--title", titulo_final, "--body", descricao, "--repo", repo_alvo_pr], check=False, cwd=repo_path)
        else:
            print("🆕 Nenhum PR aberto. Criando Pull Request...", file=sys.stderr)
            try:
                comando_pr = ["gh", "pr", "create", "--repo", repo_alvo_pr, "--base", base_branch_target, "--head", head_branch_completa, "--title", titulo_final, "--body", descricao]
                result = subprocess.run(comando_pr, check=True, capture_output=True, text=True, encoding='utf-8', cwd=repo_path)
                pr_url = result.stdout.strip()
                match = re.search(r"/pull/(\d+)", pr_url)
                if match:
                    pr_numero = match.group(1)
                else:
                    raise Exception(f"Não foi possível extrair o número do PR da URL: {pr_url}")
                print(f"✅ PR #{pr_numero} criado: {pr_url}", file=sys.stderr)
            except Exception as e:
                if os.path.exists(temp_analise_path): os.remove(temp_analise_path)
                sys.exit(f"❌ Falha ao criar PR: {e}")

        if pr_numero:
            print(f"💬 Comentando análise técnica no PR #{pr_numero}...", file=sys.stderr)
            try:
                subprocess.run(["gh", "pr", "comment", str(pr_numero), "--body-file", temp_analise_path, "--repo", repo_alvo_pr], check=True, capture_output=True, text=True, encoding='utf-8', cwd=repo_path)
                print("✅ Comentário postado com sucesso.", file=sys.stderr)
            except subprocess.CalledProcessError as e:
                print(f"❌ Falha ao comentar no PR: {e.stderr}", file=sys.stderr)
            finally:
                if os.path.exists(temp_analise_path):
                    print("🧹 Limpando arquivo temporário...", file=sys.stderr)
                    os.remove(temp_analise_path)
    finally:
        if upstream_renomeado:
            print("🔧 Restaurando nome do remote 'upstream'...", file=sys.stderr)
            subprocess.run(["git", "remote", "rename", "upstream_temp", "upstream"], cwd=repo_path, check=True, capture_output=True)

def main_pr_origin():
    """Ponto de entrada para criar um PR no 'origin'."""
    run_pr_logic(target_selecionado="origin")

def main_pr_upstream():
    """Ponto de entrada para criar um PR no 'upstream'."""
    run_pr_logic(target_selecionado="upstream")