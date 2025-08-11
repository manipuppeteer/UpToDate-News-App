def get_news(kategory: str) -> articles[list[dict]]:
	'''Diese Funktion ruft die API und bekommt das dictionary 'data'. Die Articles kann mit data['articles'] holen.
	Diese Funktion nimmt ein Kategory ein, z.B. Sport, Politics u.s.w und gibt die Top 5 Artikel im diesen Kategorie aus'''

#--------------------------------------------------------------	
def convert_time(time: str) -> time_hours[int]:
	'''Diese Funktion nimmt die publishing time, dass man mit articles[0]['publishedAt'] holen kann, rechnet wie viele Stunde passiert hat, zwischen jetzt und diese Zeit, und gibt es aus'''

#----------------------------------------------------------------
def such_articles(wort:str) ->articles[list[dict]]:
	
    '''Diese funktion nimmt eine Suchwort ein, gibt die Top 5 Artikel, die diese Suchwort enthalten, aus'''

#-------------------------------------------------------------
def save_to_favorites(article:dict) -> None:
    '''Diese Funktion nimmt ein artikel ein(element in der Liste 'articles') und speichert es in einem JSON datei'''

####Ubungaufgabe
def get_title(articles: list[dict]) -> list[str]:
      '''Nimmt articles ein und extrahiert die titels und gibt eine liste von titels aus'''

def get_authors(articles: list[dict]) -> list[str]:
      '''Nimmt artikels ein, gibt die Liste von authora aus'''

def get_date(articles: list[dict]) -> list[str]:
      '''Nimmt articles ein, gibt eine Liste von dates der Erscheinung aus'''

def get_time(articles: list[dict]) -> list[str]):
    '''Nimmt articles ein, gibt eine Liste von der genaue Zeit der Erscheinung aus'''

