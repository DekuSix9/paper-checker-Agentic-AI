from PIL import Image, ImageDraw, ImageFont
import os


def generate_architecture_diagram():
    width, height = 1200, 700
    img = Image.new("RGB", (width, height), color="#1A202C")
    draw = ImageDraw.Draw(img)

    # Colors
    box_blue = "#2B6CB0"
    box_gold = "#D69E2E"
    box_red = "#E53E3E"
    box_green = "#38A169"
    text_white = "#FFFFFF"
    arrow_color = "#CBD5E0"

    # Draw Title Header
    draw.rectangle([0, 0, width, 70], fill="#2D3748")
    draw.text((30, 20), "AI Conference Review Committee - LangGraph Multi-Agent Architecture Topology", fill=text_white)

    # Nodes Definitions
    nodes = {
        "START": (30, 350, 130, 410, box_blue),
        "Ingestor": (170, 340, 280, 420, box_blue),
        "Novelty": (350, 100, 510, 170, box_blue),
        "Methodology": (350, 220, 510, 290, box_blue),
        "Stats Rigor": (350, 340, 510, 410, box_blue),
        "Writing Quality": (350, 460, 510, 530, box_blue),
        "AI Detector": (350, 580, 510, 650, box_blue),
        "Ethics": (600, 100, 750, 170, box_blue),
        "Area Chair": (820, 330, 970, 430, box_gold),
        "HITL Gate": (820, 480, 970, 540, box_red),
        "Finalize / END": (1020, 350, 1160, 410, box_green)
    }

    # Draw Boxes & Labels
    for name, (x1, y1, x2, y2, color) in nodes.items():
        draw.rectangle([x1, y1, x2, y2], fill=color, outline="#FFFFFF", width=2)
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        draw.text((x1 + 10, cy - 8), name, fill=text_white)

    # Draw Connections (Arrows)
    lines = [
        ("START", "Ingestor"),
        ("Ingestor", "Novelty"),
        ("Ingestor", "Methodology"),
        ("Ingestor", "Stats Rigor"),
        ("Ingestor", "Writing Quality"),
        ("Ingestor", "AI Detector"),
        ("Novelty", "Ethics"),
        ("Methodology", "Area Chair"),
        ("Stats Rigor", "Area Chair"),
        ("Writing Quality", "Area Chair"),
        ("AI Detector", "Area Chair"),
        ("Ethics", "Area Chair"),
        ("Area Chair", "HITL Gate"),
        ("HITL Gate", "Finalize / END")
    ]

    for start_node, end_node in lines:
        s = nodes[start_node]
        e = nodes[end_node]
        sx, sy = (s[2], (s[1] + s[3]) // 2)
        ex, ey = (e[0], (e[1] + e[3]) // 2)
        draw.line([(sx, sy), (ex, ey)], fill=arrow_color, width=3)

    out_path = os.path.join(os.path.dirname(__file__), "architecture_diagram.png")
    img.save(out_path)
    print(f"Architecture diagram generated at: {out_path}")


if __name__ == "__main__":
    generate_architecture_diagram()
