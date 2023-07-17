with open('oui.txt', encoding='utf-8', errors='replace') as f:
    lines = f.readlines()
    count = 0
    for line in lines:
        l = line.strip().split("\t")
        if line.__contains__("(hex)"):
            with open('oui_hex.txt', 'a', encoding='utf-8') as f:
                count += 1
                f.write(l[0][0:8] + "\t" + l[2] + "\n")

print(count)
