import os
import shutil
from flask import render_template, url_for
from app import app, get_scriptures, parse_scripture

# Configuration
BUILD_DIR = 'build'
SCRIPTURES_DIR = 'scriptures'

def main():
    """Generates the static site."""
    print("Starting static site generation...")

    if os.path.exists(BUILD_DIR):
        shutil.rmtree(BUILD_DIR)
    os.makedirs(BUILD_DIR)
    print(f"Created build directory: {BUILD_DIR}")

    # Copy static files
    static_source = 'static'
    static_dest = os.path.join(BUILD_DIR, 'static')
    if os.path.exists(static_source):
        shutil.copytree(static_source, static_dest)
        print("Copied static files.")

    with app.app_context():
        # Get the list of scriptures once
        scriptures_list = get_scriptures()

        # Render index page
        index_html = render_template('index.html', scriptures=scriptures_list)

        # Post-process links for static site compatibility
        # For index.html, convert root-relative links to simple relative links
        index_html = index_html.replace('href="/scripture/', 'href="scripture/')
        index_html = index_html.replace('href="/static/', 'href="static/')
        index_html = index_html.replace('href="/"', 'href="index.html"')

        with open(os.path.join(BUILD_DIR, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(index_html)
        print("Rendered index.html.")

        # Render scripture pages
        scripture_build_dir = os.path.join(BUILD_DIR, 'scripture')
        os.makedirs(scripture_build_dir)

        for scripture_data in scriptures_list:
            filename = scripture_data['filename']

            filepath = os.path.join(SCRIPTURES_DIR, filename + '.txt')
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            title = scripture_data['title']
            parsed_content = parse_scripture(content)

            scripture_html = render_template(
                'scripture.html',
                title=title,
                parsed_content=parsed_content,
                scriptures=scriptures_list,
                show_outline_sidebar=(len(parsed_content) > 1)
            )

            # Post-process links to be relative from the scripture page
            # e.g., /static/css/style.css -> ../../static/css/style.css
            scripture_html = scripture_html.replace('href="/scripture/', 'href="../')
            scripture_html = scripture_html.replace('href="/static/', 'href="../static/')
            scripture_html = scripture_html.replace('href="/"', 'href="../index.html"')

            # Create a directory for each scripture to allow for clean URLs like /scripture/dao_de_jing/
            scripture_dir = os.path.join(scripture_build_dir, filename)
            os.makedirs(scripture_dir)
            output_path = os.path.join(scripture_dir, 'index.html')

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(scripture_html)
            print(f"Rendered scripture/{filename}/index.html.")

    print("\nStatic site generation complete!")
    print(f"Output is in the '{BUILD_DIR}' directory.")

if __name__ == '__main__':
    main()
