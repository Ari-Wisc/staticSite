import os
import shutil

from inline_markdown import markdown_to_html_node
def extract_title(markdown):
    # Split the markdown by lines
    lines = markdown.splitlines()
    
    # Loop through the lines to find the first h1 header (line starting with a single '#')
    for line in lines:
        # Check if the line is an h1 header (starts with a single '#')
        if line.startswith('# '):
            # Return the header text, removing the '#' and leading/trailing whitespaces
            return line[2:].strip()
    
    # If no h1 header was found, raise an exception
    raise ValueError("No h1 header found in the markdown")
import os

def generate_page(from_path, template_path, dest_path):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    
    # Read the markdown content
    with open(from_path, 'r') as markdown_file:
        markdown_content = markdown_file.read()
    
    # Read the template content
    with open(template_path, 'r') as template_file:
        template_content = template_file.read()
    
    # Convert markdown to HTML
    html_node = markdown_to_html_node(markdown_content)  # Assume this function is already implemented
    html_content = html_node.to_html()
    
    # Extract the title
    title = extract_title(markdown_content)  # Assume this function is already implemented
    
    # Replace placeholders in the template with actual content
    full_html = template_content.replace('{{ Title }}', title).replace('{{ Content }}', html_content)
    
    # Create directories if they don't exist
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    
    # Write the generated HTML to the destination path
    with open(dest_path, 'w') as dest_file:
        dest_file.write(full_html)
    
    print(f"Page generated at {dest_path}")

def copy_directory_contents(src, dst):
    """
    Recursively copies all the contents from the source directory to the destination directory.
    Ensures that the destination directory is empty before copying.
    
    Args:
        src (str): The source directory path.
        dst (str): The destination directory path.
    """
    # Ensure destination directory is empty
    if os.path.exists(dst):
        shutil.rmtree(dst)
    os.makedirs(dst)

    # Loop through the source directory contents
    for item in os.listdir(src):
        source_item = os.path.join(src, item)
        destination_item = os.path.join(dst, item)

        if os.path.isdir(source_item):
            # If it's a directory, recursively copy its contents
            print(f"Copying directory: {source_item} to {destination_item}")
            os.makedirs(destination_item)  # Create the directory at destination
            copy_directory_contents(source_item, destination_item)  # Recursive call
        elif os.path.isfile(source_item):
            # If it's a file, copy it
            print(f"Copying file: {source_item} to {destination_item}")
            shutil.copy(source_item, destination_item)
def generate_pages_recursive(dir_path_content, template_path, dest_dir_path):
    print(f"Generating pages from {dir_path_content} to {dest_dir_path} using {template_path}")
    
    # Crawl the content directory recursively
    for root, dirs, files in os.walk(dir_path_content):
        for file in files:
            if file.endswith('.md'):  # Process markdown files only
                # Construct the full path to the markdown file
                markdown_path = os.path.join(root, file)
                
                # Construct the relative path from the content folder
                relative_path = os.path.relpath(markdown_path, dir_path_content)
                
                # Replace the .md extension with .html for the destination file
                dest_file_path = os.path.join(dest_dir_path, relative_path.replace('.md', '.html'))
                
                # Create any necessary directories in the destination path
                os.makedirs(os.path.dirname(dest_file_path), exist_ok=True)
                
                # Generate the HTML page
                generate_page(markdown_path, template_path, dest_file_path)
                print(f"Generated {dest_file_path}")
                
def main():
    # Define source and destination directories
    src_directory = 'static'  # Source directory
    dst_directory = 'public'  # Destination directory
    
    # Call the function to copy directory contents
    copy_directory_contents(src_directory, dst_directory)
    generate_pages_recursive('content', 'template.html', 'public')


if __name__ == "__main__":
    main()
