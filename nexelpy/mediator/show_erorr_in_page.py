from nexelpy.view import pageBuilder


async def show_errrr(errrr):
    x = pageBuilder.PageBilder()
    x.STYLE_tag.text = """
body {
    background-color: rgb(20, 20, 20);
    color: white;
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 20px;
}

h2 {
    background-color: red;
    color: white;
    padding: 1.5rem;
    margin: 1rem 2rem;
    border-radius: 8px;
    font-weight: bold;
    text-align: center;
    letter-spacing: 2px;
}

ul {
    list-style: none;
    padding: 0;
    margin: 2rem;
}

li {
    margin: 1rem 2rem;
    padding: 12px 20px;
    background-color: rgba(255, 255, 255, 0.05);
    border-left: 4px solid #ff4444;
    border-radius: 4px;
    font-size: 16px;
    font-family: 'Courier New', monospace;
    transition: all 0.3s ease;
}

li:hover {
    background-color: rgba(255, 255, 255, 0.1);
    transform: translateX(5px);
}

li:first-child {
    border-left-color: #ffaa00;
    color: #ffaa00;
}

li:nth-child(2) {
    border-left-color: #ff0000;
    color: #ff6b6b;
}

li:last-child {
    border-left-color: #00ccff;
    color: #66e0ff;
    background-color: rgba(0, 204, 255, 0.08);
}

li:last-child code {
    background-color: rgba(0, 0, 0, 0.3);
    padding: 2px 8px;
    border-radius: 3px;
    color: #ffd700;
}

li::before {
    content: "▸";
    margin-right: 10px;
    color: #ff4444;
}

li:first-child::before {
    color: #ffaa00;
}

li:nth-child(2)::before {
    color: #ff0000;
}

li:last-child::before {
    color: #00ccff;
}


li:nth-child(3) {
    border-left-color: #039408;
    color: #039408;
}

li:nth-child(3)::before {
    color: #039408;
}

li:nth-child(4) {
    border-left-color: #ff66ff;
    color: #ff66ff;
}

li:nth-child(4)::before {
    color: #ff66ff;
}
"""
    x.h2("nexelpy erorr")
    with x.ul():
        for i in errrr:
            x.li(f"{i} : {errrr[i]}")
    return x.RESPONSE()