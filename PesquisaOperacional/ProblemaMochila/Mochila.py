import random

# Definindo a classe Item para representar os itens da mochila
class Item:
    def __init__(self, id, peso, valor):
        self.id = id
        self.peso = peso
        self.valor = valor

# Nome do arquivo contendo os itens, limite de peso da mochila e parâmetros do algoritmo genético
nomeArquivo = "itens"
limiteTransporte = 20.0
tamanhoPopulacao = 12 # Número de soluções em cada geração
tamanhoGeracao = 80 # Ao todo está definido 80 gerações
taxaMutacao = 0.1 # Implementa taxa de mutação para apenas 10% da população

# Lista que conterá os objetos Item lidos do arquivo
listaItens = []
with open(nomeArquivo, "r") as f:
    for linha in f:
        novaLinha = linha.strip().split(" ")
        id, peso, valor = novaLinha[0], novaLinha[1], novaLinha[2]
        novoItem = Item(int(id), float(peso), float(valor))
        listaItens.append(novoItem)

# Função que cria uma lista chamada 'solucao, ela terá o mesmo comprimento que a lista de itens (len(listaItens))
# Cada elemento da lista será um valor aleatório 0 ou 1, representando a escolha de incluir ou não cada item na mochila
def criarSolucaoAleatoria(listaItens):
    solucao = [random.randint(0, 1) for _ in range(len(listaItens))]
    return solucao

# Função para verificar se uma solução é válida em relação ao limite de peso
def solucaoValida(listaItens, solucao, limite):
    pesoTotal = sum(listaItens[i].peso for i in range(len(solucao)) if solucao[i] == 1)
    return pesoTotal <= limite

# Função para calcular o valor total de uma solução
def calcularValor(listaItens, solucao):
    valorTotal = sum(listaItens[i].valor for i in range(len(solucao)) if solucao[i] == 1)
    return valorTotal

# Função para verificar se duas soluções são duplicadas
def verificarSolucoesDuplicadas(solucao1, solucao2):
    return all(s1 == s2 for s1, s2 in zip(solucao1, solucao2))

# Função para criar a população inicial de soluções válidas
def populacaoInicial(tamPopulacao, listaItens, limitePeso):
    populacao = []
    i = 0
    while i < tamPopulacao:
        novaSolucao = criarSolucaoAleatoria(listaItens)
        if solucaoValida(listaItens, novaSolucao, limitePeso):
            # Verifica se a nova solução é duplicada em relação às soluções existentes na população
            if not any(verificarSolucoesDuplicadas(novaSolucao, solucaoExistente) for solucaoExistente in populacao):
                # Adiciona a nova solução a população se não for uma duplicata
                populacao.append(novaSolucao)
                i += 1
    return populacao

# Função para realizar a seleção por torneio na população
def selecaoTorneio(populacao):
    concorrente1, concorrente2 = random.sample(range(len(populacao)), 2)
     # Determina o vencedor entre os dois concorrentes com base no valor da função de aptidão (calcularValor)
    vencedor = max([populacao[concorrente1], populacao[concorrente2]], key=lambda x: calcularValor(listaItens, x))
    return vencedor

# Função para realizar o crossover entre dois pais
def crossover(pai1, pai2):
    # Gera um ponto de quebra aleatório
    pontoQuebra = random.randint(0, len(pai1))
    primeiraParte = pai1[:pontoQuebra]
    segundaParte = pai2[pontoQuebra:] # Obtém a segunda parte do pai2 a partir do ponto de quebra de pai1
    filho = primeiraParte + segundaParte
    return filho if solucaoValida(listaItens, filho, limiteTransporte) else crossover(pai1, pai2)

# Função para realizar a mutação em um cromossomo
def mutacao(cromossomo):
    # Cria uma cópia temporária do cromossomo para evitar modificar o original
    temp = cromossomo.copy()
    # Seleciona dois índices de mutação aleatório
    indiceMutacao1, indiceMutacao2 = random.sample(range(len(cromossomo)), 2)
    # Realiza a troca dos valores nos índices selecionados
    temp[indiceMutacao1], temp[indiceMutacao2] = temp[indiceMutacao2], temp[indiceMutacao1]
    return temp if solucaoValida(listaItens, temp, limiteTransporte) else mutacao(cromossomo)

# Função para criar uma nova geração a partir da população atual
def criarGeracao(populacao, taxaMutacao):
    novaGeracao = []
    for _ in range(len(populacao)):
        # Seleciona dois pais usando o método de seleção por torneio
        pai1, pai2 = selecaoTorneio(populacao), selecaoTorneio(populacao)
        filho = crossover(pai1, pai2)
         # Aplica mutação no filho com probabilidade dada pela taxa de mutação
        if random.random() < taxaMutacao:
            filho = mutacao(filho)
        novaGeracao.append(filho)
    return novaGeracao

# Função para encontrar a melhor solução em uma geração
def melhorSolucao(geracao, listaItens):
    melhor = 0
    # Itera sobre todas as soluções na geração
    for i in range(len(geracao)):
        temp = calcularValor(listaItens, geracao[i])
        if temp > melhor:
            melhor = temp
    return melhor

# Lista para armazenar os valores das melhores soluções em cada geração
listaValores = [] 

# Função principal que implementa o algoritmo genético
def algoritmoGenetico(limiteTransporte, tamPopulacao, tamGeracao, taxaMutacao, listaItens):
    pop = populacaoInicial(tamPopulacao, listaItens, limiteTransporte)
    
    # Inicializa variáveis para acompanhar a melhor solução global e seu valor
    melhor_global = None
    melhor_valor_global = 0
    
    # Itera sobre as gerações do algoritmo genético
    for i in range(tamGeracao):
        pop = criarGeracao(pop, taxaMutacao)
        
        # Encontra o melhor indivíduo na geração atual
        melhor_individuo = max(pop, key=lambda x: calcularValor(listaItens, x))
        valor_melhor_individuo = calcularValor(listaItens, melhor_individuo)
        
        print(f'Melhor indivíduo da geração {i + 1}: {melhor_individuo} | Valor: {valor_melhor_individuo}')
        
        listaValores.append(valor_melhor_individuo)
        
        # Atualiza a melhor solução global se a solução atual for melhor
        if valor_melhor_individuo > melhor_valor_global:
            melhor_global = melhor_individuo
            melhor_valor_global = valor_melhor_individuo

    # Retorna a melhor solução global e a lista de valores ao longo das gerações
    return melhor_global, listaValores

# Chamada da função principal para executar o algoritmo genético
melhor_global, listaValores = algoritmoGenetico(limiteTransporte=limiteTransporte,
                                                tamPopulacao=tamanhoPopulacao,
                                                tamGeracao=tamanhoGeracao,
                                                taxaMutacao=taxaMutacao,
                                                listaItens=listaItens)

# Exibição da melhor solução encontrada
print(f'Melhor solução global: {melhor_global} | Valor: {calcularValor(listaItens, melhor_global)}')
