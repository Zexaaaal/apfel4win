import ast
import astor
import sys
import os

def remove_comments_and_docstrings(source):
    parsed = ast.parse(source)
    for node in ast.walk(parsed):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
            if (node.body and isinstance(node.body[0], ast.Expr) and 
                isinstance(node.body[0].value, ast.Constant) and 
                isinstance(node.body[0].value.value, str)):
                node.body.pop(0)
    return astor.to_source(parsed)

if __name__ == "__main__":
    for i in range(1, len(sys.argv)):
        file_path = sys.argv[i]
        if not os.path.exists(file_path): continue
        print(f"Nettoyage de {file_path}...")
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        try:
            # astor ne gère pas les commentaires # (seulement docstrings)
            # Pour les commentaires #, on va utiliser une approche plus simple par ligne
            # mais astor est plus sûr pour les docstrings.
            cleaned = remove_comments_and_docstrings(content)
            
            # Deuxième passe pour les commentaires #
            lines = cleaned.splitlines()
            final_lines = []
            for line in lines:
                if line.strip().startswith('#'):
                    continue
                # Suppression simplifiée des commentaires en fin de ligne (attention aux strings)
                # Note: Cette approche est basique, astor.to_source() retire déjà la plupart des commentaires
                final_lines.append(line)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(final_lines))
        except Exception as e:
            print(f"Erreur sur {file_path}: {e}")
