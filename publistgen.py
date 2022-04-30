#!/usr/bin/env python3

import os
import sys
import argparse
import textwrap
from pathlib import Path

import logging


BIBLIB_DIR = os.path.join(os.path.dirname(Path(__file__).resolve()), 'biblib')
sys.path.append(BIBLIB_DIR)


try:
    import biblib.bib
    import biblib.algo
except ModuleNotFoundError as ex:
    logging.DEBUG(ex, file=sys.stderr)
    logging.DEBUG(textwrap.dedent(f"""
    Error: could not load the 'biblib' library.
    To fix this do *one* of the following:

    First Option: install clone 'biblib' locally by running:

        git clone https://github.com/aclements/biblib {BIBLIB_DIR.rstrip('/')}/

    Second Option: install 'publistgen' by running: python setup.py install

    """), file=sys.stderr)
    sys.exit(1)

author_homepages = {}

def load_bib(bibtex_filehandle):
    try:
        # Load databases
        parser = biblib.bib.Parser()
        db = parser.parse(bibtex_filehandle,
                          log_fp=sys.stderr)
        db = db.get_entries()
        db = biblib.bib.resolve_crossrefs(db)
        return db
    except biblib.messages.InputError as ex:
        logging.DEBUG(ex)
        sys.exit(1)


def html_encode(source):
    return source.replace('<', '&lt;').replace('>', '&gt;')


def month2int(texmonth):
    month_names = 'jan feb mar apr may jun jul aug sep oct nov dec'.split(' ')
    try:
        return 1 + month_names.index(str(texmonth)[0:3].lower())
    except ValueError:
        return int(texmonth)

def bibentry2html(ent):
    global auth_urls
    
    # authors
    authors = [
        biblib.algo.tex_to_unicode(author.pretty(),
                                   pos=ent.field_pos['author'])
        for author in ent.authors()]
    
    auth_urls = []
    for a in authors:
        # add custom links for authors
        if a in author_homepages:
            hp = author_homepages[a]
            auth_urls.append('<a target="_blank" href="{}">{}</a>'.format(hp, a))
        else:
            auth_urls.append(a)
    
    # format the citation
    pubplace = "???"
    for pp in ['journal', 'booktitle']:
        if pp in ent:
            pubplace = '<i>' + ent[pp] + '</i>'
            break
    if 'volume' in ent:
        pubplace += ", " + ent['volume']
    if 'issue' in ent:
        pubplace += ", " + ent['issue']
    if 'pages' in ent:
        pubplace += ", pp. " + ent['pages']
    # if 'note' in ent:
    #     pubplace += " ({})".format(ent['note'])
    extraurls = ""
    if 'url' in ent:
        extraurls += ' <a class="button" href="{}">PDF</a>'.format(ent['url'])
    if 'prelogging.infourl' in ent:
        extraurls += ' <a class="button" href="{}">Prelogging.info PDF</a>'.format(ent['prelogging.infourl'])
    if 'doi' in ent:
        doi = ent['doi']
        extraurls += ' <a class="custombutton buttondoi" href="https://dx.doi.org/{}" target="_blank" rel="noopener noreferrer">DOI</a>'.format(doi)
        
    if 'doi' in ent:
        formatvars = {
            'mainurl': f"https://dx.doi.org/{doi}",
            'title': biblib.algo.tex_to_unicode(ent['title']),
            'bibsource': html_encode(ent.to_bib(month_to_macro=False,wrap_width=None)),
            # join all the authors together
            'authors': ', '.join(auth_urls),
            'short_authors': ', '.join(auth_urls[:5]),
            'extraurls': extraurls,
            'pubplace': biblib.algo.tex_to_unicode(pubplace.replace('\\ ', ' ')),
        }
    else:
        raise Exception("Need to have DOI, can't be bothered to account for this sorry")
    
    # inject the variables into the html
    #! I want to make this foldable, so work on class="authors"
    s = """\
     <span class="title"><a href="{mainurl}" target="_blank" rel="noopener noreferrer">{title}</a></span>
     <br>
     <span class="shortAuthors">{short_authors} <a class="button" style="cursor: pointer;" onClick="expandAuthors(this)">(et al.)</a></span>
     <span class="longAuthors">{authors}<a class="button" style="cursor: pointer;" onClick="expandAuthors(this)"> (collapse)</a></span>
     <span class="journal">{pubplace}</span>
     <br>
     <span class="buttonline">
     <a class="custombutton" style="cursor: pointer;" onClick="showBibHere(this);">Cite</a>
     {extraurls}
     </span>
     <pre class="bibhidden">
{bibsource}</pre>
    """.format(**formatvars)
    return s


def bibliography2html(db, year2bibs, css_string, js_string):
    logging.info('<div class="publicationlist">')
    logging.info("<style>\n{}</style>".format(css_string))
    logging.info("<script>\n{}</script>".format(js_string))
    entrynumber = len(db.values())
    for y in sorted(list(year2bibs.keys()), reverse=True):
        entries = year2bibs[y]
        entries = sorted(entries, reverse=True, key=lambda e: month2int(e.get('month', 0)))
        logging.info("<h3>{}</h3>".format(y))
        logging.info('<table cellspacing="0" class="yeartable">')

        for e in entries:
            logging.info(f"""
            <tr id="{e.key}">
             <td class="bibitemtext" valign="center">{bibentry2html(e)}</td>
            </tr>
            """)
            entrynumber -= 1
        logging.info("</table>")
    logging.info(textwrap.dedent("""
     <div class="footnotecomment">
      generated by <a target="_blank" rel="noopener noreferrer" href="https://github.com/rlaker/publications-for-website">publications-for-website</a> which was forked from <a target="_blank" rel="noopener noreferrer" href="https://github.com/t-wissmann/publistgen">t-wissmann</a>
     </div>
    </div> <!-- end of publicationlist -->
    """))

def main():
    parser = argparse.ArgumentParser(
            description='generate a static publication list from bibtex',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('BIBTEX',
                        help='input bibtex file')
    parser.add_argument('--output',
                        default='publications.html',
                        help='Output filename')
    parser.add_argument('--escape', '-e',
                        action = argparse.BooleanOptionalAction,
                        help='escape injection from Jekyll static site builder')
    parser.add_argument('--yaml', '-y',
                        action = argparse.BooleanOptionalAction,
                        help='Insert yaml frontmatter')
    args = parser.parse_args()

    # sets up the logger, which just prints to file
    logging.basicConfig(filename=args.output, level=logging.DEBUG, format='', filemode='w')

    if args.yaml:
        logging.info('---\nlayout: archive\ntitle: "Publications"\npermalink: /publications/\nauthor_profile: true\n---')
    if args.escape:
        logging.info("{% raw %}")
    
    # get the css string
    with open("pubs.css", "r") as file:
        css_string = file.read()
    # get the js string
    with open("pubs.js", "r") as file:
        js_string = file.read()

    with open(args.BIBTEX) as fh:
        db = load_bib(fh)
        #logging.info(db)
        year2bibs = { }
        for ent in db.values():
            year = ent['year']
            if year in year2bibs:
                year2bibs[year].append(ent)
            else:
                year2bibs[year] = [ent]
        bibliography2html(db, year2bibs, css_string, js_string)
        
    if args.escape:
        logging.info("{% endraw %}")

if __name__ == "__main__":
    main()
