from textnode import TextNode, TextType
from htmlnode import HTMLNode, LeafNode, ParentNode

def main():
    node=TextNode("This is a text node", TextType.BOLD, "https://www.boot.dev")
    print(node)
    print(node.text_node_to_html_node())

    print(node.text_node_to_html_node().to_html())


if __name__ == "__main__":
    main()
