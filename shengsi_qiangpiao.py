from http_utils import *



token=login4token()
payload = {"startPortNo":1028,"endPortNo":1017,"startDate":"2024-04-21","accountTypeId":"0"}

res = query_enq(payload, authentication=account['authentication'], token=token)


# todo: loop logic

