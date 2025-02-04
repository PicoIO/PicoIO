from Url_encode import url_encode

url=url_encode()

some_api='https://wpmsg.com/?text='

string_to_be_url_encoded='This is a message'

encoded_string=url.encode('string_to_be_url_encoded')
url_to_be_decoded=some_api+encoded_string

decoded_url=url.decode(url_to_be_decoded)

print('URL:',some_api+encoded_string)
print('\nThe encoded string is:',encoded_string)
print('\nThe decoded URL is:',decoded_url)