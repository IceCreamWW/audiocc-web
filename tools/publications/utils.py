import bibtexparser
from pathlib import Path
import yaml
from dataclasses import dataclass

@dataclass
class Citation:
    author_: str = ""
    year_: int = 0
    title_: str = ""
    journal_: str = ""
    volume_: str = ""
    number_: str = ""
    pages_: str = ""
    publisher_: str = ""
    entry_type_: str = ""

    @property
    def frontmatter(self):
        fields = {
            "author": self.author,
            "year": self.year,
            "title": self.title,
            "journal": self.journal,
            "volume": self.volume,
            "number": self.number,
            "pages": self.pages,
            "publisher": self.publisher,
            "uid": self.uid,
            "entry_type": self.entry_type,
        }
        return "---\n" + yaml.dump(fields) + "---"

    @property
    def uid(self):
        allowed_chars = "-'`~!@#$%^&+="
        sanitized_title = "".join(c if c.isalnum() or c in allowed_chars else "#" for c in self.title)
        return sanitized_title[:250]

    @property
    def author(self):
        return self.author_

    @author.setter
    def author(self, value):
        author = value.replace("\n", " ")
        self.author_ = author

    @property
    def year(self):
        return self.year_

    @year.setter
    def year(self, value):
        try:
            self.year_ = int(value)
        except:
            self.year_ = 0

    @property
    def title(self):
        return self.title_

    @title.setter
    def title(self, value):
        value = value.replace("\n", " ")
        self.title_ = value

    @property
    def journal(self):
        return self.journal_

    @journal.setter
    def journal(self, value):
        self.journal_ = value

    @property
    def volume(self):
        return self.volume_

    @volume.setter
    def volume(self, value):
        self.volume_ = value

    @property
    def number(self):
        return self.number_

    @number.setter
    def number(self, value):
        self.number_ = value

    @property
    def pages(self):
        return self.pages_

    @pages.setter
    def pages(self, value):
        self.pages_ = value

    @property
    def publisher(self):
        return self.publisher_

    @publisher.setter
    def publisher(self, value):
        self.publisher_ = value

    @property
    def entry_type(self):
        return self.entry_type_

    @entry_type.setter
    def entry_type(self, value):
        self.entry_type_ = value

def parse_bibstring(bibtex_string):
    # Parse the BibTeX string
    bib_database = bibtexparser.loads(bibtex_string)
    citations = []
    
    for entry in bib_database.entries:
        citation = Citation()
        citation.author = entry.get('author', '')
        citation.year = int(entry.get('year', -1))
        citation.title = entry.get('title', '')
        citation.journal = entry.get('journal', '')
        citation.volume = entry.get('volume', '')
        citation.number = entry.get('number', '')
        citation.pages = entry.get('pages', '')
        citation.publisher = entry.get('publisher', '')
        citation.entry_type = entry.get('ENTRYTYPE', '')

        citations.append(citation)
    return citations

def read_frontmatter(md_file: Path):
    text = md_file.read_text()
    text = text.strip().split("---")[1]
    frontmatter = yaml.safe_load(text)
    return frontmatter

def write_frontmatter(md_file: Path, frontmatter: dict):
    text = "---\n" + yaml.dump(frontmatter) + "---\n"
    md_file.write_text(text)
