from easy_exon import get_token, MyApiClient

USERNAME='d.guzy@ano-rsi.ru'
PASSWORD='Qwerty7890!'


token = get_token(USERNAME, PASSWORD)

api = MyApiClient(token=token)

objects = api.objects.list()
print(len(objects))

for ob in objects:
    print(ob.dsCode)
