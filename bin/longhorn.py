# In AD/Antora the xrefs need to be absolute from the root
# where $whatever/modules/ROOT/pages is defined as the root.
# So, ../deploy/accessing-the-ui/longhorn-ingress would map to
# /deploy/accessing-the-ui/longhorn-ingress.adoc. But,
# ../accessing-the-ui (if index.adoc exists)
# would be ../accessing-the-ui/index.adoc

# This is quite possibly mostly LH/Hugo specific, but it's a start.

# 1 get link
# 2 if the link begins with # then it's internal to the page, so ignore
# 3 remove and keep any anchor (a # followed by any characters)
# 4 does link/index.adoc exists (LH/Hugoism)
# 5 if so that is the target link, link = link + '/index.adoc' (LH/Hugoism)
# 6 if not then link.adoc is the target link (Normally the case)
# 7 map link to project root.
# 8 add back any anchor
# 9 if the link already ends with adoc then skip

import sys
import re
import os

debug = True


def dprint(*args, **kwargs):
    if debug:
        print(*args, **kwargs)


def ad_ify_link(fn, ad):
    link_text_re = r'xref_to_replace:(?P<xr>.*?)(?:\s|\[)'
    # matches = re.finditer(link_text_re, ad)

    while True:
        # This is necessary as after every match and replace the
        # start and end of the next one might change so using finditer
        # doesn't quite work.
        match = re.search(link_text_re, ad)
        if match is None:
            return ad
        full_link = match.group('xr')
        if full_link[0] == '#':
            continue
        match_start = match.start()
        match_end = match.end() - 1
        dprint(f"Match starts and ends at {match_start} and {match_end}")

        # Check for anchor
        anchor_re = r'(?P<anc>#.*)'
        anc_match = re.search(anchor_re, full_link)
        if anc_match:
            anchor = anc_match.group('anc')
        else:
            anchor = ''

        # Remove the anchor from the full link text
        full_link = re.sub(anchor, '', full_link)

        # If full_link is '' then we are working on an anchor to an
        # index.adoc in the current directory
        if full_link == '':
            full_link = './index.adoc' + anchor
        else:
            full_path = os.path.realpath(full_link)
            dprint(f"full_path: {full_path}")
            # Is this really a Longhorn index file?
            test_path = full_path + '/index.adoc'
            if os.path.isfile(test_path):
                full_path = test_path
            else:
                # Check to see if '.adoc' is already there so repeated runs
                # and manual fixes don't keep getting multiple '.adoc's
                # added.
                if re.search(r'\.adoc$ ', full_path) is not None:
                    continue
                else:
                    full_path = full_path + '.adoc'
                    dprint(f"full_path: {full_path}")

            full_link = full_path + anchor
            dprint(f"full_link: {full_link}")

        # Normalize to doc root by removing '^.*/modules/.*/pages/'
        # from full_link
        full_link = re.sub(
            r'^.*/modules/.*/pages/', '', full_link)
        dprint(f"Normalized full_link: {full_link}")
        full_link = 'xref:' + full_link

        # Finally replace the original link with the new one
        ad = ad[:match_start] + full_link + ad[match_end:]


def fig2img(adt):
    p = r'{{<\s+figure\s+(?:(?:(?:alt=\"(?P<alt>.+?)\")\s+)'
    p = p + r'?src=\"(?P<src>.+?)\"(?:\s+alt=\"(?P<alt2>.+?)\")?)?\s*>}}'
    matches = re.finditer(p, adt)

    for match in matches:
        alt = match.group('alt') or match.group('alt2') or 'Image'
        src = match.group('src')
        src = src.replace('/img/', '')
        adt = adt.replace(match.group(0), f'image::{src}[{alt}]')

    return adt


def main():
    if len(sys.argv) != 2:
        print("Usage: python longhorn.py input.adoc")
        sys.exit(1)

    ad_file = sys.argv[1]

    with open(ad_file, 'r', encoding='utf-8') as f:
        ad_in = f.read()
        f.close()

    # Need to be in the adoc files directory to text links
    this_dir = os.getcwd()
    try:
        dprint(f"ad_file: {ad_file}")
        dir_fn = os.path.dirname(ad_file)
        dprint(f"dir_fn: {dir_fn}")
        os.chdir(dir_fn)
    except Exception:
        print("Error changing directory to adoc file location")
        sys.exit(1)

    ad_out = ad_ify_link(ad_file, ad_in)
    ad_out = fig2img(ad_out)

    try:
        os.chdir(this_dir)
    except Exception:
        print("Error changing directory back to working directory")
        sys.exit(1)

    with open(ad_file, 'w', encoding='utf-8') as f:
        f.write(ad_out)
        f.close()


if __name__ == "__main__":
    main()
