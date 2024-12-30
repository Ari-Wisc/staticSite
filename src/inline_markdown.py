import re

from textnode import TextNode, TextType
from htmlnode import HTMLNode, LeafNode, ParentNode


def text_to_children(text):
    inline_nodes = []

    # If there are no inline elements (bold, italic, code), return the text directly
    if not any(marker in text for marker in ["**", "*", "`"]):
        return [LeafNode(None, text)]  # Directly add the text without wrapping in a span

    # Process for inline markdown: bold (**), italic (*), and code (`).
    
    # Handle **bold**
    while "**" in text:
        before, bold_text, after = text.split("**", 2)
        inline_nodes.append(LeafNode("span", before))
        inline_nodes.append(LeafNode("strong", bold_text))
        text = after

    # Handle *italic*
    while "*" in text:
        before, italic_text, after = text.split("*", 2)
        inline_nodes.append(LeafNode("span", before))
        inline_nodes.append(LeafNode("em", italic_text))
        text = after

    # Handle `code`
    while "`" in text:
        before, code_text, after = text.split("`", 2)
        inline_nodes.append(LeafNode("span", before))
        inline_nodes.append(LeafNode("code", code_text))
        text = after

    # Add any remaining text (if there is anything left)
    if text:
        inline_nodes.append(LeafNode("span", text))

    return inline_nodes

def markdown_to_html_node(markdown):
    # Step 1: Split the markdown into blocks
    blocks = markdown_to_blocks(markdown)
    
    # Step 2: Create the parent HTMLNode
    parent_node = ParentNode("div", [])
    
    # Step 3: Loop through each block, determine the type, and create appropriate HTMLNode
    for block in blocks:
        block_type = block_to_block_type(block.strip())  # Determine block type
        block_node = None
        
        if block_type == "heading":
            # Heading with level based on the number of `#`
            level = block.count("#")  # Number of '#' indicates level
            block_node = LeafNode(f"h{level}", block.strip("#").strip())
        
        elif block_type == "code":
            # Code block inside <pre><code>
            block_node = ParentNode("pre", [LeafNode("code", block.strip("`"))])
        
        elif block_type == "quote":
            # Quote block inside <blockquote>
            block_node = LeafNode("blockquote", block.strip(">").strip())
        
        elif block_type == "unordered_list":
            # Unordered list inside <ul>
            ul_node = ParentNode("ul", [])
            list_items = block.split("\n")
            for item in list_items:
                ul_node.children.append(LeafNode("li", item.strip("* ").strip()))
            block_node = ul_node
        
        elif block_type == "ordered_list":
            # Ordered list inside <ol>
            ol_node = ParentNode("ol", [])
            list_items = block.split("\n")
            for item in list_items:
                # Correctly handle the ordered list item by removing the leading number (1.)
                item_text = item.strip().lstrip("1234567890.")  # Strip the number and dot
                ol_node.children.append(LeafNode("li", item_text.strip()))
            block_node = ol_node
        
        elif block_type == "paragraph":
            # Paragraph inside <p>
            block_node = ParentNode("p", text_to_children(block.strip()))
        
        # Add the block_node to the parent_node
        parent_node.children.append(block_node)
    
    return parent_node


def markdown_to_blocks(markdown):
    """
    Splits raw markdown into a list of block strings based on blank lines.
    Strips leading/trailing whitespace from each block and removes empty blocks.
    """
    # Split the markdown by blank lines (two or more newlines)
    blocks = markdown.strip().split("\n\n")
    # Strip leading/trailing whitespace from each block and filter out empty blocks
    return [block.strip() for block in blocks if block.strip()]


def block_to_block_type(block):
    # Check for heading (starts with 1-6 '#' characters followed by a space)
    if re.match(r'^#{1,6} ', block):
        return "heading"
    
    # Check for code block (starts and ends with 3 backticks)
    if block.startswith("```") and block.endswith("```"):
        return "code"
    
    # Check for quote block (each line starts with '>')
    if all(line.startswith(">") for line in block.splitlines()):
        return "quote"
    
    # Check for unordered list (each line starts with '*' or '-')
    if all(line.lstrip().startswith(("*", "-")) for line in block.splitlines()):
        return "unordered_list"
    
    # Check for ordered list (each line starts with a number followed by a dot)
    if all(re.match(r'^\d+\.', line.lstrip()) for line in block.splitlines()):
        return "ordered_list"
    
    # If none of the above, it's a paragraph
    return "paragraph"


def text_to_textnodes(text):
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "*", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    return nodes


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        split_nodes = []
        sections = old_node.text.split(delimiter)
        if len(sections) % 2 == 0:
            raise ValueError("Invalid markdown, formatted section not closed")
        for i in range(len(sections)):
            if sections[i] == "":
                continue
            if i % 2 == 0:
                split_nodes.append(TextNode(sections[i], TextType.TEXT))
            else:
                split_nodes.append(TextNode(sections[i], text_type))
        new_nodes.extend(split_nodes)
    return new_nodes


def split_nodes_image(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        original_text = old_node.text
        images = extract_markdown_images(original_text)
        if len(images) == 0:
            new_nodes.append(old_node)
            continue
        for image in images:
            sections = original_text.split(f"![{image[0]}]({image[1]})", 1)
            if len(sections) != 2:
                raise ValueError("Invalid markdown, image section not closed")
            if sections[0] != "":
                new_nodes.append(TextNode(sections[0], TextType.TEXT))
            new_nodes.append(
                TextNode(
                    image[0],
                    TextType.IMAGE,
                    image[1],
                )
            )
            original_text = sections[1]
        if original_text != "":
            new_nodes.append(TextNode(original_text, TextType.TEXT))
    return new_nodes


def split_nodes_link(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        original_text = old_node.text
        links = extract_markdown_links(original_text)
        if len(links) == 0:
            new_nodes.append(old_node)
            continue
        for link in links:
            sections = original_text.split(f"[{link[0]}]({link[1]})", 1)
            if len(sections) != 2:
                raise ValueError("Invalid markdown, link section not closed")
            if sections[0] != "":
                new_nodes.append(TextNode(sections[0], TextType.TEXT))
            new_nodes.append(TextNode(link[0], TextType.LINK, link[1]))
            original_text = sections[1]
        if original_text != "":
            new_nodes.append(TextNode(original_text, TextType.TEXT))
    return new_nodes


def extract_markdown_images(text):
    pattern = r"!\[([^\[\]]*)\]\(([^\(\)]*)\)"
    matches = re.findall(pattern, text)
    return matches


def extract_markdown_links(text):
    pattern = r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)"
    matches = re.findall(pattern, text)
    return matches
