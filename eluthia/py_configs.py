def deb822(d):
    # https://manpages.debian.org/testing/dpkg-dev/deb822.5.en.html
    return '\n'.join(
        f'{k}: {v}'
        for k, v in d.items()
    ) + '\n'

INDENT_SIZE = 4

def format_nginx_conf(conf, indent_size, indent_multiplier=0):
    def indent(num):
        return lambda s: (' ' * num) + s
    indentx = indent(indent_multiplier * indent_size)

    def block(s):
        return '{\n' + s + indentx('}\n')

    first_few = conf[0:-1]
    last = conf[-1] if len(conf) >= 2 else None

    if last and type(last) is tuple:
        last_part = block(''.join(
            format_nginx_conf(item, indent_size, indent_multiplier + 1)
            for item in last))

        s = ' '.join(map(str,
            first_few +
            (last_part,)))
    else:
        s = ' '.join(map(str, conf)) + ';\n'

    return indentx(s)

def nginx(tuples):
    return '\n'.join(format_nginx_conf(tup, INDENT_SIZE) for tup in tuples)

def cron_line(command, minute = '*', hour = '*', date = '*', month = '*', weekday ='*', user = 'root'):
    return ' '.join(map(str, (minute, hour, date, month, weekday, user))) + ' ' + command

def cron(lines):
    return '\n'.join(cron_line(**d) for d in lines)
