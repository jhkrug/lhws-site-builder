# Now all the links need to be absolute links from the root
# Where $whatever/modules/ROOT/pages is defined as the root.
# So, ../deploy/accessing-the-ui/longhorn-ingress would map to
# /deploy/accessing-the-ui/longhorn-ingress.adoc. But,
# ../accessing-the-ui (if index.adoc exists)
# would be ../accessing-the-ui/index.adoc

# 1 get link
# 2 if the link begins with # then it's internal to the page, so ignore
# 3 remove and keep any anchor (a # followed by any characters)
# 4 does link/index.adoc exists
# 5 if so that is the target link
# 6 if not then link.adoc is the target link
# 7 map link, changing to xref, to project root.
# 8 add back any anchor

import sys
import re
import os


def ad_ify_link(doc_root, fn, ad):
    link_text_re = r'xref:(?P<xr>.*?)(?:\s|\[)'
    matches = re.finditer(link_text_re, ad)

    for match in matches:
        full_link_text = match.group('xr')

        # Check for anchor
        anchor_re = r'#(?P<anc>.*?)(?:\s|\[)'
        anchor_re = r'(?P<anc>#.*)'
        anc_match = re.search(anchor_re, full_link_text)
        if anc_match:
            anchor = anc_match.group('anc')
        else:
            anchor = ''

        # Remove the anchor from the full link text
        full_link_text = re.sub(anchor, '', full_link_text)

        # If full_link_text is '' then we are working on an anchor to an
        # index.adoc in the current directory
        if full_link_text == '':
            full_link_text = './index.adoc' + anchor
        else:
            try:
                os.chdir(os.path.dirname(fn))
                full_path = os.path.realpath(full_link_text)
                # Is this a Longhorn index file?
                test_path = full_path + '/index.adoc'
                if os.path.isfile(test_path):
                    full_path = test_path
                else:
                    full_path = full_path + '.adoc'
            except Exception:
                print("Error changing directory")
                sys.exit(1)

            full_link_text = full_path + anchor

        # Normalize to doc root
        full_link_text = re.sub(doc_root, '', full_link_text)
        print(full_link_text)

        # Finally replace the original link with the new one
        ad = ad.replace(match.group('xr'), full_link_text)

    return ad


def main():
    if len(sys.argv) != 2:
        print("Usage: python longhorn.py input.adoc")
        sys.exit(1)

    ad_file = sys.argv[1]

    with open(ad_file, 'r', encoding='utf-8') as f:
        ad_in = f.read()
        f.close()

    doc_root = '/home/jhk/projects/suse/longhorn-admig/longhorn-ws-ad/modules/ROOT/pages/'
    ad_out = ad_ify_link(doc_root, ad_file, ad_in)

    with open(ad_file, 'w', encoding='utf-8') as f:
        f.write(ad_out)
        f.close()


if __name__ == "__main__":
    main()
