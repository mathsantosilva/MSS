import re
from github import Github

class VersioningService:
    def __init__(self, gh: Github):
        self.gh = gh

    def comparar_tags(self, tag1: str, tag2: str) -> int:
        rx = r"(\d+)\.(\d+)\.(\d+)"
        m1, m2 = re.match(rx, tag1), re.match(rx, tag2)
        if not (m1 and m2): return 0
        v1, v2 = tuple(map(int, m1.groups())), tuple(map(int, m2.groups()))
        return (v1 > v2) - (v1 < v2)

    def pesquisar_maior_tag(self, username: str, repository: str, tag_atual: str, popup) -> str | None:
        try:
            repo = self.gh.get_repo(f"{username}/{repository}")
            maior = None
            for t in repo.get_tags():
                tag = t.name
                if self.comparar_tags(tag, tag_atual) > 0 and (maior is None or self.comparar_tags(tag, maior) > 0):
                    maior = tag
            return maior
        except Exception as e:
            popup(f"Erro ao consultar tags para atualização: {e}")
            return None
