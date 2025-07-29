import os
import sys
import stat
import argparse
import subprocess

PRE_PUSH_CONTENT = """#!/bin/sh
set -e
echo "--- [HOOK PRE-PUSH CodeWise ATIVADO] ---"
codewise-pr
echo "--- [HOOK PRE-PUSH CodeWise CONCLUÍDO] ---"
exit 0
"""

PRE_COMMIT_CONTENT = """#!/bin/sh
set -e
echo "--- [HOOK PRE-COMMIT CodeWise ATIVADO] ---"
codewise-lint
echo "--- [HOOK PRE-COMMIT CodeWise CONCLUÍDO] ---"
exit 0
"""
def verificar_remote_existe(remote_name):
    """Verifica se um remote com o nome especificado existe."""
    try:
        # Assumimos que o comando roda do diretório raiz do repo
        repo_path = os.getcwd() 
        remotes = subprocess.check_output(["git", "remote"], cwd=repo_path, text=True, encoding='utf-8')
        return remote_name in remotes.split()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_hook(hook_name, hook_content, repo_root):
    hooks_dir = os.path.join(repo_root, '.git', 'hooks')
    if not os.path.isdir(hooks_dir):
        print(f"❌ Erro: Diretório de hooks do Git não encontrado em '{hooks_dir}'.", file=sys.stderr)
        return False
    
    hook_path = os.path.join(hooks_dir, hook_name)
    try:
        with open(hook_path, 'w', newline='\n') as f:
            f.write(hook_content)
        st = os.stat(hook_path)
        os.chmod(hook_path, st.st_mode | stat.S_IEXEC)
        print(f"✅ Hook '{hook_name}' instalado com sucesso.")
        return True
    except Exception as e:
        print(f"❌ Erro ao instalar o hook '{hook_name}': {e}", file=sys.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(description="Instalador de hooks do CodeWise.")
    parser.add_argument('--commit', action='store_true', help='Instala o hook pre-commit.')
    parser.add_argument('--push', action='store_true', help='Instala o hook pre-push.')
    parser.add_argument('--all', action='store_true', help='Instala ambos os hooks.')
    args = parser.parse_args()

    print("🚀 Iniciando configuração de hooks do CodeWise...")
    repo_root = os.getcwd()
    
    if not any([args.commit, args.push, args.all]):
        print("Nenhum hook especificado. Use --commit, --push, ou --all.", file=sys.stderr)
        sys.exit(1)

    # Instala o hook pre-commit (não muda)
    if args.commit or args.all:
        install_hook('pre-commit', PRE_COMMIT_CONTENT, repo_root)

    # --- LÓGICA INTELIGENTE PARA O HOOK PRE-PUSH ---
    if args.push or args.all:
        push_command = "codewise-pr-origin" # Padrão seguro

        # Só pergunta se o 'upstream' existir
        if verificar_remote_existe('upstream'):
            print("\n🎯 Um remote 'upstream' foi detectado.")
            print("   Qual deve ser o comportamento padrão do 'git push' para este repositório?")
            print("   1: Criar Pull Request no 'origin' (seu fork)")
            print("   2: Criar Pull Request no 'upstream' (projeto principal)")
            
            while True:
                try:
                    escolha = input("Escolha o padrão (1 ou 2): ").strip()
                    if escolha == '1':
                        push_command = "codewise-pr-origin"
                        break
                    elif escolha == '2':
                        push_command = "codewise-pr-upstream"
                        break
                    else:
                        print("Opção inválida. Por favor, digite 1 ou 2.")
                except (KeyboardInterrupt, EOFError):
                    print("\nInstalação do hook pre-push cancelada.")
                    sys.exit(1)
        
        # Cria o conteúdo do hook com o comando escolhido
        pre_push_content_dinamico = f"""#!/bin/sh
set -e
echo "--- [HOOK PRE-PUSH CodeWise ATIVADO (Alvo: {push_command.split('-')[-1]})] ---"
{push_command}
echo "--- [HOOK PRE-PUSH CodeWise CONCLUÍDO] ---"
exit 0
"""
        install_hook('pre-push', pre_push_content_dinamico, repo_root)

    print("\n🎉 Configuração concluída!")