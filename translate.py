import asyncio
from googletrans import Translator

async def main():
    translator = Translator()
    result = await translator.translate('I am the biggest app developer in the world', dest='de')
    print(result.text)

asyncio.run(main())
