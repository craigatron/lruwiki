import wikipedia

def get_lru():
    # tuple of (title, id, timestamp)
    oldest_articles = []
    count = 0
    ignore_ids = load_disambiguation_ids()
    with open('enwiki-latest-stub-meta-current.xml', encoding='utf-8') as f, \
         open('disambiguation-ids.txt', 'a+') as disambiguation_ids:
        page_lines = []
        title = None
        timestamp = None
        redirect = False
        namespace = None
        page_id = None
        seen_revision = False
        for line in f:
            line = line.strip()
            if line.startswith('<page>'):
                page_lines = []
            elif line.startswith('</page>'):
                count += 1
                if not redirect and namespace == '0' and int(timestamp[0:4]) < 2015 and not int(page_id) in ignore_ids and (not oldest_articles or (len(oldest_articles > 0) and len(oldest_articles) < 200) or timestamp < oldest_articles[-1][2]):
                    try:
                        if is_disambiguation(title, page_id):
                            disambiguation_ids.write(f'{page_id}\n')
                        else:
                            print(f'new oldest: {title}, {timestamp} ({len(oldest_articles)} entries)\n{page_lines}')
                            oldest_articles.append((title, page_id, timestamp))
                            oldest_articles.sort(key=lambda x: x[2])
                            oldest_articles = oldest_articles[:200]
                            print(f'current winner: {oldest_articles[0]}, loser: {oldest_articles[-1]}')
                    except wikipedia.exceptions.DisambiguationError:
                        disambiguation_ids.write(f'{page_id}\n')
                        print(f'{title} is a disambiguation, moving on (current count {count})')
                    except Exception as e:
                        print(f'failed at {page_lines}')
                        raise e

                title = None
                timestamp = None
                redirect = False
                namespace = None
                page_id = None
                seen_revision = False
            elif line.startswith('<title>'):
                title = line[7:-8]
            elif line.startswith('<timestamp>'):
                timestamp = line[11:-12]
            elif line.startswith('<redirect'):
                redirect = True
            elif line.startswith('<ns>'):
                namespace = line[4:5]
            elif not seen_revision and line.startswith('<id>'):
                page_id = int(line[4:-5])
            elif line.startswith('<revision>'):
                seen_revision = True
                
            page_lines.append(line)

    print(f'{oldest_articles}\nprocessed {count} records')


def load_disambiguation_ids():
    ids = set()
    with open('disambiguation-ids.txt') as f:
        for line in f:
            d_id = int(line.strip())
            ids.add(d_id)
    return ids


def is_disambiguation(title, page_id):
    if title.endswith('(disambiguation)'):
        return True
    try:
        page = wikipedia.page(pageid=page_id)
        print(f'Checking disambiguation for {title}: {page.categories}')
        return any([x in page.categories for x in ['All disambiguation pages', 'All set index articles', 'All stub articles']])
    except wikipedia.exceptions.DisambiguationError:
        print(f'{title} is a disambiguation, set index, or stub, continuing')
        return True


if __name__ == '__main__':
    get_lru()