def limpar_string(documento_inserido):
    lista_limpa = []
    for item in documento_inserido:
        sem_mascara = (
            item.replace(".", "")
                .replace(",", "")
                .replace("-", "")
                .replace("/", "")
                .replace("(", "")
                .replace(")", "")
                .strip()
        )
        lista_limpa.append(sem_mascara)
    return lista_limpa
