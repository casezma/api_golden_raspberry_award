# API Pior Filme do Golden Raspberry Awards 

Esta aplicação foi feita com Django.

## Importação de Arquivos CSV

Por padrão o diretório de 'produção', está dentro de **csv/production** e os de teste estão em **csv/tests** (onde contem diferentes bases de dados que foram usadas para os testes.)


## Execução da Aplicação

Para executar a aplicação no modo **'produção'**, basta executar o seguinte comando:

```
    docker-compose up
```

Acesso a API (Django Rest Framework)

http://127.0.0.1:8000/api/v1/prizes_interval

Para executar os **testes**, basta executar o seguinte comando:

```
    docker-compose -f docker-compose-test.yml up 
```




