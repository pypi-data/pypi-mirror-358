# orange3-nlp-jezyk-polski

Zbiór widgetów Orange3 do przetwarzania języka naturalnego w języku polskim.

## Instalacja

W instalatorze dodatków kliknij „Dodaj więcej...” i wpisz `orange3-nlp-jezyk-polski`

## Widgety

Możesz stworzyć przepływ pracy do analizy sentymentu tekstu w języku polskim z wykorzystaniem biblioteki sentimentPL. [SentimentPL](https://github.com/philvec/sentimentPL), stworzony przez PhilVec, to model oparty na HerBERT, wytrenowany na zbiorze danych PolEmo2.0/CLARIN-PL. Zwraca ciągły wynik sentymentu w zakresie od -1 (negatywny) do +1 (pozytywny).

![Przykładowy przepływ pracy: ładowanie recenzji produktów, analiza sentymentu i wyświetlanie wyników w tabeli danych](imgs/sentiment-workflow.png)

![Tabela danych z wynikami analizy sentymentu](imgs/sentiment-output.png)
