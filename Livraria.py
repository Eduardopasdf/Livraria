import sqlite3
import csv
import os
import shutil
from pathlib import Path
from datetime import datetime


def criar_tabela(cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS livros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            autor TEXT NOT NULL,
            ano_publicacao INTEGER NOT NULL,
            preco REAL NOT NULL
        )
    ''')

def adicionar_livro(conn, cursor):
    titulo = input("Digite o título do livro: ")
    autor = input("Digite o autor do livro: ")

    try:
        ano_publicacao = int(input("Digite o ano de publicação: "))
        preco = float(input("Digite o preço do livro: "))
    except ValueError:
        print("Erro: Ano de publicação e preço devem ser valores numéricos.")
        return

    cursor.execute(
        'INSERT INTO livros (titulo, autor, ano_publicacao, preco) VALUES (?, ?, ?, ?)',
        (titulo, autor, ano_publicacao, preco)
    )
    conn.commit()
    fazer_backup()
    print("Livro adicionado com sucesso!")


def exibir_livros(cursor):
    cursor.execute('SELECT * FROM livros')
    livros = cursor.fetchall()
    if livros:
        print("\nLista de Livros:")
        for livro in livros:
            print(f"ID: {livro[0]}, Título: {livro[1]}, Autor: {livro[2]}, Ano: {livro[3]}, Preço: {livro[4]:.2f}")
    else:
        print("Nenhum livro encontrado.")


def atualizar_preco(conn, cursor):
    titulo = input("Digite o título do livro que deseja atualizar: ")

    try:
        novo_preco = float(input("Digite o novo preço: "))
    except ValueError:
        print("Erro: O preço deve ser um número válido.")
        return

    cursor.execute('UPDATE livros SET preco = ? WHERE titulo = ?', (novo_preco, titulo))
    conn.commit()
    fazer_backup()
    print("Preço atualizado com sucesso!")


def remover_livro(conn, cursor):
    try:
        livro_id = int(input("Digite o ID do livro que deseja remover: "))

        cursor.execute('SELECT * FROM livros WHERE id = ?', (livro_id,))
        livro = cursor.fetchone()

        if livro:
            cursor.execute('DELETE FROM livros WHERE id = ?', (livro_id,))
            conn.commit()
            fazer_backup()
            print(f"Livro '{livro[1]}' removido com sucesso!")
        else:
            print("Livro não encontrado. Verifique o ID digitado.")
    except ValueError:
        print("Erro: O ID deve ser um número.")
    except Exception as e:
        print(f"Erro ao remover o livro: {e}")


def buscar_livros_por_autor(cursor):
    autor = input("Digite o nome do autor: ")
    cursor.execute('SELECT * FROM livros WHERE autor = ?', (autor,))
    livros = cursor.fetchall()
    if livros:
        print(f"\nLivros do autor {autor}:")
        for livro in livros:
            print(f"ID: {livro[0]}, Título: {livro[1]}, Ano: {livro[3]}, Preço: {livro[4]:.2f}")
    else:
        print(f"Nenhum livro encontrado para o autor {autor}.")


def exportar_para_csv(cursor):
    export_dir = Path.cwd() / 'exports'
    export_dir.mkdir(parents=True, exist_ok=True)
    csv_file = export_dir / 'livros_exportados.csv'

    try:
        cursor.execute('SELECT * FROM livros')
        livros = cursor.fetchall()

        with csv_file.open(mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(['ID', 'Título', 'Autor', 'Ano de Publicação', 'Preço'])
            for livro in livros:
                writer.writerow([livro[0], livro[1], livro[2], livro[3], f"{livro[4]:.2f}"])

        print(f"Dados exportados para {csv_file} com sucesso!")
    except Exception as e:
        print(f"Erro ao exportar para CSV: {e}")


def importar_de_csv(conn, cursor):
    csv_file = input("Digite o nome do arquivo CSV (deve estar na pasta 'exports'): ")
    csv_file_path = Path.cwd() / 'exports' / csv_file

    if not csv_file_path.exists():
        print(f"Erro: O arquivo {csv_file_path} não foi encontrado.")
        return

    fazer_backup()
    try:
        with csv_file_path.open(newline='', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=',')
            next(reader)
            for row in reader:
                if len(row) != 5:
                    print(f"Erro ao importar linha: {row}")
                    continue
                cursor.execute(
                    'INSERT INTO livros (titulo, autor, ano_publicacao, preco) VALUES (?, ?, ?, ?)',
                    (row[1], row[2], int(row[3]), float(row[4]))
                )
        conn.commit()
        print("Dados importados com sucesso!")
    except Exception as e:
        print(f"Erro ao importar CSV: {e}")


def fazer_backup():
    backup_dir = Path.cwd() / 'backups'
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_file = backup_dir / f"backup_livraria_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.db"

    try:
        shutil.copy(Path.cwd() / 'livraria.db', backup_file)
        print(f"Backup criado: {backup_file}")
        limpar_backups_antigos(backup_dir)
    except Exception as e:
        print(f"Erro ao criar backup: {e}")


def limpar_backups_antigos(backup_dir):
    try:
        arquivos = list(backup_dir.glob('*.db'))
        arquivos.sort(key=lambda x: x.stat().st_mtime)

        while len(arquivos) > 5:
            arquivos[0].unlink()
            arquivos.pop(0)
        print("Backups antigos removidos, mantendo apenas os 5 mais recentes.")
    except Exception as e:
        print(f"Erro ao limpar backups antigos: {e}")



def menu():
    db_path = Path.cwd() / 'livraria.db'

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    criar_tabela(cursor)

    while True:
        print("\nEscolha uma opção:")
        print("1. Adicionar novo livro")
        print("2. Exibir todos os livros")
        print("3. Atualizar preço de um livro")
        print("4. Remover um livro")
        print("5. Buscar livros por autor")
        print("6. Exportar dados para CSV")
        print("7. Importar dados de CSV")
        print("8. Fazer backup do banco de dados")
        print("9. Sair")

        opcao = input("Opção: ")

        if opcao == "1":
            adicionar_livro(conn, cursor)
        elif opcao == "2":
            exibir_livros(cursor)
        elif opcao == "3":
            atualizar_preco(conn, cursor)
        elif opcao == "4":
            remover_livro(conn, cursor)
        elif opcao == "5":
            buscar_livros_por_autor(cursor)
        elif opcao == "6":
            exportar_para_csv(cursor)
        elif opcao == "7":
            importar_de_csv(conn, cursor)
        elif opcao == "8":
            fazer_backup()
        elif opcao == "9":
            break
        else:
            print("Opção inválida, tente novamente.")

    conn.close()


if __name__ == "__main__":
    menu()
