import random
import string
for i in range(100):
    print(''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6)))