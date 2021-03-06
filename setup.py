import setuptools


install_requires = [
    "abjad",
    "evans",
]

keywords = [
    "abjad",
    "music composition",
    "music notation",
    "formalized score control",
    "lilypond",
]

if __name__ == "__main__":
    setuptools.setup(
        author="Trinton Prater",
        author_email="trinton.k.prater@gmail.com",
        install_requires=install_requires,
        keywords=", ".join(keywords),
        name="trinton",
        packages=["trinton"],
        platforms="Any",
        url="https://github.com/tr1nt0n/trinton.git",
    )
