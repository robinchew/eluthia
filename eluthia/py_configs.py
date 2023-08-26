def deb822(d):
    # https://manpages.debian.org/testing/dpkg-dev/deb822.5.en.html
    return '\n'.join(
        f'{k}: {v}'
        for k, v in d.items()
    ) + '\n'
