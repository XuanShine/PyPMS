from itertools import product, combinations
lines = """8
0 61 81 26 95 80 27 90
61 0 36 23 26 13 63 51
81 36 0 24 29 86 68 24
26 23 24 0 73 72 14 41
95 26 29 73 0 17 47 71
80 13 86 72 17 0 44 28
27 63 68 14 47 44 0 35
90 51 24 41 71 28 35 0"""
n = int(lines.split('\n')[0])
# list_n = list(range(n))
# lines = lines.split('\n')
# combi = list(combinations(list_n, 2))
carte = [list(map(int, line.split())) for line in lines.split('\n')[1:]]
print(carte)
def link(x1, x2):
    # import pdb; pdb.set_trace()
    if x1 >= x2:
        return 0
    elif x1 + 1 == x2:
        return carte[x1][x2]
    elif x1 + 2 == x2:
        return max(carte[x1][x1+1], carte[x1][x2], carte[x1+1][x2])
    else:
        tmp = []
        for j in range(0, x2-x1):
            x_tmp = x1 + j
            for i in range(x_tmp, x2+1):
                tmp.append(link(x_tmp, i-1) + carte[x_tmp][i] + link(i+1, x2))
        return max(tmp)

print(link(0, n-1))
