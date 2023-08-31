def encontrar_estabelecimento(estabelecimento_completo: str):
    estabelecimento = estabelecimento_completo.replace('amp;', '')
    pos = estabelecimento.find('<')
    response = estabelecimento[0:pos]
    return response


def encontrar_endereco(endereco: str):
    pos = endereco.find(' ·')
    if pos == -1:
        pos = endereco.find('<')
        response = endereco[0:pos]
        return response
    else:
        response = endereco[0:pos]
        return response


def encontrar_telefone_estabelecimento(telefone: str):
    pos = telefone.find('<')
    response = telefone[0:pos]
    return response


from playwright.sync_api import sync_playwright
from openpyxl import Workbook
from bs4 import BeautifulSoup
from time import sleep
ciclos = 1
start = 0
tem_botao = True
all_estabelecimentos = []
all_enderecos = []
all_telefones = []
lugar = str(input('Qual Estabelecimento deseja? ')).strip().lower()
cidade = str(input('De qual cidade? ')).strip().lower()
with sync_playwright() as pw:
    navegador = pw.chromium.launch(headless=True)
    google_maps = navegador.new_page()
    google_maps.set_default_timeout(120000)
    print(f'Pesquisando por "{lugar.capitalize()} em {cidade.capitalize()}"')
    google_maps.goto(f'https://www.google.com/search?sca_esv=561186545&tbs=lf:1,lf_ui:9&tbm=lcl&sxsrf=AB5stBgXov6N2_ETmGY_66proRDcusH0kg:1693360006806&q={lugar}+em+{cidade}+%2B+telefone&rflfq=1&num=10&sa=X&ved=2ahUKEwiUxLrNoYOBAxXrtpUCHffUDvsQjGp6BAgWEAE#rlfi=hd:;si:;mv:[[-15.5497494,-49.9308049],[-15.570485000000001,-49.9609993]];tbs:lrf:!1m4!1u3!2m2!3m1!1e1!1m4!1u5!2m2!5m1!1sgcid_3bars_1and_1pubs!1m4!1u5!2m2!5m1!1sgcid_3pizza_1restaurant!1m4!1u2!2m2!2m1!1e1!2m1!1e2!2m1!1e5!2m1!1e3!2m4!1e17!4m2!17m1!1e2!3sIAEqAkJS,lf:1,lf_ui:9')
    while tem_botao:
        print(f'Pegando comércios da página {ciclos}.')
        conteudo = google_maps.content()
        site = BeautifulSoup(conteudo, 'html.parser')
        with open('arquivo.txt', 'wt+', encoding='utf-8') as arquivo:
            arquivo.write(site.prettify())
        pesquisa = site.find_all('a', class_='vwVdIc wzN8Ac rllt__link a-no-hover-decoration')
        print(f'{len(pesquisa)} comércios encontrados.')
        for i, estabelecimento in enumerate(pesquisa):
            try:
                # print(pesquisa[0])
                lista_nome_estabelecimento = str(estabelecimento).split('"OSrXXb">')
                lista_endereco_estabelecimento = str(estabelecimento).split('<div>')
                lista_telefone_estabelecimento = str(lista_endereco_estabelecimento[3]).split('· ')
                # print(lista_endereco_estabelecimento[3])
                nome_estabelecimento = encontrar_estabelecimento(lista_nome_estabelecimento[1])
                endereco_estabelecimento = encontrar_endereco(lista_endereco_estabelecimento[3])
                telefone_estabelecimento = encontrar_telefone_estabelecimento(lista_telefone_estabelecimento[1])
                all_estabelecimentos.append(nome_estabelecimento)
                all_enderecos.append(endereco_estabelecimento)
                all_telefones.append(telefone_estabelecimento)
            except:
                all_estabelecimentos.append(nome_estabelecimento)
                all_enderecos.append(endereco_estabelecimento)
                all_telefones.append('Este estabelecimento não possui telefone de contato')
        botao = '<span style="display:block;margin-left:'
        if botao in site.prettify():
            google_maps.locator('xpath=//*[@id="pnnext"]/span[2]').click()
            sleep(2)
        else:
            print('Não há mais estabelecimentos, encerrando...')
            google_maps.close()
            tem_botao = False
        ciclos += 1
tabela = Workbook()
tabela.create_sheet(f'{lugar.capitalize()} em {cidade.capitalize()}')
tabela.remove(tabela['Sheet'])
tabela_page = tabela[f'{lugar.capitalize()} em {cidade.capitalize()}']
tabela_page.append(['Nome do Comércio', 'Endereço', 'Telefone para Contato'])
for i, estabelecimento in enumerate(all_estabelecimentos):
    tabela_page.append([estabelecimento, all_enderecos[i], all_telefones[i]])
tabela.save(f'{lugar.capitalize()} em {cidade.capitalize()}.xlsx')
