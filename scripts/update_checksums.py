"""Normalize release text and refresh or check the package hash manifests."""
import argparse
import csv
import hashlib
import io
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IGNORED_DIRS = {'.git', '.venv', 'venv', '__pycache__', '.pytest_cache', 'reproduced'}
IGNORED_NAMES = {'.DS_Store', 'Thumbs.db', 'desktop.ini'}
TEXT_SUFFIXES = {'.md', '.txt', '.csv', '.tsv', '.json', '.py', '.cff', '.sha256'}
TEXT_NAMES = {'.gitignore', '.gitattributes', 'LICENSE', 'LICENSE-DATA'}
INDEXES = (
    ('docs/paper_artifacts.csv', 'output_file', 'sha256'),
    ('docs/file_provenance.csv', 'public_path', 'public_sha256'),
)


def release_files():
    files = []
    for path in ROOT.rglob('*'):
        rel = path.relative_to(ROOT)
        if any(part in IGNORED_DIRS for part in rel.parts):
            continue
        if path.name in IGNORED_NAMES or path.suffix in {'.pyc', '.pyo'}:
            continue
        if path.is_symlink():
            raise ValueError(f'Symlink is not a release file: {rel.as_posix()}')
        if path.is_file():
            files.append(path)
    return sorted(files, key=lambda p: p.relative_to(ROOT).as_posix())


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def target(relative):
    path = (ROOT / relative).resolve()
    if not path.is_relative_to(ROOT) or not path.is_file():
        raise ValueError(f'Missing or invalid release path: {relative}')
    return path


def index_text(path, path_column, hash_column):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames
        rows = list(reader)
    for row in rows:
        row[hash_column] = digest(target(row[path_column]))
    output = io.StringIO(newline='')
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def refresh():
    normalized = 0
    for path in release_files():
        if path.suffix in TEXT_SUFFIXES or path.name in TEXT_NAMES:
            raw = path.read_bytes()
            raw.decode('utf-8-sig')
            clean = raw.replace(b'\r\n', b'\n').replace(b'\r', b'\n')
            if clean != raw:
                path.write_bytes(clean)
                normalized += 1
    for name, path_column, hash_column in INDEXES:
        path = ROOT / name
        path.write_text(index_text(path, path_column, hash_column),
                        encoding='utf-8', newline='\n')
    lines = [f'{digest(path)}  {path.relative_to(ROOT).as_posix()}\n'
             for path in release_files() if path.name != 'checksums.sha256']
    (ROOT / 'checksums.sha256').write_text(''.join(lines), encoding='utf-8', newline='\n')
    return {'normalized_text_files': normalized, 'checksum_entries': len(lines)}


def check():
    for name, path_column, hash_column in INDEXES:
        with (ROOT / name).open(encoding='utf-8-sig', newline='') as stream:
            for row in csv.DictReader(stream):
                if row[hash_column] != digest(target(row[path_column])):
                    raise ValueError(f'{name}: hash mismatch for {row[path_column]}')
    listed = set()
    for line in (ROOT / 'checksums.sha256').read_text(encoding='utf-8').splitlines():
        expected, name = line.split('  ', 1)
        if name in listed or name == 'checksums.sha256':
            raise ValueError(f'Duplicate or self-referential checksum: {name}')
        if digest(target(name)) != expected:
            raise ValueError(f'Checksum mismatch: {name}')
        listed.add(name)
    actual = {p.relative_to(ROOT).as_posix() for p in release_files()
              if p.name != 'checksums.sha256'}
    if actual != listed:
        raise ValueError(f'Checksum coverage: unlisted={sorted(actual-listed)}, '
                         f'missing={sorted(listed-actual)}')
    for path in release_files():
        if path.suffix in TEXT_SUFFIXES or path.name in TEXT_NAMES:
            if b'\r' in path.read_bytes():
                raise ValueError(f'Text is not LF-normalized: {path.relative_to(ROOT)}')
    return len(listed)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Check without changing files.')
    args = parser.parse_args()
    if not args.check:
        result = refresh()
        print(f"Normalized {result['normalized_text_files']} text files.")
    print(f'PASS: {check()} SHA-256 entries and both provenance indexes.')


if __name__ == '__main__':
    main()
